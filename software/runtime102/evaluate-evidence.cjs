'use strict';
const fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {inspect,pair,summarize,interference}=require('./evidence-core.cjs');
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
  if(mode==='summary'&&args.length===3){
    const log=read(manifestFile,true);
    const result={schema:1,...summarize(log.value),input:{path:log.path,sha256:log.sha256}};
    fs.writeFileSync(aFile,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
    console.log(JSON.stringify(result,null,2));return;
  }
  if(!['pair','bench','interference'].includes(mode)||args.length!==5)
    throw Error('pair|bench|interference MANIFEST_OR_PLAN A_JSONL B_JSONL NEW_REPORT_JSON | summary NODE_JSONL NEW_REPORT_JSON');
  const manifest=read(manifestFile),a=read(aFile,true),b=read(bFile,true);
  let result;
  if(mode==='pair')result=pair(manifest.value,a.value,b.value);
  else if(mode==='interference'){
    result=interference(manifest.value,a.value,b.value);
    result.commit=manifest.value.commit;
    if(result.origin==='hardware'){
      result.media=verifyMedia(manifest.value,path.dirname(manifestFile),result.errors);
      result.status=result.errors.length?'FAIL':'PASS';
      if(result.status==='PASS')result.physical_status='CUMPLE';
    }
    result.limitations=['El evaluador correlaciona hechos y archivos declarados. El operador verifica el contenido de la captura y las condiciones físicas.'];
  }
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
function verifyMedia(manifest,directory,errors){
  const {perturbation,evidence}=manifest;
  if(!perturbation||!Array.isArray(perturbation.channels)||!perturbation.channels.length||
    perturbation.channels.some(x=>!['C0','C1','C2'].includes(x))||
    !Number.isFinite(perturbation.start_s)||!Number.isFinite(perturbation.end_s)||
    perturbation.start_s<0||perturbation.end_s<=perturbation.start_s||
    perturbation.reference!=='DATA_CLK'||typeof perturbation.method!=='string'||!perturbation.method.trim()){
    errors.push('PHYSICAL_INTERVAL');}
  if(!Array.isArray(evidence)||!evidence.some(e=>['photo','video','instrument'].includes(e.kind))||
    !evidence.some(e=>e.kind==='acta')){
    errors.push('PHYSICAL_ATTACHMENTS_REQUIRED');return [];
  }
  const base=fs.realpathSync(directory),verified=[];
  for(const entry of evidence){
    try{
      if(typeof entry.path!=='string'||path.isAbsolute(entry.path))throw Error('PATH');
      const file=fs.realpathSync(path.join(base,entry.path)),relative=path.relative(base,file);
      if(!relative||relative.startsWith('..')||path.isAbsolute(relative)||!fs.statSync(file).isFile())throw Error('PATH');
      const hash=crypto.createHash('sha256'),fd=fs.openSync(file,'r'),buffer=Buffer.alloc(65536);
      try{for(let n;(n=fs.readSync(fd,buffer,0,buffer.length,null));)hash.update(buffer.subarray(0,n));}
      finally{fs.closeSync(fd);}
      if(hash.digest('hex')!==entry.sha256)throw Error('HASH');
      verified.push(entry);
    }catch(e){errors.push('ATTACHMENT_'+e.message);}
  }
  return verified;
}
if(require.main===module){try{main(process.argv.slice(2));}catch(e){console.error(e.message);process.exitCode=2;}}
