#!/usr/bin/env python3
"""Utilidad offline Python 3.5+. No importa drivers ni acciona hardware."""
from __future__ import print_function
import argparse, csv, json, sys, os

FIELDS=['ensayo','medio','sentido','tick','esperado','observado','t_orden_s','t_estable_s','flancos','v_bajo','v_alto','polaridad','resolucion_s','evidencia','operador','fecha','revision_fw']

def plan(path):
    if os.path.exists(path):raise ValueError('No sobrescribir registro existente: '+path)
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['tick','t_orden_s','t_captura_s','esperado']);w.writeheader()
        for i,b in enumerate('010101'):w.writerow({'tick':i,'t_orden_s':i,'t_captura_s':i+.8,'esperado':b})

def evaluate(path):
    with open(path,'r',encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    groups={}
    for r in rows:groups.setdefault((r.get('ensayo',''),r.get('medio',''),r.get('sentido','')),[]).append(r)
    results=[]
    for key,rr in groups.items():
        issues=[];missing=[];ticks=[];lat=[];different=0
        for r in rr:
            try:
                tick=int(r.get('tick',''));ticks.append(tick)
                if tick not in range(6):issues.append('tick fuera de 0..5');continue
                if r.get('esperado')!='010101'[tick]:issues.append('patron esperado alterado')
            except (ValueError,TypeError):issues.append('tick invalido');continue
            if r.get('observado') not in ['0','1']:missing.append('observado tick '+str(tick))
            elif r['observado']!=r['esperado']:different+=1
            for field in ['t_orden_s','t_estable_s','flancos','v_bajo','v_alto','polaridad','resolucion_s','evidencia','operador','fecha','revision_fw']:
                if not r.get(field,'').strip():missing.append(field+' tick '+str(tick))
            for field in ['t_orden_s','t_estable_s','v_bajo','v_alto','resolucion_s']:
                if r.get(field,''):
                    try:
                        value=float(r[field])
                        if not __import__('math').isfinite(value):issues.append(field+' no finito')
                        if field=='resolucion_s' and value<=0:issues.append('resolucion no positiva')
                    except ValueError:issues.append(field+' no numerico')
            if r.get('t_orden_s') and r.get('t_estable_s'):
                try:
                    dt=float(r['t_estable_s'])-float(r['t_orden_s']);lat.append(dt)
                    if dt<0:issues.append('latencia negativa')
                except ValueError:pass
        if sorted(ticks)!=list(range(6)):issues.append('requiere seis ticks unicos 0..5')
        status='FALLO_REGISTRO' if issues or different else 'NO_PROBADO' if missing else 'COINCIDE_PATRON_REQUIERE_REVISION'
        results.append({'ensayo':key,'estado':status,'diferencias':different,'faltantes':missing,'problemas':issues,'retardo_max_s':max(lat) if lat else None})
    return {'estado':'NO_PROBADO' if not rows or any(r['estado']=='NO_PROBADO' for r in results) else 'REVISAR','alcance':'Solo consistencia CSV; no valida niveles, fisica, reloj, presencia acustica ni autenticidad. No cierra tareas.','resultados':results}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);sp=p.add_subparsers(dest='cmd')
    q=sp.add_parser('plan');q.add_argument('--output',required=True)
    q=sp.add_parser('evaluar');q.add_argument('--input',required=True);q.add_argument('--output',required=True)
    a=p.parse_args(argv)
    if a.cmd=='plan':plan(a.output);return 0
    if a.cmd=='evaluar':
        if os.path.abspath(a.input)==os.path.abspath(a.output):raise ValueError('Salida no puede reemplazar entrada')
        if os.path.exists(a.output):raise ValueError('Salida existe; elegir nombre nuevo')
        r=evaluate(a.input)
        with open(a.output,'w',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2)
        print(r['estado']);return 3 if r['estado']=='NO_PROBADO' else 4 if any(x['estado']=='FALLO_REGISTRO' for x in r['resultados']) else 0
    p.error('Elegir plan o evaluar')

if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError) as e:print(str(e),file=sys.stderr);sys.exit(2)
