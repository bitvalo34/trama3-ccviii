'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {spawn}=require('node:child_process');
const {P2Adapter}=require('./p2-adapter.cjs');const {load}=require('./profiles.cjs');
const {simulateSupervised}=require('./supervised-simulation.cjs');const {server}=require('./node-web.cjs');
async function until(fn){for(let i=0;i<5000;i++){if(fn())return;await new Promise(r=>setTimeout(r,2));}throw Error('TEST_TIMEOUT');}
(async()=>{
  for(const node of ['A','B']){const f=path.join(__dirname,'profiles/BBB-'+node+'.json');assert.equal(load(f).board,'BBB-'+node);assert.throws(()=>load(f,{hardware:true}),/UNCALIBRATED/);}
  const python=process.env.TRAMA3_PYTHON||'python3';
  const children=[0,1].map(()=>spawn(python,[path.join(__dirname,'p2-worker.py'),'--mock'],{stdio:['pipe','pipe','pipe'],windowsHide:true}));
  try{
    const outputs=children.map(c=>new P2Adapter(c));await Promise.all(outputs.map(o=>o.initialize()));
    await assert.rejects(outputs[0].prepare(8),/Vector/);
    const result=await simulateSupervised({a:'A',b:'B',outputs});assert.equal(result.status,'PASS');assert.deepEqual(result.deliveries,[['B'],['A']]);
  }finally{children.forEach(c=>c.kill());}
  const directory=path.join(fs.mkdtempSync(path.join(os.tmpdir(),'trama3-chat-')),'session');
  const s=server({directory,encoding:'utf-8'});await new Promise(r=>s.listen(0,'127.0.0.1',r));
  try{
    const base='http://127.0.0.1:'+s.address().port;
    const send=(node,text)=>fetch(base+'/send?node='+node,{method:'POST',body:JSON.stringify({text})});
    assert.equal((await fetch(base+'/?node=A')).status,200);
    assert.equal((await send('A','Hola 🌎')).status,202);assert.equal((await send('B','Respuesta ñ')).status,202);
    await until(()=>s.session.messages.every(row=>row.some(m=>m.status==='confirmed')));
    assert.ok(s.session.snapshot('B').messages.some(m=>m.text==='Hola 🌎'&&m.direction==='received'));
    assert.equal((await send('A','Segundo mensaje')).status,202);
    await until(()=>s.session.messages[0].filter(m=>m.status==='confirmed').length===2);
    assert.equal((await fetch(base+'/send?node=A',{method:'POST',headers:{Origin:'http://otro.invalid'},body:'{}'})).status,403);
    assert.equal((await send('X','no')).status,400);
    const log=await (await fetch(base+'/log?node=A')).text();assert.match(log,/MESSAGE_CONFIRMED/);
    assert.match(log,/"origin":"simulation"/);
  }finally{await s.session.stop();await new Promise(r=>s.close(r));}
  const {ChatSession}=require('./chat-session.cjs');
  const cp=new ChatSession({directory:directory+'-cp',encoding:'windows-1252',crc:'MAXIM-DOW'});
  try{
    cp.send('A','Espa\u00f1a \u20ac');
    await until(()=>cp.messages[0].some(m=>m.status==='confirmed'));
    assert.ok(cp.messages[1].some(m=>m.text==='Espa\u00f1a \u20ac'));
    assert.throws(()=>cp.send('A','\ud83c\udf0e'));
    for(let i=0;i<8;i++)cp.send('A','queued');
    assert.throws(()=>cp.send('A','overflow'),/QUEUE_FULL/);
  }finally{await cp.stop();}
  const faultSession=new ChatSession({directory:directory+'-fault',fault:'corrupt-data'});
  try{
    faultSession.send('A','CRC');
    await until(()=>faultSession.messages[0].some(m=>m.status==='confirmed'));
    const state=faultSession.snapshot('A');assert.ok(state.stats.retries>0);
    assert.ok(state.diagnostics.some(e=>e.kind==='NACK_ACCEPTED'));
    assert.equal(faultSession.messages[1].filter(m=>m.direction==='received').length,1);
  }finally{await faultSession.stop();}
  console.log('PASS profiles, persistent Python P2 worker, supervised exchange, multi-message node chat, UTF8, logs, origin checks');
})().catch(e=>{console.error(e);process.exitCode=1;});
