'use strict';
const {plan,capture,patterns}=require('./bench-core.cjs');
const {pair}=require('./evidence-core.cjs');
const {AcousticWindow}=require('./acoustic-window.cjs');
function run(){
 let count=0;
 const ok=(x,m)=>{count++;if(!x)throw Error(m);};
 const throws=(fn,m)=>{let hit=false;try{fn();}catch(_){hit=true;}ok(hit,m);};
 const events=p=>p.vectors.flatMap((v,i)=>{
   const base=BigInt(i)*200000000n+4294967200n;
   return [[base,8|v,1],[base+BigInt(i?40000000:120000000),v,1],[base+160000000n,v,2]]
     .map(([t,normalized,flags],j)=>({sequence:3*i+j,epoch:19,ticks_lo:Number(t&0xffffffffn),
       ticks_hi:Number(t>>32n),r31:0,normalized,flags}));
 });
 for(const name of patterns){const p=plan(name,'trial','A');ok(capture(p,events(p)).status==='PASS',name);}
 const p=plan('vectors','trial','A'),ev=events(p);
 ok(capture(p,ev.slice(1)).status==='FAIL','missing edge');
 let bad=JSON.parse(JSON.stringify(ev));bad[5].normalized^=2;
 ok(capture(p,bad).errors.includes('VECTOR_MISMATCH'),'wrong channel');
 bad=JSON.parse(JSON.stringify(ev));bad[100].sequence++;
 ok(capture(p,bad).errors.includes('SEQUENCE_GAP'),'gap');
 bad=JSON.parse(JSON.stringify(ev));bad[100].epoch++;
 ok(capture(p,bad).errors.includes('EPOCH'),'epoch');
 bad=JSON.parse(JSON.stringify(ev));bad[2].ticks_lo+=4000;
 ok(capture(p,bad).errors.includes('SAMPLE_DEADLINE'),'late sample');
 throws(()=>capture({...p,vectors:Array(87).fill(0)},ev),'altered plan');
 throws(()=>plan('invalid','trial','A'),'invalid pattern');
 const config={start:20,end:80,minActive:15,maxGap:10};
 const w=new AcousticWindow(config);
 for(let t=10;t<=80;t+=10)w.feed(t,t>=30&&t<50?1:0);
 ok(w.result().value===1&&w.result().active_ticks===20,'burst absent at final sample');
 const noise=new AcousticWindow(config);
 for(let t=10;t<=80;t+=10)noise.feed(t,t===30?1:0);
 ok(noise.result().value===0,'brief noise');
 const silence=new AcousticWindow(config);
 for(let t=10;t<=80;t+=10)silence.feed(t,0);
 ok(silence.result().value===0,'silence');
 const outside=new AcousticWindow(config,1);
 for(let t=10;t<=80;t+=10)outside.feed(t,0);
 ok(outside.result().active_ticks===0,'outside window');
 const gap=new AcousticWindow(config);
 throws(()=>gap.feed(11,1),'gap fail');
 throws(()=>gap.result(),'sticky gap');
 throws(()=>new AcousticWindow({...config,minActive:0}),'zero threshold');
 throws(()=>new AcousticWindow(config).result(),'unfinished');
 const log=(node,text)=>[
   {kind:'LAUNCH',profile:{board:'BBB-'+node},epoch:1,firmware_sha256:'a'.repeat(64)},
   {kind:'SESSION_START',t:0},{kind:'DELIVERY',text,t:1},{kind:'MESSAGE_CONFIRMED',t:2},
   {kind:'SESSION_STOP',reason:'CONSOLE_EOF',t:3},{kind:'CLEANUP',errors:[],t:4}
 ].map((r,record)=>({...r,node,origin:'simulation',record}));
 const manifest={schema:1,run_id:'pair',origin:'simulation',A_to_B:['Hola'],B_to_A:['Respuesta']};
 const a=log('A','Respuesta'),b=log('B','Hola');
 ok(pair(manifest,a,b).status==='PASS','pair');
 ok(pair(manifest,a,b.slice(0,-1)).status==='FAIL','missing cleanup');
 ok(pair({...manifest,origin:'hardware'},a,b).status==='FAIL','no simulated hardware pass');
 bad=JSON.parse(JSON.stringify(b));bad[2].text='Otro';
 ok(pair(manifest,a,bad).status==='FAIL','wrong delivery');
 bad=JSON.parse(JSON.stringify(b));bad[5].errors=['shutdown'];
 ok(pair(manifest,a,bad).status==='FAIL','cleanup failure');
 bad=JSON.parse(JSON.stringify(b));bad[3].record=2;
 ok(pair(manifest,a,bad).status==='FAIL','truncated/reordered log');
 return {checks:count,status:'PASS',origin:'synthetic',physical_status:'NOT_TESTED'};
}
module.exports={run};
if(require.main===module)console.log(JSON.stringify(run(),null,2));
