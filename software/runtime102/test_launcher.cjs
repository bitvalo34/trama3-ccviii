'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {launch}=require('./launcher.cjs');
(async()=>{
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'runtime-launch-'));
  const base={profileFile:path.join(__dirname,'profiles/BBB-B.json'),firmware:path.join(__dirname,'native/abi.h'),
    python:process.env.TRAMA3_PYTHON||'python3',mockRoot:path.join(root,'board')};
  const session=await launch({...base,directory:path.join(root,'success')});
  assert.equal(session.supervisor.state,'RUNNING');
  assert.equal(fs.readFileSync(path.join(root,'board/pins/P8_11'),'utf8'),'pruout');
  await assert.rejects(launch({...base,directory:path.join(root,'second')}));
  assert.ok(fs.existsSync(path.join(root,'board/owner')));
  const stop=await session.stop();assert.equal(stop.state,'STOPPED');
  assert.equal(fs.readFileSync(path.join(root,'board/sys/pru0/state'),'utf8'),'offline');
  assert.ok(!fs.existsSync(path.join(root,'board/owner')));
  for(const [name,flags,pattern] of [['exit',['--fail-start'],/START_EXIT/],['timeout',['--silent'],/READY_TIMEOUT/],['abi',['--wrong-abi'],/ABI_OR_EPOCH/]]){
    await assert.rejects(launch({...base,directory:path.join(root,name),mockHostFlags:flags,readyTimeoutMs:name==='timeout'?200:5000}),pattern);
    assert.ok(!fs.existsSync(path.join(root,'board/owner')));
    assert.equal(fs.readFileSync(path.join(root,'board/pins/P8_11'),'utf8'),'default');
  }
  await assert.rejects(launch({...base,mode:'hardware',directory:path.join(root,'real')}),/UNCALIBRATED/);
  assert.ok(!fs.existsSync(path.join(root,'real')));
  const crash=await launch({...base,directory:path.join(root,'runtime-crash'),coordinator:true});
  const until=Date.now()+5000;
  while(['RUNNING','STOPPING'].includes(crash.supervisor.state)&&Date.now()<until)await new Promise(r=>setTimeout(r,10));
  assert.equal(crash.supervisor.state,'STOPPED');assert.ok(!fs.existsSync(path.join(root,'board/owner')));
  assert.match(fs.readFileSync(path.join(root,'runtime-crash/B.jsonl'),'utf8'),/BRIDGE_EXIT/);
  console.log('PASS single-node launcher: processes, duplicate lock, bridge exit, startup timeout, rollback, uncalibrated block');
})().catch(e=>{console.error(e);process.exitCode=1;});
