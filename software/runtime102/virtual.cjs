'use strict';
const {Endpoint}=require('./endpoint.cjs');
const {StreamDecoder}=require('./stream.cjs');
// Same endpoints/stream parser as replay. Only wires and time are virtual.
function simulate({a='Hola',b='',drop=()=>false,mask=0,limit=30000,crc='SMBUS',corruptDataOnce=false}={}){
  const log=[],nodes=[new Endpoint({id:'A',coordinator:true,crc,log:e=>log.push(e)}),new Endpoint({id:'B',crc,log:e=>log.push(e)})];
  const events=[],free=[0,0],sent=[false,false],sequence=[0,0];let now=0,serial=0,corrupted=false;
  const schedule=(t,fn)=>events.push({t,fn,id:serial++});
  const rx=nodes.map((node,i)=>new StreamDecoder({crc,onFrame:bits=>node.receive(bits,now),onFault:reason=>node.reject(reason,now)}));
  const emit=(dir,t,vector,clock,flags)=>{
    const ticks=BigInt(Math.round(t*2e8)),r31=((vector&1)<<5)|(((vector>>1)&1)<<14)|(((vector>>2)&1)<<16)|(clock<<15);
    rx[1-dir].ingest({sequence:sequence[dir]++>>>0,epoch:1,ticks_lo:Number(ticks&0xffffffffn),ticks_hi:Number(ticks>>32n),r31:r31>>>0,normalized:vector|(clock<<3),flags});
  };
  nodes[0].start();
  while(now<=limit){
    for(let dir=0;dir<2;dir++){
      const node=nodes[dir];node.poll(now);
      if(!sent[dir]&&node.state==='CONNECTED'){
        // Wait until the opening READY has left B before application starts.
        if(nodes.every(n=>n.state==='CONNECTED')){node.send(dir?b:a,now);sent[dir]=true;}
      }
      if(now<free[dir])continue;
      const job=node.take(now);if(!job)continue;
      const start=now,skip=drop({dir,frame:job.frame,attempt:node.pending?.attempts});
      if(corruptDataOnce&&!corrupted&&dir===0&&job.frame.type==='DATA'){
        // Valid matrix codeword for a changed DATA bit with original CRC:
        // isolates final CRC detection rather than matrix correction.
        const bits=job.frame.bits.split('');bits[22]=bits[22]==='0'?'1':'0';
        job.rows=require('./protocol.cjs').rows(bits.join(''));corrupted=true;
      }
      free[dir]=start+89;
      if(!skip)job.rows.forEach((row,k)=>{
        const vector=row.split('').reduce((v,x,j)=>v|((Number(x)&((mask>>j)&1?0:1))<<j),0);
        schedule(start+k,()=>emit(dir,start+k,vector,1,1));
        schedule(start+k+(k?0.2:0.6),()=>emit(dir,start+k+(k?0.2:0.6),vector,0,1));
        schedule(start+k+0.8,()=>emit(dir,start+k+0.8,vector,0,2));
      });
      schedule(start+87,()=>node.txDone(job.id,now));
      schedule(free[dir],()=>{});
    }
    if(sent.every(Boolean)&&nodes.every(n=>!n.specs.length&&!n.pending&&!n.queue.length&&!n.sending))break;
    if(nodes.some(n=>n.state==='FAULT'))break;
    const deadlines=nodes.map(n=>n.pending?.deadline).filter(x=>x!==null&&x!==undefined&&x>now);
    events.sort((a,b)=>a.t-b.t||a.id-b.id);
    const queued=nodes.flatMap((n,i)=>n.sending?[]:n.queue.map(j=>Math.max(free[i],j.notBefore))).filter(t=>t>now);
    const next=Math.min(events[0]?.t??Infinity,...deadlines,...queued);
    if(!Number.isFinite(next))break;
    now=next;nodes.forEach(n=>n.time(now));
    while(events.length&&events[0].t===now){events.shift().fn();events.sort((a,b)=>a.t-b.t||a.id-b.id);}
  }
  return {origin:'simulation',physical_status:'NOT_TESTED',seconds:now,
    status:sent.every(Boolean)&&nodes.every(n=>n.state==='CONNECTED'&&!n.specs.length&&!n.pending)?'PASS':'FAIL',
    deliveries:nodes.map(n=>n.deliveries),stats:nodes.map(n=>n.stats),log};
}
module.exports={simulate};
