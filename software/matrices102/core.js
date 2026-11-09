(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.Matrix102=api;})(globalThis,function(){
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

return {G,encode,decode};});
