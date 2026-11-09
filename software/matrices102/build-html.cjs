const fs=require('node:fs'),path=require('node:path');const dir=__dirname;
let html=fs.readFileSync(path.join(dir,'template.html'),'utf8');
html=html.replace('/* CORE */',fs.readFileSync(path.join(dir,'core.js'),'utf8')).replace('/* ENGINE */',fs.readFileSync(path.join(dir,'engine.js'),'utf8'));
fs.writeFileSync(path.join(dir,'TRAMA3_Matricial_102.html'),html);
