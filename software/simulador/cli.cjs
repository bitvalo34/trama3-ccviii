#!/usr/bin/env node
'use strict';
const fs=require('node:fs');
const {simulate}=require('./engine.js');
const options={}, argv=process.argv.slice(2);let out;
const keys={'--a':'a','--b':'b','--scenario':'scenario','--crc':'crc','--encoding':'encoding',
  '--outages':'outages','--hz':'hz','--hz-a':'hzA','--hz-b':'hzB','--seed':'seed','--ber':'ber','--mechanical-ms':'mechanicalMs','--clock-rise-ms':'clockRiseMs','--clock-fall-ms':'clockFallMs','--clock-jitter-ms':'clockJitterMs'};
try {
  for(let i=0;i<argv.length;i++){
    if(argv[i]==='--help'){console.log('node cli.cjs [--a "A"] [--b "B"] [--scenario clean|crc|ack|clock|pwm-bit|pwm-width|pwm-start|pwm-tail|clock-skew|clock-period|truncated|fallback] [--hz 1|2|3|4] [--hz-a 1|2|3|4] [--hz-b 1|2|3|4] [--crc SMBUS|AUTOSAR|SAE-J1850|MAXIM-DOW] [--encoding utf-8|windows-1252] [--outages JSON] [--seed 23004161] [--ber 0.001] [--mechanical-ms 120] [--clock-rise-ms 0] [--clock-fall-ms 0] [--clock-jitter-ms 0] [--out log.json]');process.exit(0);}
    if(argv[i]==='--out'){out=argv[++i];if(!out)throw Error('Falta ruta para --out');continue;}
    const k=keys[argv[i]];if(!k||i+1>=argv.length)throw Error('Argumento inválido: '+argv[i]);
    const v=argv[++i];options[k]=k==='outages'?JSON.parse(v):['hz','hzA','hzB','seed','ber','mechanicalMs','clockRiseMs','clockFallMs','clockJitterMs'].includes(k)?Number(v):v;
  }
  const r=simulate(options);
  for(const e of r.events)if(!['SYMBOL','CLOCK_PWM'].includes(e.kind))console.log(`${e.t.toFixed(3).padStart(10)} s | ${e.dir===undefined?'---':e.dir?'B→A':'A→B'} | ${e.kind.padEnd(16)} | ${e.type||''} ${e.seq===undefined?'':'SEQ='+e.seq} ${e.detail||e.reason||''}`);
  console.log(JSON.stringify({status:r.status,duration:r.duration,stats:r.stats,deliveries:r.deliveries},null,2));
  if(out){fs.writeFileSync(out,JSON.stringify(r,null,2),'utf8');console.log('Log completo: '+out);}
  if(r.status!=='COMPLETE')process.exitCode=2;
}catch(e){console.error(e.message);process.exitCode=1;}
