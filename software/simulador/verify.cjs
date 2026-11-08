'use strict';
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const M=require('./engine.js');const dest=path.join(__dirname,'evidencias');fs.mkdirSync(dest,{recursive:true});
const test=cp.spawnSync(process.execPath,['--test','tests.cjs','tests_ui.cjs','lineas.test.cjs','pwm.test.cjs','direcciones.test.cjs'],{cwd:__dirname,encoding:'utf8'});
fs.writeFileSync(path.join(dest,'pruebas_motor.txt'),test.stdout+test.stderr,'utf8');
if(test.status!==0){process.stderr.write(test.stdout+test.stderr);process.exit(test.status||1);}
const cases=[{a:'Hola',b:'B',hzA:1,hzB:4},{a:'Hola',b:'B',hzA:4,hzB:1},{a:'Hola',b:'B',hzA:4,hzB:2,scenario:'fallback'},...['pwm-bit','pwm-width','pwm-start','pwm-tail','clock-skew','clock-period','truncated','extra-clock'].map(scenario=>({a:'A',scenario})),...['clean','crc','ack','clock','blocked'].map(scenario=>({a:'A',hz:1,scenario})),
 ...['clean','rate-part','rate-ready','rate-active'].map(scenario=>({a:'A',hz:4,scenario})),
 {a:'A',hz:4,mechanicalMs:300},{a:'A',hz:2,mechanicalMs:300},
 {a:'AÃ±â‚¬ðŸ™‚',b:'B',hz:1,crc:'MAXIM-DOW'}, ...[
 {mask:1,on:'start'},{mask:3,on:'start'},{mask:3,on:'mid',duration:120},{mask:7,on:'data'}
 ].map(f=>({a:'Hola',outages:[f]})),{a:'Hola'},{a:'Hola',hz:4,scenario:'fallback'}];
const results=cases.map(c=>{const r=M.simulate(c);if(['crc','ack'].includes(c.scenario))fs.writeFileSync(path.join(dest,'log_'+c.scenario+'_1hz.json'),JSON.stringify(r,null,2));
 return {config:c,lineChanges:r.events.filter(e=>e.kind==='LINE_CHANGE'),status:r.status,virtualSeconds:r.duration,stats:r.stats,deliveries:r.deliveries};});
fs.writeFileSync(path.join(dest,'resultados_simulacion.json'),JSON.stringify({date:'2026-11-07',hardwareMeasured:false,results},null,2),'utf8');
console.log('Pruebas del motor aprobadas. Resultados y logs reproducibles en evidencias/.');
