'use strict';
const path=require('node:path');
const {launch}=require('./launcher.cjs');

// Local console only. Messages go through Supervisor/Endpoint and physical IO,
// never through a network connection to the other node.
function attach(session,{input=process.stdin,output=process.stdout,intervalMs=500}={}){
  let buffer='',closing=false,last='',deliveryCount=0;
  const supervisor=session.supervisor;
  const emit=r=>output.write(JSON.stringify(r)+'\n');
  const snapshot=()=>({kind:'STATUS',board:session.profile.board,mode:session.mode,
    physical_status:'NOT_TESTED',supervisor:supervisor.state,
    protocol:supervisor.endpoint.state,stats:supervisor.endpoint.stats,
    sending:!!(supervisor.endpoint.pending||supervisor.endpoint.specs.length),
    received:supervisor.endpoint.deliveries.length,log:session.directory});
  let resolveDone;const done=new Promise(r=>{resolveDone=r;});
  async function close(reason='OPERATOR_STOP'){
    if(closing)return done;closing=true;clearInterval(timer);
    input.removeListener('data',data);input.removeListener('end',ended);input.pause();
    try{const result=await supervisor.stop(reason);emit({kind:'STOPPED',...result});resolveDone(result);}
    catch(e){const result={state:'CLEANUP_FAILED',errors:[e.message]};emit(result);resolveDone(result);}
    return done;
  }
  function command(line){
    if(closing)return;
    if(line==='status'){emit(snapshot());return;}
    if(line==='stop'){void close();return;}
    if(line==='help'){emit({kind:'HELP',commands:['status','send TEXTO','stop'],note:'send requires CONNECTED; acceptance is not delivery confirmation.'});return;}
    if(line.startsWith('send ')){
      const text=line.slice(5);
      if(!text.length){emit({kind:'REJECTED',reason:'EMPTY_MESSAGE'});return;}
      try{supervisor.send(text);emit({kind:'SUBMITTED',text,confirmed:false});}
      catch(e){emit({kind:'REJECTED',reason:e.message});}
      return;
    }
    if(line)emit({kind:'REJECTED',reason:'UNKNOWN_COMMAND'});
  }
  function data(chunk){
    // Bound each line, even if a sender never provides a newline.
    for(const part of String(chunk).split(/(?<=\n)/)){
      buffer+=part;
      if(Buffer.byteLength(buffer,'utf8')>4096){void close('CONSOLE_LINE_LIMIT');return;}
      if(buffer.endsWith('\n')){const line=buffer.replace(/\r?\n$/,'');buffer='';command(line);}
      if(closing)return;
    }
  }
  function ended(){void close('CONSOLE_EOF');}
  function poll(){
    const state=snapshot(),key=JSON.stringify(state);
    if(key!==last){last=key;emit(state);}
    while(deliveryCount<supervisor.endpoint.deliveries.length)
      emit({kind:'DELIVERY',text:supervisor.endpoint.deliveries[deliveryCount++]});
    if(['STOPPED','CLEANUP_FAILED'].includes(supervisor.state))void close('SESSION_ENDED');
  }
  input.setEncoding('utf8');input.on('data',data);input.once('end',ended);
  const timer=setInterval(poll,intervalMs);poll();
  emit({kind:'CONSOLE_READY',note:'One node only. See JSONL for ACK, NACK, retries and MESSAGE_CONFIRMED. EOF/Ctrl+C stops.'});
  return {close,done,snapshot};
}

async function main(args){
  const [mode,profileFile,directory,fourth,fifth,...flags]=args;
  if(!['mock','hardware'].includes(mode)||!profileFile||!directory||!fourth)
    throw Error('Usage: terminal.cjs mock PROFILE NEW_LOG_DIR NEW_MOCK_ROOT | hardware PROFILE NEW_LOG_DIR FIRMWARE HOST --electrical-checked [--coordinator]');
  if(mode==='hardware'&&!fifth)throw Error('HOST_REQUIRED');
  const session=await launch({mode,profileFile,directory,python:process.env.TRAMA3_PYTHON||'python3',
    ...(mode==='mock'?{mockRoot:fourth,firmware:path.join(__dirname,'native/abi.h')}:
    {firmware:fourth,host:fifth,electricalChecked:flags.includes('--electrical-checked'),coordinator:flags.includes('--coordinator')})});
  const terminal=attach(session);
  const stop=()=>{void terminal.close('OPERATOR_SIGNAL');};
  process.once('SIGINT',stop);process.once('SIGTERM',stop);
  const result=await terminal.done;
  process.removeListener('SIGINT',stop);process.removeListener('SIGTERM',stop);
  process.exitCode=result.state==='STOPPED'?0:1;
}
module.exports={attach};
if(require.main===module)main(process.argv.slice(2)).catch(e=>{console.error(e.message);process.exitCode=1;});
