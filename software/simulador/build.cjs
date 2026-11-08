'use strict';
const fs=require('node:fs'),path=require('node:path');
const read=p=>fs.readFileSync(path.join(__dirname,p),'utf8');
const engine=read('engine.js');
if(engine.includes('</script'))throw Error('El motor contiene cierre de script');
fs.writeFileSync(path.join(__dirname,'Simulador_TRAMA3.html'),read('ui.template.html').replace('/*__ENGINE__*/',()=>engine),'utf8');
console.log('Simulador_TRAMA3.html generado; incluye el motor, estilos y controles.');
