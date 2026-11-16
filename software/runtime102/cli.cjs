#!/usr/bin/env node
'use strict';
const fs=require('node:fs');
const {simulate}=require('./virtual.cjs');
const {StreamDecoder}=require('./stream.cjs');
const [mode,arg='Hola',other='']=process.argv.slice(2);
if(mode==='simulate'){
  const r=simulate({a:arg,b:other});console.log(JSON.stringify(r,null,2));process.exitCode=r.status==='PASS'?0:1;
}else if(mode==='replay'){
  const frames=[],faults=[];const rx=new StreamDecoder({onFrame:raw=>frames.push(raw),onFault:r=>faults.push(r)});
  for(const line of fs.readFileSync(arg,'utf8').split(/\r?\n/).filter(Boolean))rx.ingest(JSON.parse(line));
  console.log(JSON.stringify({origin:'replay',physical_status:'NOT_TESTED',frames,faults},null,2));process.exitCode=faults.length||!frames.length?1:0;
}else {console.error('node cli.cjs simulate [textoA] [textoB] | replay eventos.jsonl');process.exitCode=2;}
