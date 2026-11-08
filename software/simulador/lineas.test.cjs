'use strict';
const test=require('node:test'), assert=require('node:assert/strict'), M=require('./engine');
const tx=(r,type='DATA')=>r.events.filter(e=>e.kind==='TX'&&e.type===type);
const maps=r=>r.events.filter(e=>e.kind==='LINE_CHANGE');
const cut=(mask,dir=0,on='start',duration=0)=>({mask,dir,on,duration});
function delivered(r,messages){assert.equal(r.status,'COMPLETE',r.reason);assert.deepEqual(r.deliveries.map(x=>x.text).sort(),messages.sort());}
test('64 combinaciones independientes de medios de ida y de vuelta, desde HELLO',()=>{
 for(let a=0;a<8;a++)for(let b=0;b<8;b++){
  const outages=[a&&cut(a),b&&cut(b,1)].filter(Boolean),r=M.simulate({a:'Hola',b:'Adiós',outages});
  if(a===7||b===7){assert.equal(r.status,'RECOVERY_1HZ');assert.equal(r.deliveries.length,0);continue;}
  delivered(r,['Hola','Adiós']);
  for(const f of tx(r)){
   assert.equal(f.map,7^(f.dir?b:a));const s=r.events.filter(e=>e.kind==='SYMBOL'&&e.id===f.id);
   assert.deepEqual(s.flatMap(e=>e.positions.filter(x=>x!==null)),Array.from({length:54},(_,i)=>i));
   assert.equal(s.map(e=>e.positions.map((v,j)=>v===null?'':e.rx[j]).join('')).join(''),f.bits);
  }
 }
});
test('Los seis cortes parciales antes y durante DATA en ambos sentidos; bloqueo fijo alto o bajo',()=>{
 for(let m=1;m<7;m++)for(const on of ['data','mid'])for(const dir of [0,1])for(const level of [0,1]){
   const r=M.simulate({a:'Hola',b:'Adiós',outages:[{...cut(m,dir,on),level}]});
   delivered(r,['Hola','Adiós']);assert.ok(maps(r).some(e=>e.dir===dir&&e.map===(7^m)));
   assert.ok(r.events.filter(e=>e.kind==='ATTEMPT').every(e=>e.attempt<=4));
 }
});
test('Recuperación temporal y escalonada sin mezclar copias ni entregar bytes dos veces',()=>{
 const r=M.simulate({a:'Hola',outages:[cut(3,0,'mid',360)]});delivered(r,['Hola']);
 assert.deepEqual(maps(r).map(e=>e.map),[4,7]);assert.equal(r.stats.bytes,4);
 const d=tx(r).filter(e=>e.seq===3);assert.ok(d.length>=2);assert.equal(new Set(d.map(e=>e.bits)).size,1);
 const s=M.simulate({a:'Hola mundo',outages:[{...cut(1),at:600,duration:1000},{...cut(2),at:900,duration:1100}]});
 delivered(s,['Hola mundo']);assert.ok(maps(s).some(e=>e.map===4));
});
test('Pérdida total temporal vuelve si se recupera dentro de los intentos; permanente es acotada',()=>{
 let r=M.simulate({a:'Hola',outages:[cut(7,0,'data',180)]});delivered(r,['Hola']);
 for(const o of [cut(7,0,'data'),{...cut(0,0,'data'),clock:true},{...cut(0,0,'mid'),clock:true}]){
   r=M.simulate({a:'Hola',outages:[o]});assert.equal(r.status,'LINK_FAULT');assert.equal(r.deliveries.length,0);
   assert.equal(r.events.filter(e=>e.kind==='ATTEMPT'&&e.type==='DATA').length,4);
 }
});
test('Retorno perdido después de END: emisor incierto, receptor entrega exactamente una vez',()=>{
 const base=M.simulate({a:'A'});const end=tx(base,'END')[0];
 const r=M.simulate({a:'A',outages:[{...cut(7,1),at:end.t}]});
 assert.equal(r.status,'LINK_FAULT');assert.equal(r.deliveries.length,1);assert.ok(r.stats.duplicates>=1);
});
test('Bajada en pleno mensaje, sin resetear intentos, con tráfico inverso',()=>{
 for(const hz of [2,3,4]){const r=M.simulate({a:'Hola',b:'Adiós',hz,scenario:'fallback'});delivered(r,['Hola','Adiós']);
 const same=tx(r).filter(e=>e.dir===0&&e.seq===3);assert.equal(same.length,3);assert.equal(new Set(same.map(e=>e.bits)).size,1);
 assert.ok(Math.abs(same[2].T-1/(hz-1))<0.000001);assert.equal(r.stats.retries,2);}
});
test('Cabecera, reloj, READY, ACK de otro SID/SEQ, ACK final y sensores',()=>{
 for(const scenario of ['prefix','extra-clock','ready','stale','wrong-seq','ack-end','sound','switch']){
  const r=M.simulate({a:'Hola',scenario});delivered(r,['Hola']);
  if(['stale','wrong-seq'].includes(scenario))assert.ok(r.events.some(e=>e.kind==='REPLY_IGNORED'));
  if(scenario==='ack-end')assert.equal(r.stats.duplicates,1);
 }
});
test('Versión, perfil rechazado y reinicio con nueva sesión sin reenvío implícito',()=>{
 for(const scenario of ['version','rate-reject','reset']){
 const r=M.simulate({a:'Hola',scenario,hz:2});assert.equal(r.status,scenario==='reset'?'SESSION_LOST':'RECOVERY_1HZ');
 assert.equal(r.deliveries.length,0);
 if(scenario==='reset')assert.deepEqual(tx(r,'HELLO').map(e=>e.sid),[1,2]);}
 assert.throws(()=>M.simulate({outages:[{mask:8}]}));assert.throws(()=>M.simulate({outages:[{mask:1,duration:-1}]}));
});
