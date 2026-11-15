"""Verificaciones offline de cabida, archivos y registros; nunca prueba hardware."""
from pathlib import Path
import json,csv,math,importlib.util,tempfile,sys
from pypdf import PdfReader
R=Path(__file__).resolve().parent
M=json.loads((R/'cad/componentes-posiciones.json').read_text(encoding='utf8'))
P=json.loads((R/'cad/parametros.json').read_text(encoding='utf8'))
checks=[]
def check(name,condition):
    checks.append({'comprobacion':name,'cumple':bool(condition)})
    if not condition:print('FALLO',name)

def overlap(a,b):
    return all(min(a[i+3],b[i+3])-max(a[i],b[i])>1e-4 for i in range(3))

# Exactas para envolventes axis-aligned principales, no tornillos/contactos intencionales.
sel=['Perfboard_150x90','BBB_PCB','SG90_cuerpo','SW2_final_carrera','SW287_cuerpo','F1_portafusible']
blocks=[m for m in M if m['node'] in ['A','B'] and (m['id'][2:] in sel or m['id'].endswith('_LDR_modulo') or m['id'].endswith('_modulo'))]
collisions=[]
for i,a in enumerate(blocks):
    for b in blocks[i+1:]:
        if overlap(a['bbox'],b['bbox']):collisions.append([a['id'],b['id']])
check('envolventes principales sin interseccion',not collisions)
check('dos bases MDF',[x['id'] for x in M if x['id'].endswith('MDF_300x200')]==['A_MDF_300x200','B_MDF_300x200'])
for n in ['A','B']:
    for role in ['BBB_PCB','Perfboard_150x90','SG90_cuerpo','SW2_final_carrera','SW287_cuerpo']:
        check(n+' '+role,len([x for x in M if x['id']==n+'_'+role])==1)
    below=[x['bbox'][2]-P['mdf_t'] for x in M if x['node']==n and x['id'].startswith(n+'_P2_W')]
    check('soldadura-modelo '+n+' libre MDF>=3mm',min(below)>=3)
check('PVC dentro de1000mm con kerf3',2*P['pvc_length']+6<=1000)
check('manguera dentro de1000mm',2*P['hose_length']<=1000)
check('separacion BBB-PCB20mm',P['bbb_x']-(P['board_x']+150)>=20)
h=list(csv.DictReader((R/'planos/perforaciones.csv').open(encoding='utf-8-sig')))
check('agujeros dentro deMDF',all(float(x['borde_mm'])>0 for x in h))
check('todos los agujeros identifican estado pendiente/propuesta',all('PENDIENTE' in x['estado'] or 'PROPUESTA' in x['estado'] for x in h))
spec=importlib.util.spec_from_file_location('registro',R/'calibracion/registro.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
result=module.evaluate(str(R/'calibracion/muestras.csv'));check('registros vacios NO_PROBADO',result['estado']=='NO_PROBADO')
with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)/'m.csv'
    def put(rows):
        with p.open('w',newline='',encoding='utf8') as f:w=csv.DictWriter(f,fieldnames=module.FIELDS);w.writeheader();w.writerows(rows)
    rows=[]
    for i,b in enumerate('010101'):
        r={k:'sintetico' for k in module.FIELDS};r.update(ensayo='TEST',medio='C0',sentido='AB',tick=str(i),esperado=b,observado=b,t_orden_s=str(i),t_estable_s=str(i+.01),flancos='1',v_bajo='0.1',v_alto='3.2',resolucion_s='.001');rows.append(r)
    put(rows);check('datos sinteticos coinciden sin cerrar tareas',module.evaluate(str(p))['resultados'][0]['estado']=='COINCIDE_PATRON_REQUIERE_REVISION')
    rows[1]['observado']='0';put(rows);check('detecta bit incorrecto',module.evaluate(str(p))['resultados'][0]['estado']=='FALLO_REGISTRO')
    rows[1]['observado']='1';rows[1]['tick']='0';put(rows);check('detecta tick duplicado',module.evaluate(str(p))['resultados'][0]['estado']=='FALLO_REGISTRO')
    rows[1]['tick']='1';rows[1]['v_alto']='nan';put(rows);check('rechaza NaN',module.evaluate(str(p))['resultados'][0]['estado']=='FALLO_REGISTRO')

for n in ['A','B','Global']:
    for ext in ['FCStd','step','obj','mtl']:check(n+' '+ext,(R/'cad'/('TRAMA3_'+n+'.'+ext)).stat().st_size>100)
for n in ['A','B']:
    pdf=PdfReader(R/'planos'/('MDF-'+n+'-perforaciones.pdf'))
    check('plantilla '+n+' 3paginas A3 y2A4',len(pdf.pages)==3)
    check('A3 real',abs(float(pdf.pages[0].mediabox.width)-420*72/25.4)<.01)
    check('A4 real',abs(float(pdf.pages[1].mediabox.width)-210*72/25.4)<.01)
report={'estado':'PASS_OFFLINE' if all(c['cumple'] for c in checks) else 'FALLO_OFFLINE','alcance':'No valida hardware ni todos los contactos CAD','colisiones_envolventes':collisions,'envolventes_comparadas':len(blocks),'comprobaciones':checks,'fisico':'NO_PROBADO'}
(R/'evidencias/cabida.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
print(report['estado'],len(checks),'comprobaciones');sys.exit(0 if report['estado']=='PASS_OFFLINE' else 1)
