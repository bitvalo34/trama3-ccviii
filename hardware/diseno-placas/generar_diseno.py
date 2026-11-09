"""Generador T51 provisional, sin acceso a hardware."""
from pathlib import Path
import json,csv,math,uuid,itertools,collections,html
ROOT=Path(__file__).resolve().parent
for d in ['esquematicos','netlist','cad/placa-A','cad/placa-B','planos','soldadura','verificaciones']:(ROOT/d).mkdir(parents=True,exist_ok=True)
P=2.54;C=[]
def xy(c,r):return(round(5+c*P,3),round(5+r*P,3))
def rowname(r):
 s='';r+=1
 while r:r,n=divmod(r-1,26);s=chr(65+n)+s
 return s
def add(ref,value,kind,pins,box,zone,notes='',status='Disponible para diseño; dimensiones estimadas'):
 ps=[dict(number=str(n),name=na,net=net,col=c,row=r,x=xy(c,r)[0],y=xy(c,r)[1],hole=f'{rowname(r)}{c+1}') for n,na,net,c,r in pins]
 C.append(dict(ref=ref,value=value,kind=kind,pins=ps,box=box,zone=zone,notes=notes,status=status))
def axial(ref,val,n1,n2,c,r,zone,kind='R',notes=''):
 x,y=xy(c,r);add(ref,val,kind,[(1,'1',n1,c,r),(2,'2',n2,c+3,r)],[x+.61,y-1.3,6.4,2.6,3],zone,notes)
def header(ref,val,nets,c,r,zone,step=1,kind='header',notes=''):
 x,y=xy(c,r);n=len(nets);box=[x-2.5,y-4,5+(n-1)*step*P,8,10] if kind=='terminal' else [x-1.25,y-1.25,2.5+(n-1)*step*P,2.5,8]
 add(ref,val,kind,[(i+1,net or 'NC',net,c+i*step,r) for i,net in enumerate(nets)],box,zone,notes)
def npn(ref,val,c,r,zone,b,cn,e='GND_ACT'):
 x,y=xy(c,r);add(ref,val,'npn',[(1,'E',e,c,r),(2,'B',b,c+1,r),(3,'C',cn,c+2,r)],[x-.6,y-2,6.3,4,5],zone,'PAD 1=E,2=B,3=C. Adaptar patas aisladas segun lote; no asumir cara plana.',status='Pinout del lote pendiente; TO92 aproximado')
def cap(ref,val,n1,n2,c,r,zone,diam=4,height=5,step=1):
 x,y=xy(c,r);cx=x+P*step/2;add(ref,val,'electro' if 'uF' in val else 'cap',[(1,'+',n1,c,r),(2,'-',n2,c+step,r)],[cx-diam/2,y-diam/2,diam,diam,height],zone)
