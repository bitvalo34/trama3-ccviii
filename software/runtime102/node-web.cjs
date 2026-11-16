'use strict';
const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const {ChatSession}=require('./chat-session.cjs');
function server({directory,crc='SMBUS',encoding='utf-8',fault='none'}={}){
  const session=new ChatSession({directory,crc,encoding,fault});
  const page=fs.readFileSync(path.join(__dirname,'node-chat.html'));
  const s=http.createServer((req,res)=>{
    res.setHeader('Cache-Control','no-store');res.setHeader('X-Content-Type-Options','nosniff');
    const host='127.0.0.1:'+s.address().port;
    if(req.headers.host!==host&&req.headers.host!=='localhost:'+s.address().port){res.writeHead(403);res.end();return;}
    if(req.headers.origin&&!['http://'+host,'http://localhost:'+s.address().port].includes(req.headers.origin)){res.writeHead(403);res.end();return;}
    const url=new URL(req.url,'http://'+host),node=url.searchParams.get('node')||'A';
    try{
      session.index(node);
      if(req.method==='GET'&&url.pathname==='/'){res.setHeader('Content-Type','text/html; charset=utf-8');res.end(page);return;}
      if(req.method==='GET'&&url.pathname==='/state'){res.setHeader('Content-Type','application/json');res.end(JSON.stringify(session.snapshot(node)));return;}
      if(req.method==='GET'&&url.pathname==='/log'){res.setHeader('Content-Type','application/x-ndjson');res.setHeader('Content-Disposition','attachment; filename="'+node+'.jsonl"');res.end(session.log(node));return;}
      if(req.method!=='POST'||url.pathname!=='/send'){res.writeHead(404);res.end();return;}
      let body='',bytes=0;
      req.on('data',chunk=>{bytes+=chunk.length;if(bytes>8192){res.writeHead(413);res.end();req.destroy();return;}body+=chunk;});
      req.on('end',()=>{if(res.writableEnded)return;try{
        const id=session.send(node,JSON.parse(body).text);res.writeHead(202,{'Content-Type':'application/json'});res.end(JSON.stringify({id}));
      }catch(e){res.writeHead(400,{'Content-Type':'application/json'});res.end(JSON.stringify({error:e.message}));}});
    }catch(e){res.writeHead(400);res.end(JSON.stringify({error:e.message}));}
  });
  s.session=session;return s;
}
if(require.main===module){
  const directory=process.argv[2];if(!directory)throw Error('Usage: node node-web.cjs NEW_DIRECTORY [CRC] [encoding] [fault]');
  const s=server({directory,crc:process.argv[3],encoding:process.argv[4],fault:process.argv[5]});
  s.listen(8081,'127.0.0.1',()=>console.log('Simulacion supervisada: http://127.0.0.1:8081/?node=A y /?node=B'));
  const stop=async()=>{await s.session.stop();s.close();};process.once('SIGINT',stop);process.once('SIGTERM',stop);
}
module.exports={server};
