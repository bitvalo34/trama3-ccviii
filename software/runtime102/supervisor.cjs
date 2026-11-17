'use strict';
const fs=require('node:fs');
const {Endpoint}=require('./endpoint.cjs');
const {StreamDecoder}=require('./stream.cjs');

// Exclusive file creation prevents overwriting previous evidence. A full disk or
// log limit is a session fault, never permission to continue without evidence.
class Journal {
  constructor(path,{node,origin='simulation',runId=null,onRecord=()=>{},maxBytes=16*1024*1024}={}){
    if(!['simulation','hardware'].includes(origin)||!['A','B'].includes(node))throw Error('journal configuration');
    this.fd=fs.openSync(path,'wx');this.node=node;this.origin=origin;
    this.bytes=0;this.sequence=0;this.maxBytes=maxBytes;
    this.runId=runId;this.onRecord=onRecord;
  }
  write(event){
    const record={run_id:this.runId,...event,node:this.node,origin:this.origin,
      utc_system_unverified:new Date().toISOString(),physical_status:'NOT_TESTED',record:this.sequence};
    const line=Buffer.from(JSON.stringify(record)+'\n');
    if(this.bytes+line.length>this.maxBytes)throw Error('JOURNAL_LIMIT');
    let offset=0;while(offset<line.length){const n=fs.writeSync(this.fd,line,offset,line.length-offset);if(!n)throw Error('JOURNAL_WRITE');offset+=n;}
    this.bytes+=line.length;this.sequence++;
    this.onRecord(record);
  }
  close(){if(this.fd!==null){const fd=this.fd;this.fd=null;try{fs.fsyncSync(fd);}finally{fs.closeSync(fd);}}}
}

