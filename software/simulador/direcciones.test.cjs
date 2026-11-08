const test=require('node:test'),assert=require('node:assert/strict'),M=require('./engine.js');
test('16 pares de frecuencias y cuatro CRC con mensajes simultáneos',()=>{
 for(const hzA of [1,2,3,4])for(const hzB of [1,2,3,4])for(const crc of Object.keys(M.CRCS)){
 const r=M.simulate({a:'Hola',b:'B',hzA,hzB,crc});assert.equal(r.status,'COMPLETE',JSON.stringify({hzA,hzB,crc}));assert.equal(r.stats.retries,0);assert.equal(r.deliveries.length,2);
 for(const e of r.events.filter(e=>e.kind==='TX'&&e.type==='DATA'))assert.ok(Math.abs(e.T-1/(e.dir?hzB:hzA))<.000001);
 }});
test('ACK lento respeta el período del retorno, sin timeout prematuro',()=>{
 const r=M.simulate({a:'A',b:'B',hzA:4,hzB:1});
 assert.equal(r.status,'COMPLETE');assert.equal(r.stats.retries,0);
 for(const e of r.events.filter(e=>e.kind==='ACK_TIMER'))assert.equal(e.tau,e.dir?52:202);
 const loss=M.simulate({a:'A',hzA:4,hzB:1,scenario:'ack'});
 assert.equal(loss.status,'COMPLETE');assert.equal(loss.stats.duplicates,1);assert.equal(loss.stats.retries,1);
});
test('Bajada de A conserva la velocidad de B y la identidad del pendiente',()=>{
 const r=M.simulate({a:'Hola',b:'B',hzA:4,hzB:2,scenario:'fallback'});
 assert.equal(r.status,'COMPLETE');assert.deepEqual(r.finalPeriods,[.333334,.5]);
 const a=r.events.filter(e=>e.kind==='TX'&&e.type==='DATA'&&e.dir===0&&e.seq===3);
 assert.equal(new Set(a.map(e=>e.bits)).size,1);assert.equal(a.length,3);
});
test('Asimetría, cortes parciales y control corrupto no duplican entrega',()=>{
 for(const hzA of [1,4])for(const hzB of [1,4])for(const mask of [1,3,5,6]){
 const r=M.simulate({a:'A',b:'B',hzA,hzB,scenario:'pwm-bit',outages:[{dir:0,mask}]});
 assert.equal(r.status,'COMPLETE');assert.equal(r.deliveries.length,2);assert.equal(r.stats.bytes,2);
 }});
test('Negociación de B, pérdidas de gestión y parámetros inválidos',()=>{
 for(const scenario of ['rate-part','rate-ready','rate-active']){
 const r=M.simulate({a:'A',b:'B',hzA:1,hzB:4,scenario});assert.equal(r.status,'COMPLETE');assert.deepEqual(r.finalPeriods,[1,.25]);}
 assert.throws(()=>M.simulate({hzA:0}));assert.throws(()=>M.simulate({hzB:200}));
});
