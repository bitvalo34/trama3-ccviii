'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const E=require('./engine.js'),R=require('./reference.cjs'),M=require('./core.js');
const rows=[];let n=0;
function check(name,options,expected='COMPLETE'){
 const r=E.simulate(options);assert.equal(r.status,expected,name);
 if(expected==='COMPLETE'){
  for(const [dir,text] of [[0,options.a??'A'],[1,options.b??'']]){
   const got=r.deliveries.filter(d=>d.dir===dir);assert.equal(got.length,text?1:0,name);
   if(text)assert.equal(got[0].text,text,name);
  }
 }
 assert.equal(r.stats.undetected,0,name);
 rows.push({name,status:r.status,duration:r.duration,stats:r.stats,deliveries:r.deliveries,periods:r.finalPeriods});
 n++;return r;
}
const math=R.tests();
for(let mask=0;mask<512;mask++)for(const d of [[0,0],[0,1],[1,0],[1,1]]){
 const y=M.encode(d).map((v,i)=>mask&(1<<i)?v:null);
 assert.deepEqual(M.decode(y),R.decode(y));n++;
}
for(let a=0;a<8;a++)for(let b=0;b<8;b++){
 check('Canales '+a+'/'+b,{a:'Hola',b:'Sí',outages:[...(a?[{mask:a,dir:0}]:[]),...(b?[{mask:b,dir:1}]:[])]},a===7||b===7?'RECOVERY_1HZ':'COMPLETE');
}
for(const crc of Object.keys(E.CRCS))for(let hzA=1;hzA<=4;hzA++)for(let hzB=1;hzB<=4;hzB++)
 check(crc+' '+hzA+'/'+hzB,{a:'Hola',b:'Adrián',crc,hzA,hzB});
for(const scenario of ['crc','two-errors','frame-crc','ack','clock','extra-clock','pwm-bit','pwm-width','pwm-start','pwm-tail','clock-skew','clock-period','truncated','ready','stale','wrong-seq','ack-end','rate-ready','rate-active','rate-part','fallback']){
 const r=check(scenario,{a:'Hola',b:'Adrián',scenario,hzA:2,hzB:4});
 if(scenario==='crc'||scenario==='two-errors')assert.ok(r.events.some(e=>e.kind==='MATRIX_BLOCK'&&e.status==='CORRECTED'));
 if(scenario==='frame-crc')assert.ok(r.stats.crcErrors>=1&&r.stats.retries>=1);
}
check('reset',{scenario:'reset'},'SESSION_LOST');
check('version',{scenario:'version'},'RECOVERY_1HZ');
check('rechazo frecuencia',{scenario:'rate-reject',hzA:2},'RECOVERY_1HZ');
for(const mask of [1,2,3,4,5,6])for(const level of [0,1])for(const on of ['data','mid']){
 check('Corte '+mask+' '+level+' '+on,{a:'Hola',outages:[{mask,level,on,dir:0}]});
 check('Corte temporal '+mask+' '+level+' '+on,{a:'Hola',outages:[{mask,level,on,dir:0,duration:120}]});
}
check('Los tres desde DATA',{a:'Hola',outages:[{mask:7,on:'data'}]},'LINK_FAULT');
check('Los tres temporalmente',{a:'Hola',outages:[{mask:7,on:'data',duration:120}]});
check('Reloj perdido',{a:'Hola',outages:[{mask:0,clock:true,on:'data'}]},'LINK_FAULT');
check('Reloj temporal',{a:'Hola',outages:[{mask:0,clock:true,on:'data',duration:120}]});
check('CP1252',{a:'Ñ €',encoding:'windows-1252'});
check('Vuelta SEQ',{a:'x'.repeat(260)});
check('UTF8',{a:'¡Hola! 🐈',b:'€'});
for(const o of [{a:'x'.repeat(1025)},{a:'🐈',encoding:'windows-1252'},{hz:0},{hz:5},{ber:-1},{outages:[{mask:8}]}]){assert.throws(()=>E.simulate(o));n++;}
for(const text of ['A','Hola'])check('Tiempo '+text,{a:text});
const slow=E.sweep({mechanicalMs:500});
assert.ok(slow.some(x=>!x.all));n++;
// Decoder may miscorrect beyond its radius: reference tests explicitly demonstrate this.
const result={revision:102,date:'2026-11-08',mathematicalChecks:math.checked,integrationChecks:n,sessionScenarios:rows.length,tests:'PASS',limits:['No prueba hardware','Fuera del radio puede haber corrección equivocada; CRC no infalible','No certifica equivalencia al caso de clase'],slowSweep:slow,scenarios:rows};
fs.writeFileSync(path.join(__dirname,'resultados-integracion.json'),JSON.stringify(result,null,2)+'\n');
const example=E.simulate({a:'Hola',outages:[{mask:3,on:'mid',duration:120}]});
fs.writeFileSync(path.join(__dirname,'ejemplo-corte-dos-medios.json'),JSON.stringify(example,null,2)+'\n');
console.log(JSON.stringify({math:math.checked,integration:n,sessions:rows.length,tests:'PASS',slow}));
