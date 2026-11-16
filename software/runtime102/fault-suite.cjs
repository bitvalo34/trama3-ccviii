'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {simulateSupervised}=require('./supervised-simulation.cjs');
const {Journal}=require('./supervisor.cjs');
const scenarios=[
  {name:'baseline',options:{},expected:'PASS'},
  {name:'lost-data-ack',options:{fault:'drop-data-ack'},expected:'PASS',duplicates:true},
  {name:'lost-end-ack',options:{fault:'drop-end-ack'},expected:'PASS',duplicates:true},
  {name:'crc-nack-retry',options:{fault:'corrupt-data'},expected:'PASS',nack:true},
  {name:'no-A-channel',options:{fault:'drop-all-A'},expected:'FAIL',reason:'PROTOCOL_FAULT'},
  {name:'bridge-exit',options:{fault:'bridge-exit'},expected:'FAIL',reason:'BRIDGE_EXIT'},
  {name:'capture-gap',options:{fault:'capture-gap'},expected:'FAIL',reason:'SEQUENCE_GAP'},
  {name:'epoch-change',options:{fault:'epoch-change'},expected:'FAIL',reason:'EPOCH_CHANGED'},
  {name:'output-error',options:{failOutput:true},expected:'FAIL',reason:'OUTPUT_IO'},
  {name:'output-late',options:{latePrepare:true},expected:'FAIL',reason:'OUTPUT_PREPARE_LATE'}
];
function sources(){
  const result={};
  function visit(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true})){
    if(['dist','build','__pycache__'].includes(e.name))continue;
    const f=path.join(dir,e.name);if(e.isDirectory())visit(f);
    else if(/\.(cjs|js|py|c|h|sh|json|html|md)$/.test(e.name))result[path.relative(path.join(__dirname,'..'),f).replaceAll('\\','/')]=crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
  }}visit(__dirname);
  for(const n of ['core.js','engine.js'])result['matrices102/'+n]=crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'../matrices102',n))).digest('hex');
  return result;
}
async function runSuite(directory){
  fs.mkdirSync(directory,{recursive:false});const checks=[];
  for(const s of scenarios){
    const folder=path.join(directory,s.name);fs.mkdirSync(folder);
    const events=[[],[]],journals=['A','B'].map((node,i)=>{
      const j=new Journal(path.join(folder,node+'.jsonl'),{node});
      return {write:e=>{if(e.kind!=='CAPTURE')events[i].push(e);j.write(e);},close:()=>j.close()};
    });
    const r=await simulateSupervised({...s.options,journals});
    const assertions={status:r.status===s.expected,cleanup:r.cleanup.every(c=>c.state==='STOPPED'&&c.errors.length===0)};
    if(s.options.fault)assertions.injection_observed=r.injections.length>0;
    if(s.expected==='PASS')assertions.exactly_once=JSON.stringify(r.deliveries)===JSON.stringify([['Respuesta'],['Hola']]);
    if(s.duplicates){assertions.duplicate_detected=r.stats.some(x=>x.duplicates>0);assertions.retry=r.stats.some(x=>x.retries>0);}
    if(s.nack){assertions.nack=events.flat().some(e=>e.kind==='NACK_ACCEPTED');assertions.retry=r.stats.some(x=>x.retries>0);}
    if(s.reason)assertions.reason=r.cleanup.some(c=>c.reason===s.reason);
    if(s.name==='no-A-channel')assertions.bounded_attempts=r.stats[0].retries===3;
    const {records,...summary}=r;
    const check={name:s.name,expected_session_status:s.expected,verdict:Object.values(assertions).every(Boolean)?'PASS':'FAIL',assertions,...summary};
    fs.writeFileSync(path.join(folder,'summary.json'),JSON.stringify(check,null,2),{flag:'wx'});checks.push(check);
  }
  const report={schema:1,origin:'simulation',physical_status:'NOT_TESTED',created_at:new Date().toISOString(),node:process.version,
    status:checks.every(c=>c.verdict==='PASS')?'PASS':'FAIL',sources:sources(),checks};
  fs.writeFileSync(path.join(directory,'report.json'),JSON.stringify(report,null,2),{flag:'wx'});
  const rows=checks.map(c=>'| '+c.name+' | '+c.expected_session_status+' | '+c.status+' | '+c.verdict+' |').join('\n');
  fs.writeFileSync(path.join(directory,'REPORTE.md'),'# Banco de fallos del runtime\n\nSimulacion: no acredita pruebas fisicas. FAIL esperado significa parada protectora, no fallo del ensayo.\n\n| Caso | Sesion esperada | Observada | Ensayo |\n| --- | --- | --- | --- |\n'+rows+'\n\nreport.json contiene hashes de fuentes y las comprobaciones. Cada carpeta conserva A.jsonl/B.jsonl.\n',{flag:'wx'});
  return report;
}
module.exports={runSuite,scenarios};
if(require.main===module){
  if(!process.argv[2])throw Error('Usage: node fault-suite.cjs NEW_DIRECTORY');
  runSuite(process.argv[2]).then(r=>{console.log(JSON.stringify({status:r.status,checks:r.checks.map(c=>({name:c.name,verdict:c.verdict,assertions:c.assertions}))},null,2));process.exitCode=r.status==='PASS'?0:1;}).catch(e=>{console.error(e);process.exitCode=1;});
}