// Bridge: EventEmitter(record, failure, exit), write(command). Outputs:
// prepare(vector) -> Promise, shutdown() -> Promise. Resource owner:
// cleanup() -> Promise. Hardware ownership and loading are deliberately injected.
class Supervisor {
  constructor({node,coordinator=false,sid=1,crc='SMBUS',encoding='utf-8',bridge,outputs,cleanup,clock,journal,availableMask=7,prepareTimeout=0.015}){
    Object.assign(this,{bridge,outputs,cleanup,clock,journal,prepareTimeout});
    this.state='NEW';this.active=null;this.preparing=false;this.stopPromise=null;
    this.endpoint=new Endpoint({id:node,coordinator,sid,crc,encoding,log:e=>journal.write(e)});
    this.lastClockSample=null;this.clockGap=false;
    this.decoder=new StreamDecoder({crc,availableMask,onBlock:block=>this.journal.write({kind:'MATRIX_BLOCK',
      direction:'rx',...block,t:this.clock()}),onFrame:bits=>{
      this.endpoint.receive(bits,this.clock());this.decoder.crc=this.endpoint.crc;
    },onFault:(reason,raw)=>{
      if(raw)this.endpoint.receive(raw,this.clock());
      else if(this.decoder.faulted)this.stop(reason);
      else this.endpoint.reject(reason,this.clock());
    }});
    bridge.on('record',r=>{try{this.record(r);}catch(e){this.stop(e.message,'bridge');}});
    bridge.on('failure',e=>this.stop(String(e.message||e),'bridge'));
    bridge.on('exit',()=>{if(this.state==='RUNNING')this.stop('BRIDGE_EXIT','bridge');});
    if(outputs.on)outputs.on('failure',e=>{if(this.state==='RUNNING')this.stop('P2: '+e.message,'p2');});
  }
  start(){
    if(this.state!=='NEW')throw Error('supervisor state');
    this.state='RUNNING';
    try{this.journal.write({kind:'SESSION_START',t:this.clock()});
      if(this.endpoint.coordinator)this.endpoint.start(this.clock());this.pump();
    }catch(e){this.stop(e.message);}
  }
  send(text){if(this.state!=='RUNNING')throw Error('not running');this.endpoint.send(text,this.clock());this.pump();}
  pump(){
    if(this.state!=='RUNNING')return;
    try{
      if(this.preparing&&this.clock()>this.prepareDeadline){this.stop('OUTPUT_PREPARE_TIMEOUT');return;}
      const rx=this.decoder.receiver;
      if(this.lastClockSample!==null&&!this.clockGap&&rx.rows.length>0&&!rx.result&&!rx.error&&
        this.clock()-this.lastClockSample>1.1*this.decoder.period){
        this.clockGap=true;
        this.journal.write({kind:'CLOCK_GAP',direction:'rx',after_tick:rx.rows.length,t:this.clock()});
      }
      this.endpoint.poll(this.clock());
      if(this.endpoint.state==='FAULT'){this.stop('PROTOCOL_FAULT');return;}
      if(this.active)return;
      const job=this.endpoint.take(this.clock());if(!job)return;
      const vectors=job.rows.map(row=>row.split('').reduce((v,b,j)=>v|(Number(b)<<j),0));
      this.active={id:job.id,vectors,index:0,bodyEnd:null};
      this.bridge.write('TX '+job.id+' '+vectors.join('')+'\n');
    }catch(e){this.stop(e.message);}
  }
  record(r){
    if(this.state!=='RUNNING')return;
    if(r.kind==='event'){
      const t=this.clock();
      if(r.flags===2){this.lastClockSample=t;this.clockGap=false;}
      this.journal.write({...r,kind:'CAPTURE',direction:'rx',t});this.decoder.ingest(r);return;
    }
    const a=this.active;
    if(!a||r.id!==a.id)throw Error('BRIDGE_TX_ID');
    if(r.kind==='prepare'){
      if(this.preparing||r.index!==a.index||r.vector!==a.vectors[r.index])throw Error('BRIDGE_PREPARE_ORDER');
      this.preparing=true;const began=this.clock();this.prepareDeadline=began+this.prepareTimeout;
      // READY must follow completion of the output operation, not its dispatch.
      this.preparePromise=Promise.resolve().then(()=>{if(this.state==='RUNNING')return this.outputs.prepare(r.vector);}).then(async readback=>{
        if(this.state!=='RUNNING'){
          // An I/O operation may finish after STOP. Reassert inactive outputs.
          await this.outputs.shutdown();return;
        }
        if(this.clock()-began>this.prepareTimeout)throw Error('OUTPUT_PREPARE_LATE');
        this.journal.write({kind:'OUTPUT_PREPARED',id:r.id,index:r.index,vector:r.vector,readback,t:this.clock()});
        this.bridge.write('READY '+r.id+' '+r.index+'\n');a.index++;this.preparing=false;
      }).catch(e=>{
        this.preparing=false;
        if(this.state==='RUNNING')this.stop(e.message,'p2');
        else {this.errors=this.errors||[];this.errors.push('late output: '+e.message);this.state='CLEANUP_FAILED';}
      });
    }else if(r.kind==='body_done'){
      if(a.index!==a.vectors.length||a.bodyEnd!==null)throw Error('BRIDGE_BODY_ORDER');
      a.bodyEnd=this.clock();
    }else if(r.kind==='done'){
      if(a.index!==a.vectors.length||a.bodyEnd===null)throw Error('BRIDGE_DONE_ORDER');
      this.endpoint.txDone(a.id,this.clock(),a.bodyEnd);this.active=null;this.pump();
    }else throw Error('BRIDGE_RECORD');
  }
  stop(reason='OPERATOR_STOP',source){
    if(this.stopPromise)return this.stopPromise;
    this.state='STOPPING';
    this.stopPromise=Promise.resolve().then(async()=>{
      const errors=[];this.errors=errors;
      if(this.preparing)errors.push('Output preparation in flight: physical shutdown not confirmed');
      try{this.journal.write({kind:'SESSION_STOP',reason,source,t:this.clock()});}catch(e){errors.push('log: '+e.message);}
      try{if(!this.bridge.closed)this.bridge.write('STOP\n');}catch(e){errors.push('bridge: '+e.message);}
      try{await this.outputs.shutdown();}catch(e){errors.push('outputs: '+e.message);}
      try{await this.cleanup();}catch(e){errors.push('cleanup: '+e.message);}
      try{this.journal.write({kind:'CLEANUP',errors,t:this.clock()});}catch(e){errors.push('log: '+e.message);}
      try{this.journal.close();}catch(e){errors.push('close: '+e.message);}
      this.state=errors.length?'CLEANUP_FAILED':'STOPPED';this.errors=errors;
      return {state:this.state,reason,errors};
    });return this.stopPromise;
  }
}
module.exports={Journal,Supervisor};