header('J1','ENTRADA 5V / 2.5A',['+5V_RAW','GND_ACT'],2,2,'POWER',2,'terminal','Una fuente; nunca paralelo con USB.')
header('JF1','PORTAFUSIBLE EXTERNO',['+5V_RAW','+5V_FUSED'],2,7,'POWER',2,'terminal')
header('JQ6','PMOS G/S/D',['GATE_POL','+5V_ACT','+5V_FUSED'],9,2,'POWER',kind='solderpads',notes='IRLML6402 G1/S2/D3 en adaptador elevado 10x10mm; cables soldados, sin Dupont en S/D.')
axial('R30','100k','GATE_POL','GND_ACT',9,6,'POWER')
cap('C1','1000uF/16V','+5V_ACT','GND_ACT',3,12,'POWER',10,20,2)
cap('C2','100nF','+5V_ACT','GND_ACT',10,11,'POWER')
header('NT1','ESTRELLA 22AWG',['GND_ACT','GND_LOGIC'],10,15,'POWER',kind='link',notes='Unir 1-2: unico enlace local de retornos.')
header('JUSB','USB AUX TEST',['+5V_RAW','GND_ACT'],2,17,'POWER',notes='Alternativa externa; NO servo ni simultaneo J1. Limite provisional 0.5A.')
header('JS1','CORTE SERVO DPDT',['+5V_ACT','+5V_SERVO',None,'PWM_5V','SERVO_SIG','GND_ACT'],18,2,'SERVO',kind='solderpads',notes='DPDT externo >=3A DC/12V: ON 1-2/4-5; OFF 2-3/5-6. Pin3 aislado. Cable directo soldado; no Dupont para potencia.')
header('J4','SG90 GND/+5V/SIG',['GND_ACT','+5V_SERVO','SERVO_SIG'],27,2,'SERVO',2,'terminal','Arnes a macho 3p/2.54 compatible con hembra servo; no insertar conector servo en bornera.')
npn('Q3','2N3904',19,8,'SERVO','PWM_B1','PWM_INV');npn('Q4','2N3904',27,8,'SERVO','PWM_B2','PWM_5V')
for a in [('R10','4.7k','PWM_BBB','PWM_B1',16,5),('R11','47k','PWM_B1','GND_ACT',16,11),('R12','4.7k','+5V_SERVO','PWM_INV',21,11),('R13','4.7k','PWM_INV','PWM_B2',26,11),('R14','47k','PWM_B2','GND_ACT',16,14),('R15','2.2k','+5V_SERVO','PWM_5V',21,14),('R16','47k','SERVO_SIG','GND_ACT',26,14)]:axial(*a,'SERVO')
cap('C3','100nF','+5V_SERVO','GND_ACT',28,17,'SERVO')
mp={i:(f'GPB{i-1}',None) for i in range(1,9)}
mp.update({9:('VDD','+3V3_LOGIC'),10:('VSS','GND_LOGIC'),11:('NC',None),12:('SCL','I2C_SCL'),13:('SDA','I2C_SDA'),14:('NC',None),15:('A0','GND_LOGIC'),16:('A1','GND_LOGIC'),17:('A2','GND_LOGIC'),18:('RESET','MCP_RESET'),19:('INTB',None),20:('INTA',None)})
mp.update({i:(f'GPA{i-21}',{21:'C0_TX',22:'C1_TX'}.get(i)) for i in range(21,29)})
ps=[(n,mp[n][0],mp[n][1],4 if n<=14 else 7,21+n-1 if n<=14 else 21+28-n) for n in range(1,29)];x,y=xy(4,21)
add('U1','MCP23017 + zocalo DIP28','dip28',ps,[x-1.2,y-1.4,10.02,35.82,9],'CORE','Muesca hacia A. Zocalo e IC comparten pads. Direccion 0x20.')
cap('C4','100nF','+3V3_LOGIC','GND_LOGIC',1,29,'CORE')
axial('R1','10k','+3V3_LOGIC','MCP_RESET',1,37,'CORE');header('JP1','RESET abierto',['MCP_RESET','GND_LOGIC'],6,37,'CORE')
axial('R2','4.7k DNP','+3V3_LOGIC','SCL_PULL',1,40,'CORE');axial('R3','4.7k DNP','+3V3_LOGIC','SDA_PULL',6,40,'CORE')
header('JP2','PU SCL abierto',['SCL_PULL','I2C_SCL'],1,43,'CORE');header('JP3','PU SDA abierto',['SDA_PULL','I2C_SDA'],6,43,'CORE')
header('JBBB','ARNES BBB',['+3V3_LOGIC','GND_LOGIC','I2C_SCL','I2C_SDA','PWM_BBB','CLK_TX','OPT_BBB','AUD_BBB','MECH_BBB','CLK_BBB'],12,36,'CORE',notes='Ver arnes-BBB.csv; sin 5V BBB.')
npn('Q1','2N2222 lote pendiente',13,22,'TX','LED_BASE','LED_K')
axial('R4','1k','C0_TX','LED_BASE',11,19,'TX');axial('R5','10k','LED_BASE','GND_ACT',11,25,'TX');axial('R6','330','+5V_ACT','LED_A',17,19,'TX')
header('J2','LED A/K',['LED_A','LED_K'],19,23,'TX',2,'terminal')
npn('Q2','2N2222 lote pendiente',13,30,'TX','BUZZ_BASE','BUZZ_NEG')
axial('R7','1k','C1_TX','BUZZ_BASE',11,27,'TX');axial('R8','10k','BUZZ_BASE','GND_ACT',11,33,'TX')
header('J3','BUZZER +/-',['+5V_ACT','BUZZ_NEG'],19,29,'TX',2,'terminal')
axial('D1','1N5819','BUZZ_NEG','+5V_ACT',18,33,'TX','diode','Pad1 A, pad2 K/banda +5V; no conectar sobre servo.')
header('J5','LDR 3V3/GND/DO',['+3V3_LOGIC','GND_LOGIC','OPT_RAW'],27,21,'RX',2,'terminal','Orden placa; adaptar al modulo. AO libre.')
header('J6','AUDIO 3V3/GND/DO',['+3V3_LOGIC','GND_LOGIC','AUD_RAW'],27,27,'RX',2,'terminal','Arnes individual por serigrafia.')
header('J7','FINAL COM/NO',['GND_LOGIC','MECH_RAW'],28,33,'RX',2,'terminal')
axial('R17','10k','+3V3_LOGIC','OPT_RAW',25,24,'RX');axial('R18','10k','+3V3_LOGIC','AUD_RAW',25,30,'RX');axial('R19','4.7k','+3V3_LOGIC','MECH_RAW',26,37,'RX');cap('C5','100nF','MECH_RAW','GND_LOGIC',29,40,'RX')
for k,raw,bbb,c in [(0,'OPT_RAW','OPT_BBB',2),(1,'AUD_RAW','AUD_BBB',12),(2,'MECH_RAW','MECH_BBB',22)]:
 sel=f'C{k}_SEL';pre=f'C{k}_TEST';header(f'EN_C{k}',f'C{k}:1-2 ON/2-3 OFF',[raw,sel,'GND_LOGIC'],c,46,'ENABLE')
 axial(f'R{20+k}','1k',sel,pre,c,49,'ENABLE');axial(f'R{23+k}','100k',sel,'GND_LOGIC',c+4,46,'ENABLE')
 header(f'JP{4+k}',f'C{k} LINK GPIO',[pre,bbb],c+5,49,'ENABLE',notes='Abierto antes de medir DO. EN deshabilita RX remoto->local.')
