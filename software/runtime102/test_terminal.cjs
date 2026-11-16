'use strict';
const assert=require('node:assert/strict'),{PassThrough}=require('node:stream');
const {attach}=require('./terminal.cjs');
const {launch}=require('./launcher.cjs');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
function streams(){const input=new PassThrough(),output=new PassThrough();let text='';output.on('data',x=>text+=x);return {input,output,read:()=>text};}
(async()=>{
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'runtime-console-'));
  const session=await launch({mode:'mock',profileFile:path.join(__dirname,'profiles/BBB-B.json'),
    directory:path.join(root,'logs'),mockRoot:path.join(root,'board'),firmware:path.join(__dirname,'native/abi.h'),
    python:process.env.TRAMA3_PYTHON||'python3'});
  const io=streams(),terminal=attach(session,{...io,intervalMs:10});
  io.input.write('sta');io.input.write('tus\r\nsend Hola\n');
  assert.match(io.read(),/REJECTED/); // real supervisor is not CONNECTED
  assert.ok(!session.supervisor.endpoint.pending);
  io.input.end();assert.equal((await terminal.done).state,'STOPPED');
  assert.ok(!fs.existsSync(path.join(root,'board/owner')));
  const received=[],fake={state:'RUNNING',endpoint:{state:'CONNECTED',stats:{},pending:null,specs:[],deliveries:[]},
    send:text=>received.push(text),stop:async()=>({state:'STOPPED',errors:[]})};
  const io2=streams(),t2=attach({supervisor:fake,profile:{board:'BBB-A'},mode:'mock',directory:'fixture'},{...io2,intervalMs:10});
  io2.input.write('send Hola\nsend Adi\u00f3s\n');assert.deepEqual(received,['Hola','Adi\u00f3s']);
  assert.match(io2.read(),/"confirmed":false/);
  io2.input.write('x'.repeat(4097));assert.equal((await t2.done).state,'STOPPED');
  console.log('PASS console: real launcher, fragmented commands, disconnected rejection, EOF restore, send delegation, bounded input');
})().catch(e=>{console.error(e);process.exitCode=1;});
