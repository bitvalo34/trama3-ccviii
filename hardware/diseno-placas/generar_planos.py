"""Genera planos SVG, esquematico KiCad y dossier PDF desde diseno.json."""
from pathlib import Path
import json,math,uuid,html,collections
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'netlist/diseno.json').read_text(encoding='utf-8'));C=D['components'];W=D['wires'];EXT=D['external'];P=2.54
COLORS={'POWER':'#efcc8b','SERVO':'#ddbaa0','CORE':'#9cc4d5','TX':'#c2d9ac','RX':'#b5cfb7','ENABLE':'#d8c6eb','CLOCK':'#d0d0df','CLOCK_RX':'#ead4a2'}
def rowname(r):
 s='';r+=1
 while r:r,n=divmod(r-1,26);s=chr(65+n)+s
 return s
def svgview(bottom=False,wires=False,focus=None):
 out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 -13 112 177" width="896" height="1416">','<rect x="-10" y="-13" width="112" height="177" fill="white"/>',f'<text x="0" y="-8" font-size="2.9" font-family="sans-serif">T51-P1 | {"INFERIOR ESPEJO" if bottom else "SUPERIOR"} | ESTIMADO</text>','<rect x="0" y="0" width="90" height="150" fill="#eee6cc" stroke="#333" stroke-width=".3"/>'];fx=lambda x:90-x if bottom else x
 for r in range(56):
  out.append(f'<text x="-2" y="{5+r*P+.7}" font-size="1.7" text-anchor="end">{rowname(r)}</text>')
  for c in range(32):out.append(f'<circle cx="{fx(5+c*P)}" cy="{5+r*P}" r=".65" fill="none" stroke="#aaa" stroke-width=".12"/>')
 for c in range(32):out.append(f'<text x="{fx(5+c*P)}" y="-1.5" font-size="1.7" text-anchor="middle">{c+1}</text>')
 if wires:
  for w in W:
   color={'rojo':'#b32323','negro':'#222','naranja':'#bc6600','violeta':'#8a299b','azul':'#28699c'}[w['color']];pts=' '.join(f'{fx(p[0])},{p[1]}' for p in w['path'])
   out.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width=".23" opacity=".75"><title>{html.escape(w["id"]+" "+w["net"]+" "+w["start"]+" - "+w["end"])}</title></polyline>')
 for c in C:
  x,y,w,h,_=c['box'];left=90-x-w if bottom else x;opacity='1' if focus is None or c['zone'] in focus else '.18'
  out.append(f'<g opacity="{opacity}"><rect x="{left}" y="{y}" width="{w}" height="{h}" fill="{COLORS[c["zone"]] if not bottom else "none"}" stroke="#222" stroke-width=".2"/><text x="{left+w/2}" y="{y+h/2+.5}" text-anchor="middle" font-family="sans-serif" font-size="1.5">{c["ref"]}</text>')
  for p in c['pins']:out.append(f'<circle cx="{fx(p["x"])}" cy="{p["y"]}" r=".42" fill="{"#e22" if p["number"]=="1" else "#222"}"><title>{html.escape(c["ref"]+"."+p["number"]+" "+str(p["net"]))}</title></circle>')
  out.append('</g>')
 out+=['<text x="0" y="155" font-size="2.3">Pin 1 rojo. 90 x 150 mm; reticula asumida 32 x 56.</text>','<text x="0" y="159" font-size="2.1">T07/T08/T52 pendientes. No soldar con este estado.</text>','</svg>'];return '\n'.join(out)
for name,b,w,f in [('superior',False,False,None),('inferior',True,True,None),('sectores',False,False,None),('conexiones',False,True,None),('deshabilitacion',False,False,['ENABLE','SERVO']),('alimentacion-reloj',False,False,['POWER','CLOCK','CLOCK_RX'])]:(ROOT/f'planos/{name}.svg').write_text(svgview(b,w,f),encoding='utf-8')