header('J8','CLK RX REMOTO +/-',['CLK_REMOTE_A','CLK_REMOTE_K'],2,54,'CLOCK_RX',2,'terminal')
x,y=xy(8,53);add('U2','PC817 DIP4','dip4',[(1,'A','CLK_REMOTE_A',8,53),(2,'K','CLK_REMOTE_K',8,54),(3,'E','GND_LOGIC',11,54),(4,'C','CLK_RX_RAW',11,53)],[x-1.1,y-1.2,9.82,5,4.5],'CLOCK_RX','Pin1 arriba izquierda; no unir remoto con GND local.')
axial('R26','4.7k','+3V3_LOGIC','CLK_RX_RAW',12,52,'CLOCK');axial('R27','1k','CLK_RX_RAW','CLK_TEST',12,55,'CLOCK');header('JP7','CLK LINK',['CLK_TEST','CLK_BBB'],17,55,'CLOCK')
npn('Q5','2N3904',23,52,'CLOCK','CLK_BASE','CLK_SINK','GND_LOGIC')
axial('R28','2.2k','CLK_TX','CLK_BASE',20,42,'CLOCK');axial('R29','47k','CLK_BASE','GND_LOGIC',26,43,'CLOCK');axial('R31','270','+3V3_LOGIC','CLK_SEND_A',21,55,'CLOCK')
header('J9','CLK TX +/-',['CLK_SEND_A','CLK_SINK'],28,54,'CLOCK',2,'terminal')
axial('D2','1N4148','CLK_REMOTE_K','CLK_REMOTE_A',2,51,'CLOCK_RX','diode','Antiparalelo LED: banda hacia U2.1.')
for ref,net,c,r,zone in [('TP1','+5V_ACT',13,12,'POWER'),('TP2','GND_ACT',13,15,'POWER'),('TP3','+3V3_LOGIC',9,29,'CORE'),('TP4','GND_LOGIC',9,32,'CORE'),('TP5','OPT_RAW',24,21,'RX'),('TP6','AUD_RAW',24,27,'RX'),('TP7','MECH_RAW',24,33,'RX'),('TP8','CLK_RX_RAW',17,52,'CLOCK'),('TP9','SERVO_SIG',24,17,'SERVO'),('TP10','CLK_TX',20,49,'CLOCK')]:header(ref,net,[net],c,r,zone,kind='test')
EXT=[]
def ext(ref,value,size,pins,connect,status,role):EXT.append(dict(ref=ref,value=value,size=size,pins=pins,connect=connect,status=status,role=role))
ext('F1','5x20mm 1A; T08 pendiente',[32,12,12],{'1':'+5V_RAW','2':'+5V_FUSED'},'JF1','Recibido; rapido/lento desconocido','portafusible con cable')
ext('Q6','IRLML6402 + adaptador SOT23',[10,10,4],{'1':'GATE_POL','2':'+5V_ACT','3':'+5V_FUSED'},'JQ6','Adicional no comprado','G/S/D; D entrada, S salida; elevado')
ext('SW1','DPDT ON-ON >=3A DC/12V',[13,10,15],{'1':'+5V_ACT','2':'+5V_SERVO','3':None,'4':'PWM_5V','5':'SERVO_SIG','6':'GND_ACT'},'JS1','Adicional no comprado','ON 1-2/4-5; OFF 2-3/5-6')
ext('MOD_USB','Micro USB breakout',[15,15,5],{'VBUS':'+5V_RAW','GND':'GND_ACT'},'JUSB','Recibido sin medida','Alternativa test sin servo')
ext('LED_EXT','LED rojo 5mm',[5,5,8],{'A':'LED_A','K':'LED_K'},'J2','Recibido','emisor externo')
ext('BUZZ_EXT','Buzzer activo 5V',[12,12,10],{'+':'+5V_ACT','-':'BUZZ_NEG'},'J3','Recibido; consumo pendiente','driver provisional max20mA')
ext('SG90_EXT','SG90 180',[23,12.2,29],{'GND':'GND_ACT','VCC':'+5V_SERVO','SIG':'SERVO_SIG'},'J4','Recibido sin medida','volumen de referencia')
ext('LDR_EXT','LDR LM393',[32,14,12],{'VCC':'+3V3_LOGIC','GND':'GND_LOGIC','DO':'OPT_RAW','AO':None},'J5','Recibido sin medida','orden modulo pendiente')
ext('AUD_EXT','KY037/HW484',[45,17,16],{'VCC':'+3V3_LOGIC','GND':'GND_LOGIC','DO':'AUD_RAW','AO':None},'J6','Recibido sin medida','variantes A/B, no copiar arnes')
ext('LIMIT_EXT','SPDT rueda',[28,16,15],{'COM':'GND_LOGIC','NO':'MECH_RAW','NC':None},'J7','Recibido sin medida','NC libre')
REN={'JBBB':'J10','JUSB':'J11','JQ6':'J12','JS1':'J13','JF1':'J14','EN_C0':'JP10','EN_C1':'JP11','EN_C2':'JP12','MOD_USB':'MOD3','LED_EXT':'D3','BUZZ_EXT':'BZ1','SG90_EXT':'M1','LDR_EXT':'MOD1','AUD_EXT':'MOD2','LIMIT_EXT':'SW2'}
for c in C:c['ref']=REN.get(c['ref'],c['ref'])
for e in EXT:
 e['ref']=REN.get(e['ref'],e['ref']);e['connect']=REN.get(e['connect'],e['connect'])
