'use strict';
const fs=require('node:fs'),path=require('node:path');
const {Journal}=require('./supervisor.cjs');
const {simulateSupervised,FAULTS}=require('./supervised-simulation.cjs');
const P=require('./protocol.cjs');
class ChatSession {
  constructor({directory,crc='SMBUS',encoding='utf-8',outputs,fault='none'}={}){
    if(!P.CRCS[crc]||!['utf-8','windows-1252'].includes(encoding))throw Error('SESSION_CONFIG');
    if(!FAULTS.includes(fault))throw Error('UNKNOWN_FAULT');this.fault=fault;this.diagnostics=[[],[]];
    fs.mkdirSync(directory,{recursive:false});this.directory=directory;this.crc=crc;this.encoding=encoding;
    this.messages=[[],[]];this.current=[null,null];this.next=1;this.closed=false;this.wake=null;
    this.profiles=['A','B'].map(n=>require('./profiles.cjs').load(path.join(__dirname,'profiles/BBB-'+n+'.json')));
    const journals=['A','B'].map((node,i)=>{
      const j=new Journal(path.join(directory,node+'.jsonl'),{node});
      j.write({kind:'PROFILE',profile:this.profiles[i]});
      return {write:e=>{j.write(e);this.event(i,e);},close:()=>j.close()};
    });
    this.driver={closed:false,ready:nodes=>{this.nodes=nodes;},tick:()=>this.tick(),wait:()=>new Promise(r=>{this.wake=r;})};
    this.result=simulateSupervised({crc,encoding,journals,outputs,fault,interactive:this.driver,limit:Infinity})
      .then(result=>{this.summary=result;return result;})
      .finally(()=>{this.closed=true;for(const row of this.messages)for(const m of row)if(['pending','sending'].includes(m.status))m.status='failed';});
  }
  event(i,e){
    if(['INJECTED_FAULT','RX_REJECT','NACK_CONTEXT','NACK_ACCEPTED','FAULT','SESSION_STOP','CLEANUP'].includes(e.kind)){
      this.diagnostics[i].push(e);if(this.diagnostics[i].length>100)this.diagnostics[i].shift();
    }
    if(e.kind==='MESSAGE_CONFIRMED'&&this.current[i]){this.current[i].status='confirmed';this.current[i]=null;}
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
    if(typeof text!=='string'||P.encode(text,this.encoding).length>1024)throw Error('MESSAGE_SIZE_OR_ENCODING');
    if(this.messages[i].filter(m=>['pending','sending'].includes(m.status)).length>=8)throw Error('QUEUE_FULL');
    if(this.messages[i].length>=256)throw Error('SESSION_MESSAGE_LIMIT');
    const message={id:this.next++,direction:'sent',text,status:'pending'};this.messages[i].push(message);
    if(this.wake){this.wake();this.wake=null;}return message.id;
  }
  index(node){if(!['A','B'].includes(node))throw Error('NODE');return node==='A'?0:1;}
  snapshot(node){const i=this.index(node);return {node,origin:'simulation',physical_status:'NOT_TESTED',
    state:this.closed?'STOPPED':this.nodes[i].endpoint.state,crc:this.crc,encoding:this.encoding,board:this.profiles[i].board,
    fault:this.fault,stats:this.nodes[i].endpoint.stats,diagnostics:this.diagnostics[i],messages:this.messages[i]};}
  log(node){this.index(node);return fs.readFileSync(path.join(this.directory,node+'.jsonl'));}
  async stop(){this.driver.closed=true;if(this.wake){this.wake();this.wake=null;}return this.result;}
}
module.exports={ChatSession};
