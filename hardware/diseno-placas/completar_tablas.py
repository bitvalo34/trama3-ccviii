from pathlib import Path
import json,csv
R=Path(__file__).resolve().parent;D=json.loads((R/'netlist/diseno.json').read_text(encoding='utf8'))
def write(name,rows):
 with (R/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rows=[]
for e in D['external']:
 if e['ref']=='MOD3':lens=100
 elif e['ref']=='Q6':lens=25
 elif e['ref']=='SW1':lens=150
 else:lens=200
 conn=next(c for c in D['components'] if c['ref']==e['connect'])
 for pin,net in e['pins'].items():
  if net is None:continue
  match=[p for p in conn['pins'] if p['net']==net]
  assert len(match)==1
  p=match[0];power=net.startswith('+5') or net=='GND_ACT'
  rows.append(dict(id=f'H{len(rows)+1:02}',aplica='A y B',origen=f"{conn['ref']}.{p['number']} ({p['hole']})",destino=f"{e['ref']}.{pin}",red=net,longitud_reserva_mm=lens,conductor='22AWG flexible' if power else '26AWG flexible',nota='NC/AO libres. Ver serigrafia real; no asumir ordinal del modulo.'))
for node,other in [('A','B'),('B','A')]:
 for pin in [1,2]:rows.append(dict(id=f'H{len(rows)+1:02}',aplica=f'{node}->{other}',origen=f'J9.{node}.{pin}',destino=f'J8.{other}.{pin}',red='par opto remoto '+str(pin),longitud_reserva_mm=500,conductor='26AWG aislado, par trenzado',nota='Sin conductor GND entre nodos; identificar + y -. Ajustar longitud a mesa real.'))
write('soldadura/arneses-externos.csv',rows)
p=[]
for c in D['components']:
 if c['ref']=='NT1' or c['ref'].startswith('JP'):
  ref=c['ref'];is_en=ref in ['JP10','JP11','JP12']
  p.append(dict(ref=ref,funcion=c['value'],perforaciones=' / '.join(x['hole'] for x in c['pins']),inicial='2-3 OFF' if is_en else '1-2 permanente 22AWG' if ref=='NT1' else 'ABIERTO',uso='1-2 habilitado; 2-3 deshabilitado' if is_en else 'ver guia-montaje.md',redes=' / '.join(str(x['net']) for x in c['pins'])))
write('soldadura/puentes.csv',p)
# Inventario del ensamblaje completo, incluye externos y zocalo por separado.
rows=[]
new_refs={'R31','R15','R28','R11','R14','R16','R29','R23','R24','R25','R30','J14','D1'}
for c in D['components']:
 compra='ADICIONAL; no declarado adquirido' if c['ref'] in new_refs else 'PARCIAL: 2 existentes / 6 totales; comprar 4' if c['ref'] in {'Q3','Q4','Q5'} else 'DNP; no comprar por defecto' if 'DNP' in c['value'] else 'Existente o compra previa considerada disponible para diseño'
 rows.append(dict(ref=c['ref'],cantidad_ambos_nodos=2,valor=c['value'],montar='NO (DNP)' if 'DNP' in c['value'] else 'SI',ubicacion='placa',estado=c['status'],adquisicion=compra))
for e in D['external']:rows.append(dict(ref=e['ref'],cantidad_ambos_nodos=2,valor=e['value'],montar='ALTERNATIVA' if e['ref']=='MOD3' else 'SI',ubicacion=e['connect'],estado=e['status'],adquisicion='ADICIONAL; seleccionar y comprar' if e['ref'] in {'Q6','SW1'} else 'Existente o previsto; verificar especificacion'))
rows.append(dict(ref='ZOCALO_U1',cantidad_ambos_nodos=2,valor='Incluido en volumen U1; DIP28 7.62mm',montar='SI',ubicacion='U1',estado='Existente/previsto; no duplicar compra'))
rows.append(dict(ref='CAPUCHONES_JP',cantidad_ambos_nodos=14,valor='2.54mm; seis EN y ocho enlaces GPIO',montar='SEGUN CONFIGURACION',ubicacion='JP4-7 y JP10-12',estado='Medidas por confirmar',adquisicion='ADICIONAL; 20 si se desean reservas'))
rows.append(dict(ref='ADAPTADOR_Q6',cantidad_ambos_nodos=2,valor='SOT23, G/S/D; reserva 10x10mm',montar='SI',ubicacion='Q6/J12',estado='Corriente y dimensiones por confirmar',adquisicion='ADICIONAL; seleccionar y comprar'))
write('netlist/BOM-ensamble.csv',rows)
print('Arneses, puentes y BOM generados')