N=collections.defaultdict(list)
for c in C:
 for p in c['pins']:
  if p['net']:N[p['net']].append(dict(ref=c['ref'],**p))
W=[]
for net,ps in sorted(N.items()):
 remaining=ps[:];cur=remaining.pop(0)
 while remaining:
  nxt=min(remaining,key=lambda p:abs(p['x']-cur['x'])+abs(p['y']-cur['y']));remaining.remove(nxt)
  power=net in ['+5V_RAW','+5V_FUSED','+5V_ACT','+5V_SERVO','GND_ACT'];z=-2.4-1.5*(len(W)%4)
  path=[[cur['x'],cur['y'],z],[nxt['x'],cur['y'],z],[nxt['x'],nxt['y'],z]]
  # Dominio remoto inferior izquierdo x<30,y>132: prohibido atravesarlo con redes locales.
  if not net.startswith('CLK_REMOTE') and min(cur['x'],nxt['x'])<30 and max(cur['y'],nxt['y'])>132:
   path=[[cur['x'],cur['y'],z],[cur['x'],130,z],[nxt['x'],130,z],[nxt['x'],nxt['y'],z]]
  path=[p for i,p in enumerate(path) if i==0 or p!=path[i-1]]
  W.append(dict(id=f'W{len(W)+1:03}',net=net,source=f'{cur["ref"]}.{cur["number"]}',destination=f'{nxt["ref"]}.{nxt["number"]}',start=cur['hole'],end=nxt['hole'],path=path,cut_mm=round(abs(nxt['x']-cur['x'])+abs(nxt['y']-cur['y'])+2*abs(z)+12),side='inferior',wire='22AWG unifilar' if power else '26AWG aislado (adicional)',color='violeta' if net.startswith('CLK_REMOTE') else 'negro' if 'GND' in net else 'rojo' if net.startswith('+5') else 'naranja' if net.startswith('+3') else 'azul',notes='Aislado; soldar lateral al terminal, no insertar varios cables en agujero.'))
  cur=nxt
