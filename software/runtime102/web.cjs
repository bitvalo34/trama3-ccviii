#!/usr/bin/env node
'use strict';
const http=require('node:http');
const {simulate}=require('./virtual.cjs');
const page=`<!doctype html><html lang="es"><meta charset="utf-8"><title>TRAMA3 — banco de chat</title>
<style>body{font:17px system-ui;max-width:850px;margin:40px auto;padding:20px;background:#101827;color:#eee}textarea,select,button{font:inherit;padding:10px;margin:8px 0}textarea{display:block;width:95%}pre{white-space:pre-wrap;background:#1e293b;padding:20px}button{cursor:pointer}</style>
<h1>TRAMA3 · Chat de prueba</h1><p>SIMULACIÓN LOCAL · No conectado a las BeagleBone. El tiempo mostrado es virtual.</p>
<label>A envía<textarea id="a" maxlength="1024">Hola</textarea></label>
<label>B envía<textarea id="b" maxlength="1024">Respuesta</textarea></label>
<label>CRC <select id="crc"><option>SMBUS</option><option>AUTOSAR</option><option>SAE-J1850</option><option>MAXIM-DOW</option></select></label>
<button id="send">Probar intercambio</button><button id="save" disabled>Descargar registro</button><pre id="out">Listo.</pre>
<script>let result;const el=id=>document.getElementById(id);el('send').onclick=async()=>{el('send').disabled=true;el('save').disabled=true;el('out').textContent='Ejecutando...';try{const r=await fetch('/simulate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({a:el('a').value,b:el('b').value,crc:el('crc').value})});result=await r.json();if(!r.ok)throw Error(result.error);el('out').textContent=JSON.stringify({status:result.status,physical_status:result.physical_status,segundos_virtuales:result.seconds,A_recibio:result.deliveries[0],B_recibio:result.deliveries[1],estadisticas:result.stats},null,2);el('save').disabled=false;}catch(e){el('out').textContent=e.message;}finally{el('send').disabled=false;}};el('save').onclick=()=>{const u=URL.createObjectURL(new Blob([JSON.stringify(result,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=u;a.download='trama3-simulacion.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);};</script></html>`;
function server(){return http.createServer((req,res)=>{
 res.setHeader('Cache-Control','no-store');res.setHeader('X-Content-Type-Options','nosniff');
 if(req.method==='GET'&&req.url==='/'){res.setHeader('Content-Type','text/html; charset=utf-8');res.end(page);return;}
 if(req.method!=='POST'||req.url!=='/simulate'){res.writeHead(404);res.end();return;}
 let body='',bytes=0;req.on('data',chunk=>{bytes+=chunk.length;if(bytes>16384){res.writeHead(413);res.end();req.destroy();return;}body+=chunk;});
 req.on('end',()=>{if(res.writableEnded)return;res.setHeader('Content-Type','application/json; charset=utf-8');try{
  const o=JSON.parse(body);if(typeof o.a!=='string'||typeof o.b!=='string'||o.a.length>1024||o.b.length>1024)throw Error('Mensajes invalidos');
  res.end(JSON.stringify(simulate({a:o.a,b:o.b,crc:o.crc})));
 }catch(e){res.statusCode=400;res.end(JSON.stringify({error:e.message}));}});
});}
if(require.main===module)server().listen(8080,'127.0.0.1',()=>console.log('Simulacion local: http://127.0.0.1:8080'));
module.exports={server};
