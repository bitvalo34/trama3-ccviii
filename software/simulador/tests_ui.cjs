'use strict';
// Prueba de código de interfaz con un DOM mínimo. No es un navegador ni QA visual.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),test=require('node:test');
const html=fs.readFileSync(require('node:path').join(__dirname,'Simulador_TRAMA3.html'),'utf8');
class Element {
 constructor(tag='div'){this.tag=tag;this.children=[];this.value='';this.className='';this._text='';this.style={};this.scrollTop=0;this.scrollHeight=100;}
 append(...els){this.children.push(...els);}
 replaceChildren(...els){this.children=els;this._text='';}
 set textContent(v){this._text=String(v);this.children=[];}
 get textContent(){return this._text+this.children.map(x=>x.textContent||'').join('');}
 get classList(){const self=this;return {contains(n){return self.className.split(' ').includes(n);},add(n){if(!this.contains(n))self.className+=' '+n;},toggle(n,on){const has=this.contains(n);if(on===undefined)on=!has;if(on&&!has)self.className+=' '+n;if(!on)self.className=self.className.split(' ').filter(v=>v!==n).join(' ');}};}
 click(){if(this.onclick)this.onclick();}
}
function runtime(){
 const elements={};
 for(const m of html.matchAll(/<(\w+)\b[^>]*\bid="([^"]+)"[^>]*>/g)){
   const el=new Element(m[1]);el.className=(m[0].match(/class="([^"]*)"/)||[])[1]||'';
   el.value=(m[0].match(/value="([^"]*)"/)||[])[1]||'';
   const end=html.indexOf('</'+m[1]+'>',m.index+m[0].length),inside=html.slice(m.index+m[0].length,end);
   if(m[1]==='textarea')el.value=inside;
   if(m[1]==='select'){
     const opts=[...inside.matchAll(/<option([^>]*)>([^<]*)<\/option>/g)];
     const selected=opts.find(x=>x[1].includes('selected'))||opts[0];
     el.value=(selected[1].match(/value="([^"]*)"/)||[])[1]??selected[2];
   }
   elements[m[2]]=el;
 }
 const context=vm.createContext({TextEncoder,TextDecoder,Blob,URL,performance:{now:()=>0},
   document:{getElementById:id=>{assert.ok(elements[id],id);return elements[id];},createElement:tag=>new Element(tag)},
   requestAnimationFrame:()=>{},setTimeout:()=>{}});
 for(const m of html.matchAll(/<script>([\s\S]*?)<\/script>/g))vm.runInContext(m[1],context);
 return {elements,run:s=>vm.runInContext(s,context)};
}
test('HTML autónomo carga y sus controles recorren el ensayo',()=>{
 const {elements:e,run}=runtime();assert.equal(run('result.status'),'COMPLETE');assert.equal(e.frames.textContent,'14');
 e.toData.click();assert.ok(e.frameLabel.textContent.includes('DATA'));assert.equal(e.symbols.children.length,95);
 e.step.click();e.nextFrame.click();e.end.click();assert.ok(e.chat.textContent.includes('A'));
 e.analysisTab.click();assert.equal(e.analysis.classList.contains('hidden'),false);e.labTab.click();assert.equal(e.analysis.classList.contains('hidden'),true);
 e.reset.click();assert.equal(e.timeline.value,0);e.play.click();assert.equal(run('playing'),true);e.play.click();assert.equal(run('playing'),false);
});
test('Interfaz aplica fallos, valida codificación y presenta texto como texto',()=>{
 const {elements:e,run}=runtime();e.scenario.value='crc';e.build.click();assert.equal(run('result.stats.crcErrors'),1);
 e.scenario.value='blocked';e.build.click();assert.equal(run('result.status'),'COMPLETE');
 e.encoding.value='windows-1252';e.msgA.value='🙂';e.build.click();assert.ok(e.error.textContent.includes('CP1252'));
 e.encoding.value='utf-8';e.msgA.value='<img src=x onerror=alert(1)>';e.scenario.value='clean';e.build.click();e.end.click();
 assert.ok(e.chat.textContent.includes('<img'));assert.equal(e.chat.children.length,0);
 e.msgA.value='Añ€🙂';e.msgB.value='B';e.hz.value='4';e.crc.value='MAXIM-DOW';e.scenario.value='rate-active';e.build.click();
 assert.equal(run('result.status'),'COMPLETE');assert.equal(run('result.deliveries.length'),2);
 e.toData.click();e.filter.value='all';e.filter.onchange();assert.ok(e.log.children.length>0);
});
test('HTML sin dependencias externas y scripts con sintaxis válida',()=>{
 assert.equal(/<script\b[^>]*\bsrc\s*=/.test(html),false);assert.equal(/<link\b[^>]*\brel="stylesheet"/.test(html),false);
 assert.equal(html.includes('/*__ENGINE__*/'),false);
 for(const m of html.matchAll(/<script>([\s\S]*?)<\/script>/g))new vm.Script(m[1]);
});

test('Selector de cortes y salto al cambio enseñan la línea superviviente',()=>{
 const {elements:e,run}=runtime();e.msgA.value='Hola';e.cutA.value='3';e.build.click();e.nextMap.click();
 assert.equal(run('result.events[idx].map'),4);e.toData.click();assert.ok(e.frameLabel.textContent.includes('54 ciclos de cuerpo'));
 assert.equal(e.symbols.children.length,275);e.end.click();assert.ok(e.chat.textContent.includes('Hola'));
 e.cutA.value='7';e.build.click();assert.equal(run('result.status'),'RECOVERY_1HZ');
});

test('Comparador reproduce el límite hipotético de las tres líneas',()=>{
 const {elements:e}=runtime();e.mechanicalMs.value='300';e.sweep.click();
 assert.ok(e.sweepResult.textContent.includes('sin reintentos: 2 Hz'));
});