from rutear import route
routing=route(C,W)
D=dict(revision='T51-P1',protocol='102',status='PROVISIONAL - NO AUTORIZADO PARA SOLDAR',date='2026-11-09',board=dict(width=90,height=150,thickness=1.6,pitch=P,rows=56,columns=32,origin=[5,5],hole_diameter=1,pad_diameter=1.8,measurement='ESTIMADO; confirmar T07'),components=C,external=EXT,wires=W,routing=routing)
(ROOT/'netlist/diseno.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')
def csvout(name,rows):
 with (ROOT/name).open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
csvout('soldadura/coordenadas.csv',[dict(ref=c['ref'],valor=c['value'],pin=p['number'],funcion=p['name'],red=p['net'] or 'NC',perforacion=p['hole'],columna=p['col']+1,fila=rowname(p['row']),x_mm=p['x'],y_mm=p['y'],altura_mm=c['box'][4],zona=c['zone'],estado=c['status']) for c in C for p in c['pins']])
csvout('soldadura/cableado.csv',[{**{k:v for k,v in w.items() if k!='path'},'ruta_xyz_mm':json.dumps(w['path'])} for w in W])
csvout('netlist/componentes.csv',[dict(ref=c['ref'],valor=c['value'],tipo=c['kind'],zona=c['zone'],ancho_mm=c['box'][2],largo_mm=c['box'][3],alto_mm=c['box'][4],pin1=c['pins'][0]['hole'],estado=c['status'],nota=c['notes']) for c in C])
csvout('netlist/redes.csv',[dict(red=n,terminales='; '.join(f'{p["ref"]}.{p["number"]}' for p in ps)) for n,ps in sorted(N.items())])
csvout('soldadura/arnes-BBB.csv',[dict(pin_placa=i,BBB=b,funcion=n) for i,b,n in [(1,'P9_3','3.3V'),(2,'P9_1','GND'),(3,'P9_19','SCL'),(4,'P9_20','SDA'),(5,'P9_14','PWM'),(6,'P8_11','CLK TX'),(7,'P9_27','OPT RX'),(8,'P8_16','AUD RX'),(9,'P9_24','MECH RX'),(10,'P8_15','CLK RX')]])
errors=[];occupied={}
for c in C:
 x,y,w,h,z=c['box']
 if x<0 or y<0 or x+w>90 or y+h>150:errors.append('Fuera placa '+c['ref'])
 for p in c['pins']:
  key=(p['col'],p['row'])
  if key in occupied:errors.append(f'Pad compartido {c["ref"]}.{p["number"]} con {occupied[key]}')
  occupied[key]=f'{c["ref"]}.{p["number"]}'
  if not(0<=key[0]<32 and 0<=key[1]<56):errors.append('Pad fuera reticula '+str(key))
for a,b in itertools.combinations(C,2):
 x,y,w,h,_=a['box'];X,Y,Wd,H,_=b['box']
 if min(x+w,X+Wd)-max(x,X)>.01 and min(y+h,Y+H)-max(y,Y)>.01:errors.append(f'Cuerpos solapados {a["ref"]}/{b["ref"]}')
for net,ps in N.items():
 target={f'{p["ref"]}.{p["number"]}' for p in ps};seen={next(iter(target))}
 for _ in ps:
  for w in [q for q in W if q['net']==net]:
   if w['source'] in seen or w['destination'] in seen:seen.update([w['source'],w['destination']])
 if target!=seen:errors.append('Red desconectada '+net)
report=dict(components=len(C),pads=len(occupied),grid_holes=1792,wires=len(W),nets=len(N),errors=errors,scope='Cuerpos estimados, pads y conectividad. No prueba fisica ni analogica.',wire_meters_per_node=round(sum(w['cut_mm'] for w in W)/1000,2))
(ROOT/'verificaciones/resultado-geometria.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
if errors:raise SystemExit(2)
