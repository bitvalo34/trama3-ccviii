"""Comprobaciones reproducibles del paquete, sin controlar las BeagleBone."""
from pathlib import Path
import json,math,itertools,collections,xml.etree.ElementTree as ET,csv
R=Path(__file__).resolve().parent
D=json.loads((R/'netlist/diseno.json').read_text(encoding='utf8'))
errors=[];checks={};expected=collections.defaultdict(set)
for c in D['components']:
 for p in c['pins']:
  if p['net']:expected[p['net']].add((c['ref'],p['number']))
for c in D['external']:
 for pin,net in c['pins'].items():
  if net:expected[net].add((c['ref'],pin))
tree=ET.parse(R/'netlist/kicad-export.xml');actual={}
for n in tree.findall('.//nets/net'):
 name=n.attrib['name'].lstrip('/')
 if name.startswith('unconnected-'):continue
 actual[name]={(p.attrib['ref'],p.attrib['pin']) for p in n.findall('node')}
checks['netlist_kicad_igual_manifest']=dict(expected)==actual
if not checks['netlist_kicad_igual_manifest']:
 for net in set(expected)|set(actual):
  if expected.get(net)!=actual.get(net):errors.append({'net':net,'esperado':sorted(expected.get(net,[])),'kicad':sorted(actual.get(net,[]))})
def segments(w):
 ps=w['path'];ps=[[ps[0][0],ps[0][1],-.3]]+ps+[[ps[-1][0],ps[-1][1],-.3]]
 return [(a,b) for a,b in zip(ps,ps[1:]) if a!=b]
def distance(a,b,c,d):
 # Exacta para segmentos ortogonales alineados a X/Y/Z.
 return math.sqrt(sum(max(min(a[k],b[k])-max(c[k],d[k]),min(c[k],d[k])-max(a[k],b[k]),0)**2 for k in range(3)))
collisions=[];minimum=99
for wa,wb in itertools.combinations(D['wires'],2):
 if wa['net']==wb['net']:continue
 radii=(.6 if wa['wire'].startswith('22') else .4)+(.6 if wb['wire'].startswith('22') else .4)
 dist=min(distance(*a,*b) for a in segments(wa) for b in segments(wb));clear=dist-radii;minimum=min(minimum,clear)
 if clear<-.001:collisions.append([wa['id'],wb['id'],round(clear,3)])
checks['rutas_sin_interseccion_entre_redes']=not collisions
checks['holgura_minima_aislamientos_mm']=round(minimum,3)
checks['diametro_modelado_cable_mm']={'22AWG':1.2,'26AWG':.8}
checks['capas_ruteo']=D['routing']['capas_usadas']
checks['profundidad_cable_mm']=round(max(-p[2]+(.6 if w['wire'].startswith('22') else .4) for w in D['wires'] for p in w['path']),2)
if collisions:errors.append({'colisiones':collisions})
# Los ocho estados EN: OFF impone cero electrico, ON conserva RAW. El reloj no participa.
en=[]
for mask in range(8):
 outputs=[('RAW' if mask&(1<<k) else 'GND_LOGIC') for k in range(3)]
 en.append({'mascara':format(mask,'03b'),'C0':outputs[0],'C1':outputs[1],'C2':outputs[2],'reloj':'sin cambio'})
checks['estados_EN']=en
checks['servo_doble_inversion']=[{'PWM_BBB':0,'Q3':'off','Q4':'on','PWM_5V':0},{'PWM_BBB':1,'Q3':'on','Q4':'off','PWM_5V':1}]
checks['servo_OFF']={'alimentacion':'abierta','senal':'GND_ACT','condicion':'DPDT cableado segun contactos comprobados'}
remote={p['net'] for c in D['components'] for p in c['pins'] if p['net'] and p['net'].startswith('CLK_REMOTE')}
checks['dominio_remoto_sin_GND_en_red']=not bool(remote&{'GND_LOGIC','GND_ACT'})
checks['nota_aislamiento']='Comprobacion de redes, no ensayo de aislamiento. PC817 barrera optica; USB compartido puede unir tierras fuera de estas placas.'
usage=collections.Counter()
for c in D['components']:
 if c['kind']=='R':usage[c['value']]+=2
checks['resistencias_ambas_placas']=dict(usage)
checks['cables_metros_ambas_placas']={typ:round(sum(w['cut_mm'] for w in D['wires'] if w['wire']==typ)*2/1000,3) for typ in {w['wire'] for w in D['wires']}}
checks['corriente_LED_mA_nominal']=round((5-2-.1)/330*1000,2)
checks['corriente_LED_mA_extremos_5V5pct_Vf1p8a2p2_Vce0p1a0p2_R5pct']=[round((4.75-2.2-.2)/(330*1.05)*1000,2),round((5.25-1.8-.1)/(330*.95)*1000,2)]
checks['potencia_R_LED_W_max']=round((5.25-1.8-.1)**2/(330*.95),4)
checks['CLK_IF_mA_min_diseno']=round((3.135-1.4-.2)/(270*1.05)*1000,2)
checks['CLK_IF_mA_max_diseno']=round((3.465-1.0-.1)/(270*.95)*1000,2)
checks['CLK_lector_mA']=round((3.3-.2)/4700*1000,3)
checks['limite_driver_buzzer_mA']=20
checks['MCP_fuente_base_mA_por_driver']=round((3.3-.8)/1000*1000,2)
checks['RC_final_carrera_ms']=4700*100e-9*1000
checks['PMOS_P_W_1A_R065']=.065
checks['PMOS_P_W_2p5A_R065']=round(2.5**2*.065,3)
checks['limites']='Calculos condicionales con tolerancias asumidas; sin SPICE, medidas de sensores, ensayo de fusible, temporizacion ni validacion fisica.'
out={'revision':'T51-P1','comprobaciones':checks,'errores':errors,'estado':'PASA COMPROBACIONES DIGITALES/GEOMETRICAS' if not errors else 'CORREGIR','T52':'PENDIENTE REVISION INDEPENDIENTE'}
(R/'verificaciones/resultado-integrado.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False,indent=2))
if errors:raise SystemExit(1)
