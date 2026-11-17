'use strict';
const assert=require('node:assert/strict'),{EventEmitter}=require('node:events');
const P=require('./protocol.cjs'),{StreamDecoder}=require('./stream.cjs');
const {makePlan,inspect,PhysicalTrial}=require('./phy.cjs');
const {evaluate}=require('./phy-evaluate.cjs');
const {validate,validateLab}=require('./profiles.cjs');
function events(vectors,{invert=8,c2=true}={}){
  let sequence=0;const out=[];
  vectors.forEach((v,i)=>{
    // Unknown C2 deliberately mimics perfect pilots; still must be excluded.
    v=(v&3)|(c2?(i%2)<<2:0);
    for(const [offset,flags,clock] of [[0,1,8],[i?40000000:120000000,1,0],[160000000,2,0]]){
      const t=BigInt(i)*200000000n+BigInt(offset),n=v|clock,physical=n^invert;
      const r31=((physical&1)<<5)|((physical>>1&1)<<14)|((physical>>2&1)<<16)|((physical>>3&1)<<15);
      out.push({kind:'event',sequence:sequence++,epoch:1,ticks_lo:Number(t&0xffffffffn),ticks_hi:Number(t>>32n),r31,normalized:n,flags,acoustic_active:v&2?60000000:0,acoustic_gap:1000});
    }
  });return out;
}
function fixture(role,plan,ack=false){
  let time=0;const records=[],commands=[],bridge=new EventEmitter();bridge.write=s=>commands.push(s);
  const s=new PhysicalTrial({node:role==='tx'?'A':'B',bridge,clock:()=>time,journal:{write:r=>records.push(r),close(){}},
    outputs:{prepare:async()=>({readback_verified:true}),shutdown:async()=>{}},cleanup:async()=>{}},
    {role,kind:plan.kind,runId:'test',plan:role==='tx'?plan:null,ticks:plan.ticks,timeout:260,ack});
  return {s,records,commands,time:t=>{time=t;}};
}
async function finishTx(f,id=1){
  const a=f.s.active;
  for(let i=0;i<a.vectors.length;i++){
    f.s.record({kind:'prepare',id,index:i,vector:a.vectors[i]});await f.s.preparePromise;
  }
  f.s.record({kind:'body_done',id});f.s.record({kind:'done',id});
}
async function run(){
  const mask=[0,1,3,4,6,7];
  for(const bits of ['00','01','10','11']){
    const w=P.matrix.encode([...bits].map(Number)),y=w.map((b,i)=>mask.includes(i)?b:null);
    const result=P.matrix.decode(y,{diagnostics:true});assert.deepEqual(result.data,[...bits].map(Number));assert.equal(result.distance,4);
    assert.deepEqual(result.restrictedSyndrome,[0,0,0,0]);
    for(const at of mask){const altered=[...y];altered[at]^=1;assert.deepEqual(P.matrix.decode(altered).data,result.data);}
  }
  assert.equal(makePlan({kind:'pair',pair:'all'}).ticks,12);
  for(const crc of Object.keys(P.CRCS))for(const invert of [8,9,10,11]){
    const p=makePlan({kind:'frame',crc});let decoded=null;
    const d=new StreamDecoder({availableMask:3,crc,onFrame:x=>{decoded=x;},onFault:x=>{throw Error(x);}});
    for(const e of events(p.vectors,{invert}))d.ingest(e);
    assert.equal(decoded,p.frame.bits);assert.equal(d.receiver.meta.seen,3);assert.equal(d.receiver.blocks.length,27);
    assert.ok(d.receiver.blocks.every(b=>b.received.filter(x=>x===null).length===3));
  }
  const p=makePlan({kind:'frame'}),rx=fixture('rx',p);rx.s.start();
  assert.deepEqual(P.rows(p.frame.bits).slice(39,42),['011','110','101']);
  const muted=p.vectors.map((vector,k)=>k>=39&&k<=41?vector&4:vector);
  let badFrame;
  const perturbation=new StreamDecoder({availableMask:3,onFault:(reason,raw)=>{
    assert.equal(reason,'CRC');badFrame=P.parse(raw);
  }});
  for(const e of events(muted))perturbation.ingest(e);
  assert.equal(perturbation.receiver.blocks[11].data.join(''),'00');
  assert.equal(badFrame.data,1);assert.equal(badFrame.crc,p.frame.crc);
  assert.notEqual(badFrame.calculated,badFrame.crc);
  for(const e of events(p.vectors))rx.s.record(e);
  assert.equal((await rx.s.stopPromise).reason,'PHY_COMPLETE');assert.equal(rx.s.plan,null);
  assert.equal(rx.records.filter(e=>e.kind==='PHY_BLOCK').length,27);
  const short=fixture('rx',makePlan({kind:'pair',pair:'all'}));short.s.start();
  for(const e of events(makePlan({kind:'pair',pair:'all'}).vectors))short.s.record(e);
  assert.equal((await short.s.stopPromise).reason,'PHY_COMPLETE');assert.equal(short.records.filter(e=>e.kind==='PHY_BLOCK').length,4);
  const noClock=fixture('rx',p);noClock.s.start();noClock.time(261);noClock.s.pump();
  assert.equal((await noClock.s.stopPromise).reason,'PHY_TIMEOUT');
  const t=fixture('tx',p,true);t.s.start();await finishTx(t);
  assert.equal(t.s.state,'RUNNING'); // TX completion alone cannot confirm.
  const ack=P.frame('ACK',p.frame.ctrl,p.frame.seq,p.frame.sid);
  for(const e of events(P.rows(ack.bits).map(row=>[...row].reduce((v,b,j)=>v|Number(b)<<j,0))))t.s.record(e);
  assert.equal((await t.s.stopPromise).reason,'PHY_COMPLETE');assert.ok(t.records.some(e=>e.kind==='PHY_ACK_RECEIVED'));
  const r=fixture('rx',p,true);r.s.start();for(const e of events(p.vectors))r.s.record(e);
  assert.equal(r.commands.length,0);r.time(2.3);r.s.pump();assert.match(r.commands[0],/^TX 2 /);
  await finishTx(r,2);assert.equal((await r.s.stopPromise).reason,'PHY_COMPLETE');
  const broken=events(p.vectors).slice(0,-1);assert.equal(inspect(broken,87).status,'FAIL');
  const fake=(f,node)=>[
    {kind:'LAUNCH',mode:'hardware',profile:{available_mask:3,experiment:'optical-acoustic',rx_invert:8}},{kind:'BRIDGE_READY',abi:4},...f.records
  ].map(e=>({...e,node,origin:'hardware'}));
  const report=evaluate(fake(t,'A'),fake(r,'B'));assert.equal(report.status,'PASS');assert.equal(report.levels.physical_ack,true);
  const corrupt=fake(r,'B');corrupt.find(e=>e.kind==='CLEANUP').errors=['failed'];assert.equal(evaluate(fake(t,'A'),corrupt).status,'FAIL');
  const profile=JSON.parse(JSON.stringify(require('./profiles/BBB-A-optical-acoustic.json')));
  assert.throws(()=>validate(profile,{hardware:true}),/EVIDENCE/);
  profile.mcp_reset_confirmed=true;Object.assign(profile.calibration,{status:'COMMISSIONING',evidence:'TEST',checked_at:'TEST',rx_invert:8,i2c_device:profile.i2c_device,i2c_adapter_evidence:'TEST'});
  for(const k of Object.keys(profile.calibration.checks))profile.calibration.checks[k]=true;
  validate(profile,{hardware:true});assert.throws(()=>validateLab(profile,{frames:true}),/FRAME_CALIBRATION/);
  console.log('PASS physical-path fixtures: C2 erasure, distance4, single-bit correction, CRCs, polarities, 4 pairs, full frame, independent RX, timeout, ACK guard/return, cleanup and profiles. NOT HARDWARE.');
}
run().catch(e=>{console.error(e);process.exitCode=1;});
