'use strict';
const fs=require('node:fs'),path=require('node:path');
const {Journal}=require('./supervisor.cjs');
const {simulateSupervised,FAULTS}=require('./supervised-simulation.cjs');
const P=require('./protocol.cjs');
const activeStatuses=['pending','sending','waiting_ack'];
const diagnosticKinds=['INJECTED_FAULT','RX_REJECT','NACK_CONTEXT','NACK_ACCEPTED','FAULT','CLOCK_GAP','SESSION_STOP','CLEANUP'];
function updateMessage(message,event){
  if(!message)return;
  if(event.kind==='TX_START'&&event.attempt)message.status='sending';
  if(event.kind==='TX_DONE'&&event.attempt)message.status='waiting_ack';
  if(event.kind==='ATTEMPT'&&event.attempt>1)message.status='pending';
  if(event.kind==='MESSAGE_CONFIRMED')message.status='confirmed';
  if(event.kind==='SESSION_STOP'){
    message.status='uncertain';
    message.error=event.reason;
  }
}

class NodeChat {
  constructor(directory){
    this.directory=directory;this.next=1;this.messages=[];this.diagnostics=[];this.current=null;
  }
  attach(session){this.session=session;}
  event(event){
    if(diagnosticKinds.includes(event.kind)){
      this.diagnostics.push(event);
      if(this.diagnostics.length>100)this.diagnostics.shift();
    }
    updateMessage(this.current,event);
    if(this.current&&!activeStatuses.includes(this.current.status))this.current=null;
    if(event.kind==='DELIVERY')this.remember({id:this.next++,direction:'received',text:event.text,status:'received'});
  }
  remember(message){
    this.messages.push(message);
    if(this.messages.length>256)this.messages.splice(this.messages.findIndex(item=>item!==this.current),1);
  }
  index(node){
    const local=this.session.supervisor.endpoint.id;
    if(node&&node!==local)throw Error('NODE');
    return local;
  }
  send(node,text){
    this.index(node);
    const {supervisor}=this.session;
    if(this.current||supervisor.state!=='RUNNING'||supervisor.endpoint.state!=='CONNECTED')throw Error('NOT_READY');
    if(typeof text!=='string'||!text.length)throw Error('EMPTY_MESSAGE');
    const message={id:this.next++,direction:'sent',text,status:'pending'};
    this.current=message;
    try{supervisor.send(text);}
    catch(error){
      this.current=null;message.status='failed';message.error=error.message;
      this.remember(message);throw error;
    }
    this.remember(message);
    return message.id;
  }
  snapshot(node){
    const local=this.index(node);
    const {profile,supervisor}=this.session;
    const {endpoint,decoder}=supervisor;
    return {node:local,origin:this.session.mode==='hardware'?'hardware':'simulation',physical_status:'NOT_TESTED',
      board:profile.board,hardware_revision:profile.hardware_revision,available_mask:profile.available_mask??7,
      frequency_hz:1/profile.period_s,clock:decoder.faulted||supervisor.clockGap?'error':
        supervisor.lastClockSample===null?'sin muestras':'muestras observadas',
      state:supervisor.state==='RUNNING'?endpoint.state:supervisor.state,
      crc:endpoint.crc,encoding:endpoint.encoding,stats:endpoint.stats,diagnostics:this.diagnostics,
      can_send:supervisor.state==='RUNNING'&&endpoint.state==='CONNECTED'&&!this.current,
      messages:this.messages};
  }
  log(node){return fs.readFileSync(path.join(this.directory,this.index(node)+'.jsonl'));}
  stop(){return this.session.stop();}
}
class ChatSession {
  constructor({directory,crc='SMBUS',encoding='utf-8',outputs,fault='none',runId=null}={}){
    if(!P.CRCS[crc]||!['utf-8','windows-1252'].includes(encoding))throw Error('SESSION_CONFIG');
    if(!FAULTS.includes(fault))throw Error('UNKNOWN_FAULT');this.fault=fault;this.diagnostics=[[],[]];
    fs.mkdirSync(directory,{recursive:false});this.directory=directory;this.crc=crc;this.encoding=encoding;
    this.messages=[[],[]];this.current=[null,null];this.next=1;this.closed=false;this.wake=null;
    this.profiles=['A','B'].map(n=>require('./profiles.cjs').load(path.join(__dirname,'profiles/BBB-'+n+'.json')));
    const journals=['A','B'].map((node,i)=>{
      const j=new Journal(path.join(directory,node+'.jsonl'),{node,runId});
      j.write({kind:'PROFILE',profile:this.profiles[i],protocol_revision:102,protocol_version:P.VERSION,
        crc,encoding,frequency_hz:1,available_mask:7});
      return {write:e=>{j.write(e);this.event(i,e);},close:()=>j.close()};
    });
    this.driver={closed:false,ready:nodes=>{this.nodes=nodes;},tick:()=>this.tick(),wait:()=>new Promise(r=>{this.wake=r;})};
    this.result=simulateSupervised({crc,encoding,journals,outputs,fault,interactive:this.driver,limit:Infinity})
      .then(result=>{this.summary=result;return result;})
      .finally(()=>{this.closed=true;for(const row of this.messages)for(const m of row)
        if(activeStatuses.includes(m.status))m.status=m.status==='pending'?'failed':'uncertain';});
  }
  event(i,e){
    if(diagnosticKinds.includes(e.kind)){
      this.diagnostics[i].push(e);if(this.diagnostics[i].length>100)this.diagnostics[i].shift();
    }
    updateMessage(this.current[i],e);
    if(this.current[i]&&!activeStatuses.includes(this.current[i].status))this.current[i]=null;
    if(e.kind==='DELIVERY')this.messages[i].push({id:this.next++,direction:'received',text:e.text,status:'received'});
  }
  tick(){this.nodes.forEach((n,i)=>{
    if(this.current[i]||n.endpoint.state!=='CONNECTED'||n.endpoint.pending||n.endpoint.specs.length)return;
    const m=this.messages[i].find(m=>m.direction==='sent'&&m.status==='pending');
    if(m){this.current[i]=m;m.status='sending';try{n.send(m.text);}catch(e){m.status='failed';m.error=e.message;this.current[i]=null;}}
  });}
  send(node,text){
    const i=this.index(node);
    if(this.closed||this.driver.closed)throw Error('SESSION_CLOSED');
    if(typeof text!=='string'||!text.length||P.encode(text,this.encoding).length>1024)throw Error('MESSAGE_SIZE_OR_ENCODING');
    if(this.messages[i].filter(m=>activeStatuses.includes(m.status)).length>=8)throw Error('QUEUE_FULL');
    if(this.messages[i].length>=256)throw Error('SESSION_MESSAGE_LIMIT');
    const message={id:this.next++,direction:'sent',text,status:'pending'};this.messages[i].push(message);
    if(this.wake){this.wake();this.wake=null;}return message.id;
  }
  index(node='A'){if(!['A','B'].includes(node))throw Error('NODE');return node==='A'?0:1;}
  snapshot(node='A'){const i=this.index(node);return {node,origin:'simulation',physical_status:'NOT_TESTED',
    state:this.closed?'STOPPED':this.nodes[i].endpoint.state,crc:this.crc,encoding:this.encoding,board:this.profiles[i].board,
    available_mask:7,frequency_hz:1,clock:'virtual',can_send:!this.closed&&!this.driver.closed,
    fault:this.fault,stats:this.nodes[i].endpoint.stats,diagnostics:this.diagnostics[i],messages:this.messages[i]};}
  log(node='A'){this.index(node);return fs.readFileSync(path.join(this.directory,node+'.jsonl'));}
  async stop(){this.driver.closed=true;if(this.wake){this.wake();this.wake=null;}return this.result;}
}
module.exports={ChatSession,NodeChat};
