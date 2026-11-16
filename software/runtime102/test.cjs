'use strict';
const assert=require('node:assert/strict');
const {simulate}=require('./virtual.cjs');
const {Endpoint}=require('./endpoint.cjs');
const {StreamDecoder,decodeEvent}=require('./stream.cjs');
const P=require('./protocol.cjs');
let checks=0;
function test(name,fn){try{fn();checks++;console.log('PASS '+name);}catch(e){console.error('FAIL '+name);throw e;}}
test('two independent nodes, simultaneous messages',()=>{
 const r=simulate({a:'Hola',b:'A'});assert.equal(r.status,'PASS');assert.deepEqual(r.deliveries,[['A'],['Hola']]);
});
for(const crc of Object.keys(P.CRCS))test('negotiated CRC '+crc,()=>{const r=simulate({a:'ñ',b:'ok',crc});assert.equal(r.status,'PASS');assert.deepEqual(r.deliveries,[['ok'],['ñ']]);});
test('lost DATA ACK: same sequence, no duplicate delivery',()=>{
 let used=false;const r=simulate({a:'x',drop:({dir,frame})=>{if(dir===1&&!used&&frame.type==='ACK'&&frame.data===4){used=true;return true;}return false;}});
 assert.equal(r.status,'PASS');assert.deepEqual(r.deliveries[1],['x']);assert.equal(r.stats[0].retries,1);assert.equal(r.stats[1].duplicates,1);
});
test('lost END ACK does not redeliver message',()=>{
 let used=false;const r=simulate({a:'x',drop:({dir,frame})=>{if(dir===1&&!used&&frame.type==='ACK'&&frame.data===5){used=true;return true;}return false;}});
 assert.equal(r.status,'PASS');assert.deepEqual(r.deliveries[1],['x']);assert.equal(r.stats[0].retries,1);
});
test('four attempts, no infinite retries',()=>{
 const r=simulate({a:'x',drop:({frame})=>frame.type==='DATA'});assert.equal(r.status,'FAIL');assert.equal(r.stats[0].retries,3);assert.deepEqual(r.deliveries[1],[]);
});
for(const mask of [1,2,3,4,5,6])test('pilot exclusion mask '+mask,()=>{const r=simulate({a:'Z',mask});assert.equal(r.status,'PASS');assert.deepEqual(r.deliveries[1],['Z']);});
test('all channels absent cannot deliver',()=>{const r=simulate({mask:7});assert.equal(r.status,'FAIL');assert.deepEqual(r.deliveries,[[],[]]);});
test('wrong SID/sequence ACK cannot advance',()=>{
 const n=new Endpoint({id:'A',coordinator:true});n.state='CONNECTED';n.send('x');const p=n.pending;
 n.receive(P.frame('ACK',1,0,2).bits,0);assert.equal(n.pending,p);
 n.receive(P.frame('ACK',1,1,1).bits,0);assert.equal(n.pending,p);
});
test('sequence wraps without losing bytes',()=>{
 const text='x'.repeat(260);const r=simulate({a:text,limit:100000});assert.equal(r.status,'PASS');assert.deepEqual(r.deliveries[1],[text]);
});
test('peer restart never silently resumes old message',()=>{
 const n=new Endpoint({id:'B'});n.receive(P.frame('HELLO',6,0,1).bits,0);n.receive(P.frame('COMMIT',6,0,1).bits,1);
 n.receive(P.frame('HELLO',6,0,2).bits,2);assert.equal(n.state,'FAULT');
});
test('uncharacterized rate rejected',()=>{
 const n=new Endpoint({id:'B'});n.state='CONNECTED';n.receive(P.frame('RATE_CTRL',P.RATE.QUIESCE,1,1).bits,0);
 assert.equal(n.queue[0].frame.data,P.RATE.REJECT);assert.equal(n.txPeriod,1);
});
test('binary event and uint32 validation',()=>{
 const b=Buffer.alloc(28);b.writeUInt32LE(0xffffffff);assert.equal(decodeEvent(b).sequence,0xffffffff);
 assert.throws(()=>decodeEvent(Buffer.alloc(27)));
});
test('sequence gaps/epoch changes stop stream',()=>{
 for(const change of [{sequence:2},{epoch:2}]){
 const faults=[];const rx=new StreamDecoder({onFault:r=>faults.push(r)});
 const e={sequence:0,epoch:1,ticks_lo:0,ticks_hi:0,r31:0,normalized:8,flags:1};
 rx.ingest(e);rx.ingest({...e,sequence:1,...change});assert.equal(faults.length,1);assert.equal(rx.faulted,true);
 }
});
test('late sample is rejected',()=>{
 const faults=[];const rx=new StreamDecoder({onFault:r=>faults.push(r)});
 const e={sequence:0,epoch:1,ticks_lo:0,ticks_hi:0,r31:0,normalized:8,flags:1};
 rx.ingest(e);rx.ingest({...e,sequence:1,ticks_lo:120000000,normalized:0});rx.ingest({...e,sequence:2,ticks_lo:180000000,normalized:0,flags:2});assert.deepEqual(faults,['SAMPLE_DEADLINE']);
});
test('CRC -> contextual NACK -> retransmission',()=>{
 const r=simulate({a:'Hola',corruptDataOnce:true});assert.equal(r.status,'PASS');
 assert.deepEqual(r.deliveries[1],['Hola']);
 assert.ok(r.log.some(e=>e.kind==='RX_REJECT'&&e.reason==='CRC'));
 assert.ok(r.log.some(e=>e.kind==='NACK_CONTEXT'));
 assert.ok(r.log.some(e=>e.kind==='NACK_ACCEPTED'));assert.equal(r.stats[0].retries,1);
});
test('clock failure and no message context do not invent NACK',()=>{
 const n=new Endpoint({id:'B'});n.state='CONNECTED';n.reject('CRC');assert.equal(n.queue.length,0);
 n.rx.phase='body';n.reject('CLOCK_PERIOD');assert.equal(n.queue.length,0);
});
console.log(JSON.stringify({checks,status:'PASS',physical_status:'NOT_TESTED'}));

