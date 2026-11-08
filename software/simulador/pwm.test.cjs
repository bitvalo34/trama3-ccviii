'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),M=require('./engine');
function physical(f,map,report=7,{T=1,flip=-1,skew=0,jitter=0,omit=-1,extra=-1,rows=null}={}){
 const r=new M.PhysicalReceiver(T,f.algorithm),words=M.clockControl(map,report),data=rows||M.layout(f.bits,map);
 data.forEach((values,k)=>{
  let code=k===0?'S':k<=17?words[k-1]:'0';
  if(k===flip)code=code==='0'?'1':'0';
  if(k===omit)return;
  const rise=k*T+((k%2)?jitter:-jitter),fall=rise+M.pulseWidth(code,T)+skew;
  r.ingest({rise,fall,values,extra:k===extra});
 });return r;
}
test('Todos los mapas y reportes: control de 17 bits, CRC y versiones',()=>{
 for(let map=0;map<8;map++)for(let report=0;report<8;report++){
  const raw=M.clockControl(map,report);assert.equal(raw.length,17);assert.deepEqual(M.readClock(raw),{map,report});
  for(let i=0;i<17;i++)assert.equal(M.readClock(raw.slice(0,i)+(raw[i]==='0'?'1':'0')+raw.slice(i+1)),null);
 }
 assert.equal(M.readClock(M.clockControl(7,7,3)),null);
});
test('Los cuatro CRC y 256 bytes llegan en 18/27/54 pulsos sin prefijo',()=>{
 for(const crc of Object.keys(M.CRCS))for(let b=0;b<256;b++)for(let map=1;map<8;map++){
  const f=M.frame('DATA',b,3,1,crc),r=physical(f,map);
  assert.equal(r.outcome().ok,true);assert.equal(r.outcome().data,b);
  assert.equal(r.rows.length,54/[0,1,2].filter(i=>map&(1<<i)).length);
  assert.equal(r.outcome().raw,f.bits);
 }
});
test('RX aprende el mapa del reloj y retiene muestras previas a recibirlo',()=>{
 const f=M.frame('DATA',65),r=new M.PhysicalReceiver(1),rows=M.layout(f.bits,6),word=M.clockControl(6,4);
 rows.forEach((values,k)=>{
  r.ingest({rise:k,fall:k+M.pulseWidth(k===0?'S':k<=17?word[k-1]:'0',1),values});
  if(k<17)assert.equal(r.meta,null);
 });
 assert.deepEqual(r.meta,{map:6,report:4,seen:7});assert.equal(r.outcome().raw,f.bits);
});
test('Pulsos dudosos, CRC de reloj, inicio, relleno, faltantes y extras se rechazan',()=>{
 const f=M.frame('DATA',65);
 for(let k=1;k<=17;k++)assert.equal(physical(f,7,7,{flip:k}).outcome().ok,false);
 for(let k=0;k<54;k++){
  assert.equal(physical(f,4,7,{omit:k}).outcome().ok,false);
  assert.equal(physical(f,4,7,{extra:k}).outcome().ok,false);
 }
 assert.equal(physical(f,4,7,{flip:19}).outcome().reason,'PWM_TAIL');
 assert.equal(physical(f,7,7,{skew:.1}).outcome().ok,false);
});
test('Tolerancia del pulso y del período en los extremos',()=>{
 for(const T of [1,.5,1/3,.25]){
  for(const symbol of ['S','0','1']){
   const w=M.pulseWidth(symbol,T);
   for(const offset of [-.05,0,.05])assert.equal(M.decodePulse(0,w+offset*T,T),symbol);
   assert.equal(M.decodePulse(0,w+.051*T,T),null);
  }
  assert.equal(physical(M.frame('DATA',65),7,7,{T,skew:.049*T,jitter:.024*T}).outcome().ok,true);
  assert.equal(physical(M.frame('DATA',65),7,7,{T,jitter:.026*T}).outcome().ok,false);
 }
});
test('Al recuperarse el reloj se busca un inicio tras guarda; no se empalman intentos',()=>{
 const f=M.frame('DATA',65),r=physical(f,7,7,{omit:7}),word=M.clockControl(7,7);
 assert.equal(r.outcome().ok,false);
 M.layout(f.bits,7).forEach((values,k)=>r.ingest({rise:25+k,fall:25+k+M.pulseWidth(k===0?'S':word[k-1],1),values}));
 assert.equal(r.outcome().ok,true);
});
test('Cada error PWM inyectado produce recuperación sin doble entrega',()=>{
 for(const scenario of ['pwm-bit','pwm-width','pwm-start','clock-skew','clock-period','truncated']){
  const r=M.simulate({a:'Hola',scenario});assert.equal(r.status,'COMPLETE',scenario);
  assert.equal(r.stats.retries,1,scenario);assert.equal(r.deliveries[0].text,'Hola');
 }
 const r=M.simulate({a:'Hola',scenario:'pwm-tail',outages:[{mask:3}]});
 assert.equal(r.status,'COMPLETE');assert.equal(r.stats.retries,1);
});
test('Tres medios cortados impiden entregar texto aunque el control de reloj llegue',()=>{
 const r=M.simulate({a:'Hola',outages:[{mask:7}]});
 assert.equal(r.status,'RECOVERY_1HZ');assert.equal(r.deliveries.length,0);
 assert.ok(r.events.some(e=>e.kind==='CLOCK_CONTROL'&&e.seen===0));
});
test('Variar el ancho no cambia el período ni agrega los antiguos ciclos de prefijo',()=>{
 const r=M.simulate({a:'Hola'});
 assert.equal(r.duration,832);assert.equal(r.stats.retries,0);
 for(const f of r.events.filter(e=>e.kind==='TX')){
  assert.equal(f.bits.length,54);assert.equal(f.prefixCycles,0);
  const pulses=r.events.filter(e=>e.kind==='CLOCK_PWM'&&e.id===f.id);
  assert.equal(pulses.length,f.cycles);
  pulses.slice(1).forEach((p,i)=>assert.ok(Math.abs(p.rise-pulses[i].rise-f.T)<1e-8));
 }
});
test('Umbral virtual del opto y jitter controlados; nunca declara éxito con control inválido',()=>{
 let r=M.simulate({a:'Hola',hz:4,clockFallMs:20});assert.notEqual(r.status,'COMPLETE');assert.equal(r.deliveries.length,0);
 r=M.simulate({a:'Hola',hz:2,clockRiseMs:0.018,clockFallMs:0.018,clockJitterMs:1});
 assert.equal(r.status,'COMPLETE');assert.equal(r.deliveries[0].text,'Hola');
});
