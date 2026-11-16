'use strict';
const {EventEmitter}=require('node:events');
const {Supervisor}=require('./supervisor.cjs');
const P=require('./protocol.cjs');
const FAULTS=['none','drop-data-ack','drop-end-ack','corrupt-data','drop-all-A','bridge-exit','capture-gap','epoch-change'];
// Fake native bridge, including READY and body/guard boundaries. Only physical
// events cross between nodes; neither endpoint reads the peer's protocol state.
async function simulateSupervised({a='Hola',b='Respuesta',crc='SMBUS',encoding='utf-8',journals,outputs,interactive,
  latePrepare=false,failOutput=false,limit=10000,fault='none'}={}){
  if(!FAULTS.includes(fault))throw Error('UNKNOWN_FAULT');
  let injected=false;const injections=[];
  let now=0,serial=0;const queue=[],records=[[],[]],sent=[false,false];
  const schedule=(t,fn)=>queue.push({t,fn,serial:serial++});
  const bridges=[new EventEmitter(),new EventEmitter()];
  const sequence=[0,0],ready=[new Set(),new Set()],stopped=[false,false];
  const nodes=bridges.map((bridge,dir)=>new Supervisor({node:dir?'B':'A',coordinator:dir===0,
    crc:dir?'SMBUS':crc,encoding,bridge,clock:()=>now,
    journal:journals?.[dir]||{write:e=>records[dir].push(e),close:()=>{}},
    outputs:outputs?.[dir]||{prepare:()=>{if(failOutput&&dir===0)throw Error('OUTPUT_IO');
      if(latePrepare&&dir===0)now+=0.016;},shutdown:async()=>{}},cleanup:async()=>{stopped[dir]=true;}}));
  function mark(dir,detail){
    const e={kind:'INJECTED_FAULT',fault,node:dir?'B':'A',t:now,detail};
    injections.push(e);(journals?.[dir]||{write:e=>records[dir].push(e)}).write(e);injected=true;
  }
  function emit(dir,t,vector,clock,flags){
    if(stopped[dir]||stopped[1-dir])return;
    let epoch=1;
    if(!injected&&dir===0&&sequence[dir]>4&&['capture-gap','epoch-change'].includes(fault)){
      mark(dir,'Receiver capture metadata altered');
      if(fault==='capture-gap')sequence[dir]++;else epoch=2;
    }
    const tick=BigInt(Math.round(t*2e8));
    bridges[1-dir].emit('record',{kind:'event',sequence:sequence[dir]++,epoch,
      ticks_lo:Number(tick&0xffffffffn),ticks_hi:Number(tick>>32n),
      r31:((vector&1)<<5)|(((vector>>1)&1)<<14)|(((vector>>2)&1)<<16)|(clock<<15),
      normalized:vector|(clock<<3),flags});
  }
  bridges.forEach((bridge,dir)=>{bridge.write=command=>{
    const [op,id,rows]=command.trim().split(' ');
    if(op==='STOP'){stopped[dir]=true;return;}
    if(op==='READY'){ready[dir].add(id+':'+rows);return;}
    if(op!=='TX')throw Error('fake command');
    const frame=nodes[dir].endpoint.sending.frame;
    let received=rows,drop=false;
    if(!injected&&fault==='bridge-exit'&&dir===0){mark(dir,'Native bridge process exit');bridge.emit('exit');return;}
    if(fault==='drop-all-A'&&dir===0){mark(dir,frame.type);drop=true;}
    if(!injected&&dir===1&&frame.type==='ACK'&&
      ((fault==='drop-data-ack'&&frame.data===P.TYPES.DATA)||(fault==='drop-end-ack'&&frame.data===P.TYPES.END))){
      mark(dir,'Lost '+(fault==='drop-data-ack'?'DATA':'END')+' ACK');drop=true;
    }
    if(!injected&&dir===0&&frame.type==='DATA'&&fault==='corrupt-data'){
      const bits=frame.bits.split('');bits[22]=bits[22]==='0'?'1':'0';
      received=P.rows(bits.join('')).map(row=>row.split('').reduce((v,b,j)=>v|(Number(b)<<j),0)).join('');
      mark(dir,'Changed DATA with original CRC; valid matrix encoding');
    }
    const start=now+0.020;
    [...rows].forEach((v,k)=>{
      schedule(start+k-0.020,()=>bridge.emit('record',{kind:'prepare',id:Number(id),index:k,vector:Number(v)}));
      schedule(start+k,()=>{
        if(!ready[dir].delete(id+':'+k)){bridge.emit('failure',Error('MISSING_READY'));return;}
        if(!drop)emit(dir,start+k,Number(received[k]),1,1);
      });
      schedule(start+k+(k?0.2:0.6),()=>{if(!drop)emit(dir,start+k+(k?0.2:0.6),Number(received[k]),0,1);});
      schedule(start+k+0.8,()=>{if(!drop)emit(dir,start+k+0.8,Number(received[k]),0,2);});
    });
    schedule(start+87,()=>bridge.emit('record',{kind:'body_done',id:Number(id)}));
    schedule(start+89,()=>bridge.emit('record',{kind:'done',id:Number(id)}));
  };});
  nodes.forEach(n=>n.start());
  if(interactive)interactive.ready(nodes);
  for(let step=0;step<100000&&now<=limit;step++){
    await new Promise(resolve=>setImmediate(resolve));
    if(nodes.some(n=>n.state!=='RUNNING')||interactive?.closed)break;
    if(interactive)interactive.tick(nodes);
    nodes.forEach((n,i)=>{
      if(!interactive&&!sent[i]&&n.endpoint.state==='CONNECTED'){
        n.send(i?b:a);sent[i]=true;
      }
      n.pump();
    });
    if(!interactive&&sent.every(Boolean)&&nodes.every(n=>!n.active&&!n.endpoint.pending&&!n.endpoint.queue.length&&!n.endpoint.specs.length))break;
    queue.sort((x,y)=>x.t-y.t||x.serial-y.serial);
    const wake=nodes.flatMap(n=>[n.endpoint.pending?.deadline,
      ...(!n.active?n.endpoint.queue.map(j=>j.notBefore):[])]).filter(t=>Number.isFinite(t)&&t>now);
    const next=Math.min(queue[0]?.t??Infinity,...wake);
    if(!Number.isFinite(next)){if(interactive){await interactive.wait();continue;}break;}
    now=Math.max(now,next);
    while(queue.length&&queue[0].t<=now){queue.shift().fn();await new Promise(resolve=>setImmediate(resolve));
      if(outputs)await Promise.all(nodes.map(n=>n.preparePromise));}
  }
  const status=(interactive||sent.every(Boolean))&&nodes.every(n=>n.state==='RUNNING'&&!n.endpoint.specs.length&&!n.endpoint.pending)?'PASS':'FAIL';
  const cleanup=await Promise.all(nodes.map(n=>n.stop('SIMULATION_END')));
  return {origin:'simulation',physical_status:'NOT_TESTED',status,seconds:now,
    deliveries:nodes.map(n=>n.endpoint.deliveries),stats:nodes.map(n=>n.endpoint.stats),injections,cleanup,records};
}
module.exports={simulateSupervised,FAULTS};
if(require.main===module){
  const fs=require('node:fs'),path=require('node:path');const {Journal}=require('./supervisor.cjs');
  const dir=process.argv[2];if(!dir)throw Error('Usage: node supervised-simulation.cjs NEW_DIRECTORY');
  fs.mkdirSync(dir,{recursive:false});
  const journals=['A','B'].map(node=>new Journal(path.join(dir,node+'.jsonl'),{node}));
  simulateSupervised({journals}).then(result=>{
    fs.writeFileSync(path.join(dir,'summary.json'),JSON.stringify(result,null,2),{flag:'wx'});
    console.log(JSON.stringify(result,null,2));process.exitCode=result.status==='PASS'?0:1;
  }).catch(async e=>{journals.forEach(j=>j.close());console.error(e);process.exitCode=1;});
}
