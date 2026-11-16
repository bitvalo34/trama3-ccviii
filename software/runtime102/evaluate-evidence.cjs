'use strict';
const fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {inspect,pair}=require('./evidence-core.cjs');
const {capture}=require('./bench-core.cjs');
function read(path,jsonl=false){
  if(fs.statSync(path).size>16*1024*1024)throw Error('FILE_LIMIT');
  const bytes=fs.readFileSync(path),text=bytes.toString('utf8');
  if(jsonl&&!text.endsWith('\n'))throw Error('TRUNCATED_JSONL');
  return {path,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),
    value:jsonl?text.trimEnd().split('\n').map(line=>JSON.parse(line)):JSON.parse(text)};
}
function main(args){
  const [mode,manifestFile,aFile,bFile,target]=args;
  if(!['pair','bench'].includes(mode)||!target)throw Error('pair|bench MANIFEST_OR_PLAN TX_OR_A_JSONL RX_OR_B_JSONL NEW_REPORT_JSON');
  const manifest=read(manifestFile),a=read(aFile,true),b=read(bFile,true);
  let result;
  if(mode==='pair')result=pair(manifest.value,a.value,b.value);
  else{
    const p=manifest.value,tx=inspect(a.value,p.tx),rx=inspect(b.value,p.rx);
    result=capture(p,b.value.filter(e=>e.kind==='CAPTURE'));
    const errors=[...result.errors,...tx.errors.map(e=>'TX:'+e),...rx.errors.map(e=>'RX:'+e)];
    if(tx.origin!==rx.origin)errors.push('ORIGIN_MISMATCH');
    for(const [records,role] of [[a.value,'tx'],[b.value,'rx']]){
      const start=records.filter(e=>e.kind==='BENCH_START');
      if(start.length!==1||start[0].role!==role||start[0].run_id!==p.run_id)errors.push('BENCH_IDENTITY');
      if(role==='tx'&&JSON.stringify(start[0]?.plan)!==JSON.stringify(p))errors.push('TX_PLAN');
      if(records.filter(e=>e.kind===(role==='tx'?'BENCH_SENT':'BENCH_RECEIVED')).length!==1)errors.push('BENCH_INCOMPLETE');
      if(!records.some(e=>e.kind==='SESSION_STOP'&&e.reason==='BENCH_COMPLETE'))errors.push('BENCH_STOP');
    }
    result={...result,origin:tx.origin,errors,status:errors.length?'FAIL':'PASS'};
  }
  result.inputs=[manifest,a,b].map(({path,sha256})=>({path,sha256}));
  result.evaluator_sources={};
  for(const name of ['evaluate-evidence.cjs','evidence-core.cjs','bench-core.cjs'])
    result.evaluator_sources[name]=crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,name))).digest('hex');
  result.generated_at_pc=new Date().toISOString();
  fs.writeFileSync(target,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
  console.log(result.status+' '+target);process.exitCode=result.status==='PASS'?0:1;
}
if(require.main===module){try{main(process.argv.slice(2));}catch(e){console.error(e.message);process.exitCode=2;}}
