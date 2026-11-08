'use strict';
const assert=require('node:assert/strict');
// Rows are ordered by tick then physical channel: C0,C1,C2.
const G=[[1,0],[0,1],[1,1],[0,1],[1,1],[1,0],[1,1],[1,0],[0,1]];
const encode=d=>G.map(r=>(r[0]&d[0])^(r[1]&d[1]));
const words=[[0,0],[0,1],[1,0],[1,1]].map(d=>({d,c:encode(d)}));
function decode(y) {
 if(y.length!==9||y.some(v=>v!==null&&v!==0&&v!==1))throw Error('Muestra inválida');
 const live=y.map((v,i)=>v===null?-1:i).filter(i=>i>=0);
 let distance=9;
 for(let a=0;a<4;a++)for(let b=a+1;b<4;b++)
  distance=Math.min(distance,live.filter(i=>words[a].c[i]!==words[b].c[i]).length);
 if(!distance)return {ok:false,reason:'RANK',distance};
 const candidates=words.map(w=>({...w,e:live.filter(i=>w.c[i]!==y[i]).length})).sort((a,b)=>a.e-b.e);
 const best=candidates[0];
 if(best.e===candidates[1].e||2*best.e>=distance)return {ok:false,reason:'SYNDROME',distance};
 return {ok:true,data:best.d,errors:best.e,distance, correctedPositions:live.filter(i=>best.c[i]!==y[i]), syndrome:live.length===9?G.slice(2).map((g,k)=>y[k+2]^(g[0]&y[0])^(g[1]&y[1])):null,
  status:best.e?'CORRECTED':live.length<9?'RECOVERED':'VALID'};
}
function crc(bytes) {let c=0;for(const b of bytes){c^=b;for(let i=0;i<8;i++)c=((c<<1)^((c&128)?7:0))&255;}return c;}
const bits=(x,n)=>x.toString(2).padStart(n,'0');
function frame(data,seq=0,sid=1){
 return '111000111000101010'+bits(4,4)+bits(data,8)+bits(crc([4,data,seq,sid]),8)+bits(seq,8)+bits(sid,8);
}
function parse(raw){
 if(raw.length!==54||!raw.startsWith('111000111000101010'))return false;
 const v=(a,b)=>parseInt(raw.slice(a,b),2);
 return crc([v(18,22),v(22,30),v(38,46),v(46,54)])===v(30,38);
}
// Fault parameters belong only to the test channel; decoder receives observations.
function simulate(raw,{blocked=[],flips=[],cutAt=null,hz=1}={}){
 if(!/^[01]{54}$/.test(raw)||hz<=0)throw Error('Entrada inválida');
 const received=(v,t,j)=>blocked.includes(j)||(cutAt!==null&&t>=cutAt&&j===0)?0:v;
 const pilots=Array.from({length:6},(_,t)=>[0,1,2].map(j=>received(t%2,t,j)));
 const good=[0,1,2].map(j=>pilots.every((row,t)=>row[j]===t%2));
 const log=[];let reconstructed='';
 for(let k=0;k<27;k++){
  const sent=encode(raw.slice(2*k,2*k+2).split('').map(Number));
  const y=sent.map((v,i)=>{
   const t=6+3*k+Math.floor(i/3),j=i%3;
   let z=received(v,t,j);if(flips.some(f=>f[0]===k&&f[1]===i))z^=1;
   return good[j]?z:null;
  });
  const d=decode(y);log.push({block:k,tickEnd:6+3*k+2,timeEnd:(6+3*k+3)/hz,received:y,...d});
  if(!d.ok)return {ok:false,reason:d.reason,log,good};
  reconstructed+=d.data.join('');
 }
 return {ok:parse(reconstructed),reconstructed,log,good,ticks:87};
}
function tests(){
 let checked=0;
 for(let mask=0;mask<512;mask++){
  const keep=Array.from({length:9},(_,i)=>Boolean(mask&(1<<i)));
  for(const w of words){
   const y=w.c.map((v,i)=>keep[i]?v:null),d=decode(y);
   if(d.ok)assert.deepEqual(d.data,w.d);
   const live=keep.map((v,i)=>v?i:-1).filter(i=>i>=0);
   const dm=d.distance;
   if(dm>0)for(let a=0;a<live.length;a++) {
    if(dm>2){let z=y.slice();z[live[a]]^=1;assert.deepEqual(decode(z).data,w.d);checked++;}
    if(dm>4)for(let b=a+1;b<live.length;b++){
     let z=y.slice();z[live[a]]^=1;z[live[b]]^=1;assert.deepEqual(decode(z).data,w.d);checked++;
    }
   }
   checked++;
  }
 }
 for(let x=0;x<256;x++)for(let m=0;m<8;m++){
  const blocked=[0,1,2].filter(j=>m&(1<<j));
  const r=simulate(frame(x),{blocked});
  assert.equal(r.ok,m!==7);
  if(r.ok)assert.equal(r.reconstructed,frame(x));
  checked++;
 }
 // Detection of a single bad observation with only one medium surviving.
 for(let j=0;j<3;j++)for(const w of words)for(let tick=0;tick<3;tick++){
  let y=w.c.map((v,i)=>i%3===j?v:null);y[tick*3+j]^=1;
  assert.equal(decode(y).ok,false);checked++;
 }
 // Errors outside the correction radius can be miscorrected: explicit counterexample.
 const y=words[0].c.slice();let changed=0;
 for(let i=0;i<9&&changed<4;i++)if(words[1].c[i]!==y[i]){y[i]^=1;changed++;}
 assert.deepEqual(decode(y).data,words[1].d);
 const r=simulate(frame(65),{cutAt:10});
 // A late persistent fault must not silently deliver a different valid frame in this fixture.
 assert.ok(!r.ok||r.reconstructed===frame(65));
 return {checked,lateCut:r.ok?'recovered':'rejected',outsideRadius:'miscorrection demonstrated'};
}
module.exports={G,encode,decode,frame,parse,simulate,tests};
if(require.main===module){
 const result={tests:tests(),examples:[[],[0],[0,1],[0,1,2]].map(blocked=>({blocked,...simulate(frame(65),{blocked})}))};
 console.log(JSON.stringify(result,null,2));
}
