"""Esquema jerarquico KiCad: siete hojas funcionales, redes globales explicitas."""
from pathlib import Path
import json,uuid,math
R=Path(__file__).resolve().parent;D=json.loads((R/'netlist/diseno.json').read_text(encoding='utf8'));E=R/'esquematicos'
def uid():return str(uuid.uuid4())
def q(x):return json.dumps(str(x),ensure_ascii=False)
def ef(size=1.27):return f'(effects (font (size {size} {size})))'
def grid(v):return round(v/1.27)*1.27
root=uid();zones=['POWER','CORE','TX','SERVO','RX','ENABLE','CLOCK'];names=['Alimentacion y proteccion','MCP23017 e I2C','Transmisores luz y sonido','Servo y corte de mantenimiento','Receptores y puntos de prueba','Selectores de fallo y enlaces GPIO','Reloj aislado TX y RX']
SC=D['components'][:]
ez={'F1':'POWER','Q6':'POWER','MOD3':'POWER','SW1':'SERVO','M1':'SERVO','D3':'TX','BZ1':'TX','MOD1':'RX','MOD2':'RX','SW2':'RX'}
for e in D['external']:SC.append(dict(ref=e['ref'],value=e['value'],kind='external',zone=ez[e['ref']],pins=[dict(number=n,name=n,net=net) for n,net in e['pins'].items()]))
all_lib=[];rootitems=[]
for zi,zone in enumerate(zones):
 sheetid=uid();childid=uid();filename=f'{zi+1:02}_{zone}.kicad_sch';items=[];lib=[]
 group=[c for c in SC if ('CLOCK' if c['zone']=='CLOCK_RX' else c['zone'])==zone]
 for ci,c in enumerate(group):
  x=grid(50+(ci%4)*90);y=grid(40+(ci//4)*60);half=math.ceil(len(c['pins'])/2);height=max(10.16,(half+1)*2.54);name='T51_'+c['ref']
  shapes=f'(rectangle (start -11.43 {height/2}) (end 11.43 {-height/2}) (stroke (width 0.254) (type default)) (fill (type background)))'
  pins=[];places=[]
  for k,p in enumerate(c['pins']):
   left=k<half;idx=k if left else k-half;py=height/2-2.54-idx*2.54;px=-16.51 if left else 16.51;angle=0 if left else 180;typ='passive'
   if c['ref']=='U1' and p['name'] in ['SCL','RESET','A0','A1','A2']:typ='input'
   if c['ref']=='U1' and p['name']=='SDA':typ='bidirectional'
   if c['ref']=='U1' and p['name'] in ['GPA0','GPA1']:typ='tri_state'
   pins.append(f'(pin {typ} line (at {px} {py} {angle}) (length 5.08) (name {q(p["name"])} {ef(1)}) (number {q(p["number"])} {ef(1.1)}))');places.append((p,x+px,y-py,left))
  symbol=f'(symbol {q("T51:"+name)} (pin_names (offset 1)) (in_bom yes) (on_board yes) (property "Reference" {q(c["ref"])} (at 0 {height/2+3} 0) {ef()}) (property "Value" {q(c["value"])} (at 0 {-height/2-3} 0) {ef()}) (symbol {q(name+"_0_1")} {shapes}) (symbol {q(name+"_1_1")} {" ".join(pins)}))'
  lib.append(symbol);all_lib.append(symbol)
  items.append(f'(symbol (lib_id {q("T51:"+name)}) (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp {"yes" if "DNP" in c["value"] else "no"}) (uuid {uid()}) (property "Reference" {q(c["ref"])} (at {x} {y-height/2-2} 0) {ef(1.5)}) (property "Value" {q(c["value"])} (at {x} {y+height/2+3} 0) {ef(1.1)}) (instances (project "TRAMA3_T51" (path "/{root}/{sheetid}" (reference {q(c["ref"])}) (unit 1)))))')
  for p,px,py,left in places:
   if p['net']:
    end=px+(-3.81 if left else 3.81)
    items.append(f'(wire (pts (xy {px} {py}) (xy {end} {py})) (stroke (width 0) (type default)) (uuid {uid()}))')
    items.append(f'(global_label {q(p["net"])} (shape bidirectional) (at {end} {py} {180 if left else 0}) (effects (font (size 1.0 1.0)) (justify {"right" if left else "left"})) (uuid {uid()}))')
   else:items.append(f'(no_connect (at {px} {py}) (uuid {uid()}))')
  # Caracteristicas relevantes como texto de hoja, sin terminales ficticios.
 notes={'POWER':'J1 o J11, nunca simultaneos. NT1: puente local 1-2. Q6: D entrada / S salida / G a R30. F1 pendiente T08.', 'CORE':'U1 muesca hacia fila A. R2/R3 DNP y JP2/JP3 abiertos. P9_3 alimenta logica 3.3V; NO 5V desde BBB.', 'TX':'Q1/Q2 pads E-B-C; verificar lote. LED A/K y D1 banda a +5V. Buzzer: 5V y <=20mA provisional.', 'SERVO':'SW1 ON:1-2/4-5; OFF:2-3/5-6. Pin3 libre. Dos inversiones, PWM no invertido. J13 cable soldado.', 'RX':'VCC de modulos SOLO 3.3V. Orden de pines se verifica por modulo. AO/NC libres. JP4-6 abiertos antes de medir.', 'ENABLE':'JP10/11/12 = EN_C0/1/2. 1-2 RX habilitado; 2-3 RX a cero. JP4-6: enlaces BBB, inicialmente abiertos.', 'CLOCK':'J9 A->J8 B y J9 B->J8 A por pares +/-; NO GND A-B. U2 RX activo bajo. JP7 abierto antes de medir.'}[zone]
 items.append(f'(text {q(notes)} (at 25.4 261.62 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid {uid()}))')
 sch=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {childid}) (paper "A3") (title_block (title {q(names[zi]+" - Nodo A/B")}) (rev "T51-P1 PROVISIONAL") (comment 1 "Etiquetas globales del mismo nombre son la misma red. No autoriza soldadura.")) (lib_symbols {" ".join(lib)}) {" ".join(items)} (embedded_fonts no))'
 (E/filename).write_text(sch,encoding='utf8')
 x=25.4+(zi%2)*127;y=38.1+(zi//2)*38.1
 rootitems.append(f'(sheet (at {x} {y}) (size 101.6 25.4) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid {sheetid}) (property "Sheetname" {q(names[zi])} (at {x} {y-2.54} 0) (effects (font (size 1.27 1.27)) (justify left bottom))) (property "Sheetfile" {q(filename)} (at {x} {y+27.94} 0) (effects (font (size 1.27 1.27)) (justify left top))) (instances (project "TRAMA3_T51" (path "/{root}" (page "{zi+2}")))))')
roottext='TRAMA3 T51 - Interfaz simetrica A/B\nRevision 102 conservada. T07/T08/T52 pendientes.\nEsquema documental por componentes y redes globales.\nCoordenadas y cableado fisico: hardware/diseno-placas/soldadura.\nPuentes/switches: conexiones internas definidas en la guia y CSV.'
rootitems.append(f'(text {q(roottext)} (at 25.4 15.24 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid {uid()}))')
(E/'TRAMA3_T51.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {root}) (paper "A4") (title_block (title "TRAMA3 T51 - Indice de circuitos A/B") (rev "P1 - PROVISIONAL")) (lib_symbols) {" ".join(rootitems)} (sheet_instances (path "/" (page "1"))) (embedded_fonts no))',encoding='utf8')
(E/'T51.kicad_sym').write_text('(kicad_symbol_lib (version 20250114) (generator "kicad_symbol_editor") '+' '.join(s.replace('(symbol "T51:T51_','(symbol "T51_',1) for s in all_lib)+')',encoding='utf8')
print('Esquema modular generado: 7 hojas funcionales + indice')
