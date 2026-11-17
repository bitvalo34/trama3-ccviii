'use strict';
const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const {ChatSession,NodeChat}=require('./chat-session.cjs');
const {launch}=require('./launcher.cjs');
const P=require('./protocol.cjs');

function events(log,query){
  let before=+query.get('before')||Infinity;
  if(before!==Infinity&&(!Number.isSafeInteger(before)||before<0))throw Error('CURSOR');
  const type=query.get('type'),filter=query.get('filter');
  const lines=log.toString('utf8').trimEnd().split('\n'),entries=[];
  for(let i=Math.min(lines.length,before)-1;i>=0;i--){
    const e=JSON.parse(lines[i]);
    if(['CAPTURE','OUTPUT_PREPARED','MATRIX_BLOCK'].includes(e.kind))continue;
    if(type&&e.type!==type)continue;
    if(filter==='ack'&&!['ACK','NACK'].includes(e.type)&&e.kind!=='NACK_CONTEXT')continue;
    if(filter==='retry'&&!(e.kind==='ATTEMPT'&&e.attempt>1))continue;
    if(filter==='error'&&!['RX_REJECT','FAULT','CLOCK_GAP','TIMEOUT','START_FAILED','HOST_DIAGNOSTIC','OWNER_DIAGNOSTIC'].includes(e.kind)&&!e.source&&!e.errors?.length)continue;
    if(entries.length===100)return {entries,before:entries.at(-1).record};
    entries.push(e);
  }
  return {entries,before:null};
}
function server({directory,crc='SMBUS',encoding='utf-8',fault='none',runId,session=new ChatSession({directory,crc,encoding,fault,runId})}={}){
  const page=fs.readFileSync(path.join(__dirname,'node-chat.html'));
  const s=http.createServer((req,res)=>{
    res.setHeader('Cache-Control','no-store');res.setHeader('X-Content-Type-Options','nosniff');
    const host='127.0.0.1:'+s.address().port;
    if(req.headers.host!==host&&req.headers.host!=='localhost:'+s.address().port){res.writeHead(403);res.end();return;}
    if(req.headers.origin&&!['http://'+host,'http://localhost:'+s.address().port].includes(req.headers.origin)){res.writeHead(403);res.end();return;}
    const json=(status,value)=>{res.writeHead(status,{'Content-Type':'application/json; charset=utf-8'});res.end(JSON.stringify(value));};
    try{
      const url=new URL(req.url,'http://'+host),node=url.searchParams.get('node')||undefined;
      session.index(node);
      if(req.method==='GET'&&url.pathname==='/'){res.setHeader('Content-Type','text/html; charset=utf-8');res.end(page);return;}
      if(req.method==='GET'&&url.pathname==='/state'){json(200,session.snapshot(node));return;}
      if(req.method==='GET'&&url.pathname==='/log'){
        const record=session.log(node),name=session.snapshot(node).node;
        res.setHeader('Content-Type','application/x-ndjson');
        res.setHeader('Content-Disposition','attachment; filename="'+name+'.jsonl"');res.end(record);return;
      }
      if(req.method==='GET'&&url.pathname==='/events'){json(200,events(session.log(node),url.searchParams));return;}
      if(req.method!=='POST'||url.pathname!=='/send'){res.writeHead(404);res.end();return;}
      const chunks=[];let bytes=0;
      req.on('data',chunk=>{
        if(res.writableEnded)return;
        bytes+=chunk.length;
        if(bytes>8192){json(413,{error:'REQUEST_TOO_LARGE'});return;}
        chunks.push(chunk);
      });
      req.on('end',()=>{if(res.writableEnded)return;try{
        const id=session.send(node,JSON.parse(Buffer.concat(chunks).toString('utf8')).text);
        json(202,{id});
      }catch(e){json(e.message==='NOT_READY'?409:400,{error:e.message});}});
    }catch(e){json(400,{error:e.message});}
  });
  s.session=session;return s;
}
async function main(args){
  let session,s,stopping=false;
  const stop=async()=>{
    if(stopping)return;
    stopping=true;
    if(s?.listening)s.close();
    if(session){
      const result=await session.stop();
      if(result.errors?.length||result.cleanup?.some(c=>c.errors.length)){
        console.error(JSON.stringify(result));process.exitCode=1;
      }
    }
  };
  const onSignal=()=>void stop().catch(error=>{console.error(error.message);process.exitCode=1;});
  process.once('SIGINT',onSignal);process.once('SIGTERM',onSignal);
  try{
    if(args[0]==='hardware'){
      const [,profileFile,directory,firmware,host,runId,...flags]=args;
      const flag=(name,fallback)=>flags.find(value=>value.startsWith(name+'='))?.slice(name.length+1)??fallback;
      if(!runId||!host||flags.some(x=>!['--coordinator','--electrical-checked'].includes(x)&&!/^--(crc|encoding|port)=/.test(x)))
        throw Error('hardware PERFIL NUEVO_DIR FIRMWARE HOST ID --electrical-checked [--coordinator] [--crc=SMBUS] [--encoding=utf-8] [--port=8081]');
      const crc=flag('--crc','SMBUS'),encoding=flag('--encoding','utf-8'),port=Number(flag('--port','8081'));
      if(!Object.keys(P.CRCS).includes(crc)||!['utf-8','windows-1252'].includes(encoding)||
        !Number.isInteger(port)||port<1024||port>65535)throw Error('SESSION_CONFIG');
      const chat=new NodeChat(directory);
      chat.attach(await launch({mode:'hardware',profileFile,directory,firmware,host,runId,crc,encoding,
        electricalChecked:flags.includes('--electrical-checked'),coordinator:flags.includes('--coordinator'),
        onRecord:event=>chat.event(event)}));
      session=chat;
      if(stopping){await session.stop();return;}
      s=server({session});
      await listen(port);
    }else{
      const [directory,crc,encoding,fault]=args[0]==='simulation'?args.slice(1):args;
      if(!directory)throw Error('simulation NUEVO_DIR [SMBUS|AUTOSAR|SAE-J1850|MAXIM-DOW] [utf-8|windows-1252] [fallo]');
      s=server({directory,crc,encoding,fault,runId:path.basename(path.resolve(directory))});
      session=s.session;
      void session.result.catch(error=>{console.error(error.message);process.exitCode=1;onSignal();});
      await listen(8081);
    }
  }catch(error){await stop();throw error;}
  function listen(port){
    return new Promise((resolve,reject)=>{
      s.once('error',reject);
      s.listen(port,'127.0.0.1',()=>{
        const {node,origin}=session.snapshot();
        console.log((origin==='hardware'?'HARDWARE · BBB-'+node:'SIMULACIÓN — NO TRANSMISIÓN FÍSICA')+
          ' · http://127.0.0.1:'+port);
        resolve();
      });
    });
  }
}
if(require.main===module)main(process.argv.slice(2)).catch(error=>{console.error(error.message);process.exitCode=1;});
module.exports={server};
