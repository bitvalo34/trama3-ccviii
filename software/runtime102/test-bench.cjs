'use strict';
const assert=require('node:assert/strict');
const {EventEmitter}=require('node:events');
const {Bench}=require('./bench.cjs');
function fixture(role){
 let t=0,off=0,clean=0;
 const bridge=new EventEmitter(),commands=[],records=[];
 bridge.write=s=>commands.push(s);
 const bench=new Bench({node:role==='tx'?'A':'B',bridge,clock:()=>t,
   outputs:{prepare:async()=>{},shutdown:async()=>{off++;}},
   cleanup:async()=>{clean++;},journal:{write:r=>records.push(r),close(){}}},
   {role,pattern:'vectors',runId:'test'});
 return {bench,commands,records,time:n=>{t=n;},counts:()=>[off,clean]};
}
async function run(){
 const tx=fixture('tx');tx.bench.start();
 assert.match(tx.commands[0],/^TX 1 [0-7]{87}\n$/);
 for(let i=0;i<87;i++){
   tx.time(i);tx.bench.record({kind:'prepare',id:1,index:i,vector:tx.bench.plan.vectors[i]});
   await tx.bench.preparePromise;
   assert.equal(tx.commands[i+1],'READY 1 '+i+'\n');
 }
 tx.bench.record({kind:'body_done',id:1});
 tx.bench.record({kind:'done',id:1});
 assert.equal((await tx.bench.stopPromise).reason,'BENCH_COMPLETE');
 assert.deepEqual(tx.counts(),[1,1]);
 assert.equal(tx.records.filter(r=>r.kind==='BENCH_SENT').length,1);
 const rx=fixture('rx');rx.bench.start();
 assert.equal(rx.bench.plan,null);assert.deepEqual(rx.commands,[]);
 for(let i=0;i<87;i++)rx.bench.record({kind:'event',flags:2,normalized:0});
 assert.equal((await rx.bench.stopPromise).reason,'BENCH_COMPLETE');
 assert.equal(rx.records.filter(r=>r.kind==='CAPTURE').length,87);
 const timeout=fixture('rx');timeout.bench.start();timeout.time(180);timeout.bench.pump();
 assert.equal((await timeout.bench.stopPromise).reason,'BENCH_TIMEOUT');
 const late=fixture('tx');late.bench.start();late.bench.preparing=true;late.bench.prepareDeadline=0.015;
 late.time(0.02);late.bench.pump();
 assert.equal((await late.bench.stopPromise).reason,'OUTPUT_PREPARE_TIMEOUT');
 assert.throws(()=>rx.bench.send('test'),/BENCH_NOT_CHAT/);
 console.log('PASS bench lifecycle with fake IO; not physical');
}
run().catch(e=>{console.error(e);process.exitCode=1;});
