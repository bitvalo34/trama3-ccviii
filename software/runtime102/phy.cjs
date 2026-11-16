'use strict';
const P=require('./protocol.cjs');
const {Supervisor}=require('./supervisor.cjs');
const {StreamDecoder}=require('./stream.cjs');
const B=require('./bench-core.cjs');
const vector=row=>row.split('').reduce((v,b,j)=>v|(Number(b)<<j),0);
function makePlan({kind,pair='00',data=65,seq=0,sid=1,crc='SMBUS'}){
  if(kind==='frame'){
    if(!Number.isInteger(sid)||sid<1||sid>255)throw Error('SID');
    const frame=P.frame('DATA',data,seq,sid,crc);
    return {kind,frame,vectors:P.rows(frame.bits).map(vector),ticks:87};
  }
  let vectors;
  if(['c0','c1','clock','i2c'].includes(kind))vectors=Array.from({length:kind==='i2c'?20:6},(_,i)=>kind==='clock'?0:(i%2)<<(kind==='c1'?1:0));
  else if(kind==='pair'){
    const pairs=pair==='all'?['00','01','10','11']:[pair];
    if(!pairs.every(x=>/^[01]{2}$/.test(x)))throw Error('PAIR');
    vectors=pairs.flatMap(bits=>{const w=P.matrix.encode([...bits].map(Number));return [0,1,2].map(i=>w[3*i]|w[3*i+1]<<1|w[3*i+2]<<2);});
  }else throw Error('KIND');
  return {kind,vectors,ticks:vectors.length,scope:'low-level diagnostic; not a revision102 frame'};
}
function inspect(events,count,node='A'){
  return B.capture(B.plan('clock','independent-rx',node==='A'?'B':'A'),events,{count,compare:false,availableMask:3});
}
class PhysicalTrial extends Supervisor {
  constructor(options,{role,kind,runId,plan=null,ticks=87,timeout=150,ack=false,crc='SMBUS'}){
    super({...options,coordinator:false});
    if(!['tx','rx'].includes(role)||!['c0','c1','clock','pair','frame','i2c'].includes(kind)||
      !/^[-a-zA-Z0-9_]{1,64}$/.test(runId)||!Number.isInteger(ticks)||ticks<1||ticks>87||
      !Number.isInteger(timeout)||timeout<ticks+5||timeout>600||ack&&kind!=='frame')throw Error('PHY_CONFIGURATION');
    if(role==='tx'&&(!plan||plan.ticks!==ticks||plan.kind!==kind))throw Error('PHY_TX_PLAN');
    Object.assign(this,{role,kind,runId,plan:role==='tx'?plan:null,ticks,timeout,ack,events:[],samples:0,sent:false,replyAt:null,reply:null});
    this.decoder=new StreamDecoder({availableMask:3,crc,onBlock:block=>this.journal.write({kind:'PHY_BLOCK',...block,t:this.clock()}),onFrame:bits=>this.frame(bits,crc),onFault:reason=>{
      const r=this.decoder.receiver;
      this.journal.write({kind:'RX_REJECT',reason,blocks:r.blocks,raw_prefix:r.raw,pilots:r.meta,t:this.clock()});void this.stop(reason);
    }});
  }
  start(){
    this.state='RUNNING';this.deadline=this.clock()+this.timeout;
    this.journal.write({kind:'PHY_START',role:this.role,trial:this.kind,run_id:this.runId,ticks:this.ticks,
      available_mask:3,c2:'deliberately disconnected; not measured',ack:this.ack,plan:this.plan,t:this.clock()});
    if(this.role==='tx')this.transmit(this.plan.vectors,1);
  }
  transmit(vectors,id){
    this.active={id,vectors,index:0,bodyEnd:null};
    this.journal.write({kind:'PHY_TX_BEGIN',id,ticks:vectors.length,t:this.clock()});
    this.bridge.write('TX '+id+' '+vectors.join('')+'\n');
  }
  send(){throw Error('PHY_NOT_CHAT');}
  pump(){
    if(this.state!=='RUNNING')return;
    if(this.preparing&&this.clock()>this.prepareDeadline){void this.stop('OUTPUT_PREPARE_TIMEOUT');return;}
    if(this.clock()>=this.deadline){void this.stop('PHY_TIMEOUT');return;}
    if(this.replyAt!==null&&this.clock()>=this.replyAt&&!this.active){
      this.replyAt=null;this.transmit(P.rows(this.reply.bits).map(vector),2);
    }
  }
  frame(bits,crc){
    const frame=P.parse(bits,crc),r=this.decoder.receiver;
    const timing=inspect(this.events,87);
    this.journal.write({kind:'PHY_RX_FRAME',frame,raw:bits,blocks:r.blocks,pilots:r.meta,timing,t:this.clock()});
    if(!frame.ok||!frame.sid||timing.status!=='PASS'||this.role==='rx'&&frame.type!=='DATA'){void this.stop('PHY_RX_INVALID');return;}
    if(this.role==='tx'){
      const f=this.plan.frame;
      if(!this.ack||!this.sent||frame.type!=='ACK'||frame.sid!==f.sid||frame.seq!==f.seq||frame.data!==f.ctrl){void this.stop('PHY_ACK_CONTEXT');return;}
      this.journal.write({kind:'PHY_ACK_RECEIVED',seq:frame.seq,sid:frame.sid,t:this.clock()});void this.stop('PHY_COMPLETE');
    }else if(this.ack){
      if(frame.type!=='DATA'){void this.stop('PHY_ACK_CONTEXT');return;}
      // A laboratory response to this CRC-validated frame; no fake CONNECTED state.
      this.reply=P.frame('ACK',frame.ctrl,frame.seq,frame.sid,crc);
      this.replyAt=this.clock()+2.2;
      this.journal.write({kind:'PHY_ACK_QUEUED',frame:this.reply,t:this.clock()});
    }else void this.stop('PHY_COMPLETE');
  }
  record(r){
    if(this.state!=='RUNNING')return;
    if(r.kind==='event'){
      if(this.events.length>=1024)throw Error('PHY_CAPTURE_LIMIT');
      this.events.push(r);this.journal.write({...r,kind:'CAPTURE',t:this.clock()});
      if(this.kind==='frame'){this.decoder.ingest(r);return;}
      if(this.role==='rx'&&r.flags===2&&++this.samples===this.ticks){
        const timing=inspect(this.events,this.ticks);
        this.journal.write({kind:'PHY_RX_DIAGNOSTIC',timing,t:this.clock()});
        if(this.kind==='pair'){
          const samples=this.events.filter(e=>e.flags===2);
          for(let i=0;i<samples.length;i+=3){
            const y=samples.slice(i,i+3).flatMap(e=>[e.normalized&1,(e.normalized>>1)&1,null]);
            const block=P.matrix.decode(y,{diagnostics:true});this.journal.write({kind:'PHY_BLOCK',index:i/3,received:y,...block});
            if(!block.ok){void this.stop('MATRIX_'+block.reason);return;}
          }
        }
        void this.stop(timing.status==='PASS'?'PHY_COMPLETE':'PHY_CLOCK_INVALID');
      }
      return;
    }
    if(r.kind==='done'){
      const a=this.active;
      if(!a||a.id!==r.id||a.index!==a.vectors.length||a.bodyEnd===null)throw Error('PHY_DONE_ORDER');
      this.journal.write({kind:'PHY_TX_DONE',id:a.id,ticks:a.index,t:this.clock()});this.active=null;this.sent=true;
      if(this.role==='rx'||!this.ack)void this.stop('PHY_COMPLETE');
      else this.outputs.prepare(0).catch(e=>this.stop(e.message));
      return;
    }
    super.record(r);
  }
}
module.exports={makePlan,inspect,PhysicalTrial};
