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
    const recent=await (await fetch(base+'/events?node=A&type=ACK&filter=ack')).json();
    assert.ok(recent.entries.length);assert.ok(recent.entries.every(e=>e.type==='ACK'));
    assert.equal((await fetch(base+'/send',{method:'POST',body:'{'})).status,400);
    assert.equal((await fetch(base+'/send',{method:'POST',body:'x'.repeat(8193)})).status,413);
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
  const {NodeChat}=require('./chat-session.cjs');
  const {Endpoint}=require('./endpoint.cjs'),{Journal}=require('./supervisor.cjs');
  const P=require('./protocol.cjs'),localDir=directory+'-local';
  fs.mkdirSync(localDir);
  const chat=new NodeChat(localDir);
  const journal=new Journal(path.join(localDir,'B.jsonl'),{node:'B',onRecord:e=>chat.event(e)});
  const endpoint=new Endpoint({id:'B',log:e=>journal.write(e)});
  const supervisor={endpoint,state:'RUNNING',decoder:{},lastClockSample:null,send:text=>endpoint.send(text)};
  chat.attach({supervisor,profile:{board:'BBB-B',period_s:1,available_mask:3},mode:'mock'});
  const local=server({session:chat});await new Promise(r=>local.listen(0,'127.0.0.1',r));
  try{
    const base='http://127.0.0.1:'+local.address().port;
    const state=()=>fetch(base+'/state').then(r=>r.json());
    const send=text=>fetch(base+'/send',{method:'POST',body:JSON.stringify({text})});
    assert.equal((await state()).node,'B');
    assert.equal((await state()).available_mask,3);
    assert.equal((await fetch(base+'/state?node=A')).status,400);
    assert.equal((await send('A')).status,409);
    endpoint.state='CONNECTED';
    assert.equal((await send('A')).status,202);
    const status=async()=>(await state()).messages.at(-1).status;
    assert.equal(await status(),'pending');
    let t=1;
    for(const kind of ['START','LEN_LO','LEN_HI','DATA','END']){
      const job=endpoint.take(t++);
      assert.equal(job.frame.type,kind);
      assert.equal(await status(),'sending');
      endpoint.txDone(job.id,t++);
      assert.equal(await status(),'waiting_ack');
      endpoint.receive(P.frame('ACK',job.frame.ctrl,job.frame.seq,job.frame.sid).bits,t++);
    }
    assert.equal(await status(),'confirmed');
    assert.equal((await fetch(base+'/log')).headers.get('content-disposition'),'attachment; filename="B.jsonl"');
    assert.equal((await send('B')).status,202);
    chat.event({kind:'SESSION_STOP',reason:'TEST_INTERRUPTION'});
    assert.equal(await status(),'uncertain');
  }finally{journal.close();await new Promise(r=>local.close(r));}
  console.log('PASS profiles, persistent Python P2 worker, supervised exchange, multi-message node chat, UTF8, logs, origin checks');
})().catch(e=>{console.error(e);process.exitCode=1;});
