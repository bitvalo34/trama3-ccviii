'use strict';
const fs=require('node:fs');
const {launch}=require('./launcher.cjs');
const {Bench}=require('./bench.cjs');
const {plan,patterns}=require('./bench-core.cjs');
async function main(args){
  if(args[0]==='plan'){
    const [,pattern,id,tx,target]=args;
    if(!target)throw Error('plan PATTERN RUN_ID A|B NEW_JSON');
    fs.writeFileSync(target,JSON.stringify(plan(pattern,id,tx),null,2)+'\n',{flag:'wx'});return;
  }
  const [role,profileFile,directory,firmware,host,runId,pattern,...flags]=args;
  if(!['tx','rx'].includes(role)||!runId||!pattern||
     (role==='tx'&&!patterns.includes(pattern))||(role==='rx'&&pattern!=='none')||
     !flags.includes('--electrical-checked')||!flags.includes('--experimental-bench'))
    throw Error('tx|rx PROFILE NEW_LOG_DIR FIRMWARE HOST RUN_ID PATTERN|none --electrical-checked --experimental-bench');
  const session=await launch({mode:'hardware',profileFile,directory,firmware,host,
    python:process.env.TRAMA3_PYTHON||'python3',electricalChecked:true,
    supervisorFactory:options=>new Bench(options,{role,pattern,runId})});
  const stop=()=>{void session.supervisor.stop('OPERATOR_SIGNAL');};
  process.once('SIGINT',stop);process.once('SIGTERM',stop);
  console.log('Diagnostic '+role+'; bounded 180 seconds; no chat/ACK. Log: '+directory);
  const timer=setInterval(()=>{
    const s=session.supervisor;
    if(['STOPPED','CLEANUP_FAILED'].includes(s.state)){
      clearInterval(timer);process.removeListener('SIGINT',stop);process.removeListener('SIGTERM',stop);
      s.stopPromise.then(result=>{
        console.log(JSON.stringify(result));
        process.exitCode=result.reason==='BENCH_COMPLETE'&&!result.errors.length?0:1;
      });
    }
  },100);
}
if(require.main===module)main(process.argv.slice(2)).catch(e=>{console.error(e.message);process.exitCode=1;});
