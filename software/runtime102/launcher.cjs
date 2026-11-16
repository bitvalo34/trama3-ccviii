'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawn}=require('node:child_process');
const {load}=require('./profiles.cjs');
const {P2Adapter}=require('./p2-adapter.cjs');
const {ProcessBridge}=require('./bridge.cjs');
const {Supervisor,Journal}=require('./supervisor.cjs');
function exited(child){return child.exitCode!==null||child.signalCode!==null;}
async function terminate(child){
  if(!child||exited(child))return;
  const wait=ms=>new Promise(r=>{const timer=setTimeout(done,ms);function done(){clearTimeout(timer);child.removeListener('exit',done);r();}child.once('exit',done);});
  child.stdin.end();await wait(300);
  if(!exited(child)){child.kill('SIGTERM');await wait(500);}
  if(!exited(child)){child.kill('SIGKILL');await wait(500);}
  if(!exited(child))throw Error('PROCESS_DID_NOT_STOP');
}
function ready(bridge,timeoutMs){return new Promise((resolve,reject)=>{
  const timer=setTimeout(()=>finish(Error('BRIDGE_READY_TIMEOUT')),timeoutMs);
  function finish(error,value){clearTimeout(timer);bridge.removeListener('ready',ok);bridge.removeListener('exit',gone);bridge.removeListener('failure',bad);error?reject(error):resolve(value);}
  const ok=value=>finish(null,value),gone=()=>finish(Error('BRIDGE_START_EXIT')),bad=e=>finish(e);
  bridge.on('ready',ok);bridge.on('exit',gone);bridge.on('failure',bad);
  if(bridge.closed)gone();else if(bridge.readyInfo)ok(bridge.readyInfo);
});}
// One node, one clock, one resource-owning child. Defaults never touch hardware.
async function launch({profileFile,directory,mode='mock',mockRoot,firmware,host,python='python3',
  electricalChecked=false,crc='SMBUS',encoding='utf-8',coordinator=false,readyTimeoutMs=3000,mockHostFlags=[],supervisorFactory=options=>new Supervisor(options)}={}){
  if(!['mock','hardware'].includes(mode))throw Error('MODE');
  const profile=load(profileFile,{hardware:mode==='hardware'});
  if(mode==='hardware'&&(process.platform!=='linux'||!electricalChecked))throw Error('HARDWARE_REQUIRES_LINUX_AND_ELECTRICAL_CHECK');
  if(mode==='mock'&&!mockRoot)throw Error('MOCK_ROOT_REQUIRED');
  if(!firmware||!fs.statSync(firmware).isFile())throw Error('FIRMWARE_MISSING');
  if(mode==='hardware'&&(!host||!fs.statSync(host).isFile()))throw Error('HOST_MISSING');
  fs.mkdirSync(directory,{recursive:false});
  const node=profile.board.slice(-1),epoch=crypto.randomInt(1,0xffffffff),begin=process.hrtime.bigint();
  const clock=()=>Number(process.hrtime.bigint()-begin)/1e9;
  const journal=new Journal(path.join(directory,node+'.jsonl'),{node,origin:mode==='mock'?'simulation':'hardware'});
  let ownerChild,hostChild,owner,supervisor,timer,cleaned=false;
  async function cleanup(){
    if(cleaned)return;clearInterval(timer);
    const errors=[];
    try{await terminate(hostChild);}catch(e){errors.push(e.message);}
    if(owner&&!owner.closed){try{await owner.request('release');}catch(e){errors.push(e.message);}}
    try{await terminate(ownerChild);}catch(e){errors.push(e.message);}
    cleaned=true;if(errors.length)throw Error(errors.join('; '));
  }
  try{
    journal.write({kind:'LAUNCH',mode,profile,epoch,firmware_sha256:crypto.createHash('sha256').update(fs.readFileSync(firmware)).digest('hex')});
    const args=[path.join(__dirname,'resource-worker.py'),'--profile',path.resolve(profileFile),'--firmware',path.resolve(firmware),
      ...(mode==='mock'?['--mock-root',path.resolve(mockRoot)]:['--active'])];
    ownerChild=spawn(python,args,{stdio:['pipe','pipe','pipe'],windowsHide:true});
    owner=new P2Adapter(ownerChild,{timeoutMs:5000});
    ownerChild.stderr.on('data',()=>{}); // Error replies carry actionable text; keep pipe drained.
    const acquired=await owner.request('acquire');journal.write({kind:'RESOURCES_ACQUIRED',...acquired});
    hostChild=mode==='mock'?spawn(process.execPath,[path.join(__dirname,'mock-host.cjs'),String(epoch),...mockHostFlags],{stdio:['pipe','pipe','pipe'],windowsHide:true}):
      spawn(host,[String(epoch),String(profile.rx_invert)],{stdio:['pipe','pipe','pipe'],windowsHide:true});
    const bridge=new ProcessBridge(hostChild);
    const greeting=await ready(bridge,readyTimeoutMs);
    if(greeting.abi!==3||greeting.epoch!==epoch)throw Error('BRIDGE_ABI_OR_EPOCH');
    journal.write({...greeting,kind:'BRIDGE_READY'});
    await owner.request('activate');
    supervisor=supervisorFactory({node,coordinator,crc,encoding,bridge,outputs:owner,cleanup,clock,journal});
    supervisor.start();timer=setInterval(()=>supervisor.pump(),5);
    return {supervisor,profile,mode,directory,stop:()=>supervisor.stop('OPERATOR_STOP')};
  }catch(e){
    let cleanupError=null;try{await cleanup();}catch(c){cleanupError=c.message;}
    try{journal.write({kind:'START_FAILED',error:e.message,cleanup_error:cleanupError});}finally{journal.close();}
    if(cleanupError)e.message+='; cleanup: '+cleanupError;throw e;
  }
}
module.exports={launch,terminate};
if(require.main===module){
  const [mode,profileFile,directory,fourth,fifth,...flags]=process.argv.slice(2);
  if(mode==='plan'){
    const profile=load(profileFile),blockers=[];
    try{load(profileFile,{hardware:true});}catch(e){blockers.push(e.message);}
    if(profile.mcp_reset_confirmed!==true)blockers.push('MCP_RESET_NOT_CONFIRMED');
    console.log(JSON.stringify({board:profile.board,mode:'read-only-plan',physical_status:'NOT_TESTED',blockers,
      steps:['lock runtime and T06','inspect PRU/IEP/PWM/I2C/pins','initialize outputs inactive','load firmware ABI3',
        'wait host ready ABI/epoch','connect clock pin','start one supervisor','STOP, disable outputs, stop host, restore resources'],
      note:'Plan does not authorize hardware; toolchain, electrical checks and actual resource inventory still required.'},null,2));
  }else{
  if(!['mock','hardware'].includes(mode)||!profileFile||!directory||!fourth)throw Error('Usage: launcher.cjs plan PROFILE | mock PROFILE NEW_LOG_DIR NEW_MOCK_ROOT | hardware PROFILE NEW_LOG_DIR FIRMWARE HOST --electrical-checked');
  const options={mode,profileFile,directory,python:process.env.TRAMA3_PYTHON||'python3',
    ...(mode==='mock'?{mockRoot:fourth,firmware:path.join(__dirname,'native/abi.h')}:
      {firmware:fourth,host:fifth,electricalChecked:flags.includes('--electrical-checked'),coordinator:flags.includes('--coordinator')})};
  launch(options).then(session=>{
    console.log(mode.toUpperCase()+' single-node launch ready. Physical validation NOT_TESTED. Ctrl+C to restore.');
    const stop=async()=>{const r=await session.stop();console.log(JSON.stringify(r));process.exitCode=r.errors.length?1:0;};
    process.once('SIGINT',stop);process.once('SIGTERM',stop);
  }).catch(e=>{console.error(e.message);process.exitCode=1;});
  }
}
