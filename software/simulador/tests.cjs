'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const M=require('./engine.js');
test('Cuatro CRC contra vectores de referencia, incluido AUTOSAR oficial',()=>{
  for(const [name,p]of Object.entries(M.CRCS))assert.equal(M.crc8(M.encode('123456789'),name),p.check,name);
  assert.equal(M.crc8([0,0,0,0],'SAE-J1850'),0x59);
  assert.equal(M.crc8([0xf2,1,0x83],'SAE-J1850'),0x37);
  assert.equal(M.crc8([4,0x41,3,1]),0x8d);
});
test('256 bytes × 4 CRC: 54 bits, 18 tripletas, campos cruzados y todo error simple del cuerpo',()=>{
  for(const name of Object.keys(M.CRCS))for(let b=0;b<256;b++){
    const f=M.frame('DATA',b,b,1,name);assert.equal(f.bits.length,54);assert.equal(f.symbols.length,18);
    assert.equal(f.symbols.join(''),f.bits);assert.equal(parseInt(f.bits.slice(22,30),2),b);
    assert.equal(M.parse(f.bits,name).data,b);
    for(let i=18;i<54;i++){
      const raw=f.bits.slice(0,i)+(f.bits[i]==='1'?'0':'1')+f.bits.slice(i+1);
      assert.equal(M.parse(raw,name).ok,false,`${name} byte=${b} posición=${i}`);
    }
  }
});
test('SYN/SFD dañados y reloj ausente se rechazan antes del CRC',()=>{
  const f=M.frame('DATA',0x41);
  for(let i=0;i<18;i++)assert.equal(M.parse(f.bits.slice(0,i)+(f.bits[i]==='1'?'0':'1')+f.bits.slice(i+1)).reason,'SYNC');
  assert.equal(M.parse(f.bits.slice(3)).reason,'CLOCK_OR_LENGTH');
});
test('UTF-8 de 1,2,3,4 bytes y CP1252 estricta',()=>{
  for(const [s,n]of [['A',1],['ñ',2],['€',3],['🙂',4]]){assert.equal(M.encode(s).length,n);assert.equal(M.decode(M.encode(s)),s);}
  assert.equal(M.decode(M.encode('niño €','windows-1252'),'windows-1252'),'niño €');
  assert.throws(()=>M.encode('🙂','windows-1252'));
  assert.throws(()=>M.encode('\ud800'));
  assert.throws(()=>M.decode([0xc3,0x28]));
  assert.throws(()=>M.decode([0x81],'windows-1252'));
});
test('Fragmentos de período completos, duplicados y q inválido',()=>{
  for(const T of [1000000,500000,250000]){
    const p=new M.Parts(1);const parts=M.periodParts(T);p.add(1,parts[0]);assert.equal(p.value(),null);
    for(const b of parts)p.add(1,b);assert.equal(p.value(),T);p.add(1,parts[0]);assert.equal(p.value(),T);
    p.add(2,parts[0]);assert.equal(p.value(),null);
  }
  const p=new M.Parts(1);p.add(1,0);p.add(1,1);assert.equal(p.value(),null);
});
test('Limpio bidireccional con todos los CRC y codificaciones',()=>{
  for(const crc of Object.keys(M.CRCS))for(const encoding of ['utf-8','windows-1252']){
    const a=encoding==='utf-8'?'Añ€🙂':'Añ€';const r=M.simulate({a,b:'B',crc,encoding});
    assert.equal(r.status,'COMPLETE');assert.deepEqual(r.deliveries.map(d=>d.text).sort(),[a,'B'].sort());
    assert.equal(r.stats.crcErrors,0);assert.equal(r.stats.retries,0);
  }
});
test('Bit alterado provoca CRC → NACK → reintento → ACK sin duplicados',()=>{
  const r=M.simulate({a:'A',scenario:'crc'});assert.equal(r.status,'COMPLETE');
  assert.equal(r.stats.crcErrors,1);assert.equal(r.stats.retries,1);assert.equal(r.deliveries.length,1);
  for(const kind of ['NACK_CONTEXT','NACK','CONFIRMED'])assert.ok(r.events.some(e=>e.kind===kind));
});
test('ACK perdido: timeout y deduplicación sin duplicar bytes ni mensaje',()=>{
  const r=M.simulate({a:'A',b:'B',scenario:'ack'});assert.equal(r.status,'COMPLETE');
  assert.equal(r.stats.duplicates,1);assert.equal(r.stats.retries,1);assert.equal(r.stats.bytes,2);
  assert.equal(r.deliveries.length,2);assert.ok(r.events.some(e=>e.kind==='TIMEOUT'));
});
test('Reloj perdido: error explícito y recuperación por timeout',()=>{
  const r=M.simulate({scenario:'clock'});assert.equal(r.status,'COMPLETE');
  assert.equal(r.stats.clockErrors,1);assert.equal(r.stats.retries,1);
});
test('Bloqueo de nylon en DATA cambia a luz y sonido y entrega una sola vez',()=>{
  const r=M.simulate({scenario:'blocked'});assert.equal(r.status,'COMPLETE');
  assert.equal(r.deliveries[0].text,'A');assert.equal(r.stats.retries,1);
  assert.deepEqual(r.events.filter(e=>e.kind==='TX'&&e.type==='DATA').map(e=>[e.seq,e.map,e.cycles]),[[3,7,18],[3,3,27]]);
});
test('Cambio previo al mensaje: 1→4 Hz, todos los CRC y pérdidas de gestión',()=>{
  for(const crc of Object.keys(M.CRCS))for(const scenario of ['clean','rate-ready','rate-active','rate-part']){
    const r=M.simulate({hz:4,crc,scenario});assert.equal(r.status,'COMPLETE',crc+' '+scenario);
    assert.equal(r.deliveries[0].text,'A');assert.ok(r.events.some(e=>e.kind==='RATE_ACTIVE_B'));
    const data=r.events.filter(e=>e.kind==='TX'&&e.type==='DATA');assert.ok(data.every(e=>e.T===0.25));
  }
});
test('Nylon tardío se excluye a 4 Hz por su cabecera ilegible',()=>{
  const r=M.simulate({hz:4,mechanicalMs:300,captureMs:200});
  assert.equal(r.status,'COMPLETE');assert.equal(r.deliveries[0].text,'A');
  assert.ok(r.events.filter(e=>e.kind==='TX'&&e.type==='DATA').every(e=>e.map===3&&e.T===0.25));
});
test('SEQ da vuelta sin confundir bytes repetidos con duplicados',()=>{
  const r=M.simulate({a:'A'.repeat(300)});assert.equal(r.status,'COMPLETE');
  assert.equal(r.deliveries[0].text,'A'.repeat(300));assert.equal(r.stats.duplicates,0);
});
test('Modelo reproducible, validaciones de entrada y límite de mensaje',()=>{
  assert.deepEqual(M.simulate({ber:0.001,seed:42}),M.simulate({ber:0.001,seed:42}));
  assert.throws(()=>M.simulate({a:'x'.repeat(1025)}));assert.throws(()=>M.simulate({hz:1000}));
  assert.throws(()=>M.simulate({ber:NaN}));assert.throws(()=>M.simulate({readyMs:20}));
});
