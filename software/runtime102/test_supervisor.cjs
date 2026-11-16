'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {EventEmitter}=require('node:events');
const {PassThrough}=require('node:stream');
const {Journal,Supervisor}=require('./supervisor.cjs');
const {ProcessBridge}=require('./bridge.cjs');
const {simulateSupervised}=require('./supervised-simulation.cjs');
(async()=>{
  for(const crc of ['SMBUS','AUTOSAR','SAE-J1850','MAXIM-DOW']){
    const r=await simulateSupervised({crc});assert.equal(r.status,'PASS',crc);
    assert.deepEqual(r.deliveries,[['Respuesta'],['Hola']]);
    assert.ok(r.cleanup.every(c=>c.state==='STOPPED'&&!c.errors.length));
  }
  for(const options of [{latePrepare:true},{failOutput:true}]){
    const r=await simulateSupervised(options);assert.equal(r.status,'FAIL');
    assert.ok(r.records[0].some(e=>e.kind==='SESSION_STOP'&&/OUTPUT/.test(e.reason)));
  }
  let now=0;const bridge=new EventEmitter(),commands=[],log=[];
  bridge.write=c=>commands.push(c);
  let off=false,clean=false;
  const n=new Supervisor({node:'A',coordinator:true,bridge,clock:()=>now,
    outputs:{prepare:async()=>{},shutdown:async()=>{off=true;throw Error('off failed');}},
    cleanup:async()=>{clean=true;},journal:{write:e=>log.push(e),close:()=>{}}});
  n.start();bridge.emit('record',{kind:'done',id:999});
  await n.stop();assert.ok(off&&clean);assert.equal(n.state,'CLEANUP_FAILED');assert.ok(commands.includes('STOP\n'));
  const stalledBridge=new EventEmitter();stalledBridge.write=()=>{};
  const stalled=new Supervisor({node:'A',coordinator:true,bridge:stalledBridge,clock:()=>now,
    outputs:{prepare:()=>new Promise(()=>{}),shutdown:async()=>{}},cleanup:async()=>{},
    journal:{write:e=>log.push(e),close:()=>{}}});
  stalled.start();stalledBridge.emit('record',{kind:'prepare',id:stalled.active.id,index:0,vector:stalled.active.vectors[0]});
  await new Promise(resolve=>setImmediate(resolve));now=0.02;stalled.pump();
  const stalledResult=await stalled.stop();assert.equal(stalledResult.reason,'OUTPUT_PREPARE_TIMEOUT');
  assert.equal(stalledResult.state,'CLEANUP_FAILED');
  const exitBridge=new EventEmitter();exitBridge.write=()=>{};
  const exited=new Supervisor({node:'B',bridge:exitBridge,clock:()=>now,
    outputs:{prepare:async()=>{},shutdown:async()=>{}},cleanup:async()=>{},
    journal:{write:e=>log.push(e),close:()=>{}}});
  exited.start();exitBridge.emit('exit');assert.equal((await exited.stop()).reason,'BRIDGE_EXIT');
  const child=new EventEmitter();child.stdin=new PassThrough();child.stdout=new PassThrough();child.stderr=new PassThrough();
  const adapter=new ProcessBridge(child),received=[],errors=[];
  adapter.on('record',r=>received.push(r));adapter.on('failure',e=>errors.push(e));
  child.stdout.write('{"kind":"do');child.stdout.write('ne","id":1}\n');
  assert.deepEqual(received,[{kind:'done',id:1}]);child.stdout.write('bad\n');assert.equal(errors.length,1);
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'r102-log-'));
  try{
    const file=path.join(dir,'A.jsonl'),journal=new Journal(file,{node:'A'});
    journal.write({kind:'TEST'});journal.close();
    assert.equal(JSON.parse(fs.readFileSync(file,'utf8')).origin,'simulation');
    assert.throws(()=>new Journal(file,{node:'A'}),/EEXIST/);
    const tiny=new Journal(path.join(dir,'tiny'),{node:'B',maxBytes:1});
    assert.throws(()=>tiny.write({kind:'TEST'}),/JOURNAL_LIMIT/);tiny.close();
  }finally{for(const file of fs.readdirSync(dir))fs.unlinkSync(path.join(dir,file));fs.rmdirSync(dir);}
  console.log('PASS supervisor: duplex, CRC negotiation, late/output faults, cleanup, bridge framing, journal');
})().catch(e=>{console.error(e);process.exitCode=1;});