def uid():return str(uuid.uuid4())
def q(s):return json.dumps(str(s),ensure_ascii=False)
def ef(sz=1):return f'(effects (font (size {sz} {sz})))'
rootid=uid();lib=[];items=[]
SC=C+[dict(ref=e['ref'],value=e['value'],kind='external',pins=[dict(number=n,name=n,net=net) for n,net in e['pins'].items()]) for e in EXT]
normal=0
for c in SC:
 if c['ref']=='U1':x,y=778,105
 else:x=44+(normal%8)*90;y=35+(normal//8)*45;normal+=1
 x=round(x/1.27)*1.27;y=round(y/1.27)*1.27
 name='T51_'+c['ref'];half=math.ceil(len(c['pins'])/2);height=max(7.62,(half+1)*2.54)
 shapes=f'(rectangle (start -11 {height/2}) (end 11 {-height/2}) (stroke (width 0.254) (type default)) (fill (type background)))';pins=[];places=[]
 for k,p in enumerate(c['pins']):
  left=k<half;idx=k if left else k-half;py=height/2-2.54-idx*2.54;px=-16.51 if left else 16.51;angle=0 if left else 180;typ='passive'
  if c['ref']=='U1' and p['name'] in ['SCL','RESET','A0','A1','A2']:typ='input'
  if c['ref']=='U1' and p['name']=='SDA':typ='bidirectional'
  if c['ref']=='U1' and p['name'] in ['GPA0','GPA1']:typ='tri_state'
  pins.append(f'(pin {typ} line (at {px} {py} {angle}) (length 5.08) (name {q(p["name"])} {ef(.75)}) (number {q(p["number"])} {ef(.85)}))');places.append((p,x+px,y-py,left))
 lib.append(f'(symbol {q("T51:"+name)} (pin_names (offset 1)) (in_bom yes) (on_board yes) (property "Reference" {q(c["ref"])} (at 0 {height/2+3} 0) {ef()}) (property "Value" {q(c["value"])} (at 0 {-height/2-3} 0) {ef()}) (symbol {q(name+"_0_1")} {shapes}) (symbol {q(name+"_1_1")} {" ".join(pins)}))')
 items.append(f'(symbol (lib_id {q("T51:"+name)}) (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp {"yes" if "DNP" in c["value"] else "no"}) (uuid {uid()}) (property "Reference" {q(c["ref"])} (at {x} {y-height/2-2} 0) {ef(1.2)}) (property "Value" {q(c["value"])} (at {x} {y+height/2+3} 0) {ef(.8)}) (instances (project "TRAMA3_T51" (path "/{rootid}" (reference {q(c["ref"])}) (unit 1)))))')
 for p,px,py,left in places:
  if p['net']:
   end=px+(-3.81 if left else 3.81);items.append(f'(wire (pts (xy {px} {py}) (xy {end} {py})) (stroke (width 0) (type default)) (uuid {uid()}))');items.append(f'(label {q(p["net"])} (at {end} {py} {0 if left else 180}) (effects (font (size .85 .85)) (justify {"left" if left else "right"} bottom)) (uuid {uid()}))')
  else:items.append(f'(no_connect (at {px} {py}) (uuid {uid()}))')
sch=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {rootid}) (paper "A1") (title_block (title "TRAMA3 T51 - Nodo A/B - PROVISIONAL") (rev "P1") (comment 1 "Redes homonimas conectadas. Ver dossier para circuitos y puentes de configuracion.")) (lib_symbols {" ".join(lib)}) {" ".join(items)} (embedded_fonts no))'
(ROOT/'esquematicos/TRAMA3_T51.kicad_sch').write_text(sch,encoding='utf-8');(ROOT/'esquematicos/TRAMA3_T51.kicad_pro').write_text('{}\n')
(ROOT/'esquematicos/T51.kicad_sym').write_text('(kicad_symbol_lib (version 20250114) (generator "kicad_symbol_editor") '+ ' '.join(s.replace('(symbol "T51:T51_','(symbol "T51_',1) for s in lib)+')',encoding='utf-8')
(ROOT/'esquematicos/sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "T51")(type "KiCad")(uri "${KIPRJMOD}/T51.kicad_sym")(options "")(descr "Simbolos documentales T51")))',encoding='utf-8')
print('SVG y KiCad generados:',len(SC),'simbolos')
