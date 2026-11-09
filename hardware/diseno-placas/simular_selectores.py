"""Simulacion DC de la red real de resistencias/puentes de recepcion: 216 lecturas."""
from pathlib import Path
import json,csv,itertools
R=Path(__file__).resolve().parent;D=json.loads((R/'netlist/diseno.json').read_text(encoding='utf8'));C={c['ref']:c for c in D['components']}
def gauss(A,b):
 n=len(b)
 for k in range(n):
  pivot=max(range(k,n),key=lambda i:abs(A[i][k]));A[k],A[pivot]=A[pivot],A[k];b[k],b[pivot]=b[pivot],b[k]
  assert abs(A[k][k])>1e-12,'Nodo flotante'
  t=A[k][k];A[k]=[v/t for v in A[k]];b[k]/=t
  for i in range(n):
   if i==k:continue
   t=A[i][k];A[i]=[v-t*q for v,q in zip(A[i],A[k])];b[i]-=t*b[k]
 return b
def calc(mask,raw,removed=False):
 parent={}
 def find(n):
  if n not in parent:parent[n]=n
  if parent[n]!=n:parent[n]=find(parent[n])
  return parent[n]
 def join(a,b):parent[find(a)]=find(b)
 for k in range(3):
  p=C[f'JP{10+k}']['pins']
  if not removed:join(p[1]['net'],p[0 if mask&(1<<k) else 2]['net'])
  p=C[f'JP{4+k}']['pins'];join(p[0]['net'],p[1]['net'])
 fixed={find('GND_LOGIC'):0,find('+3V3_LOGIC'):3.3}
 for k,n in enumerate(['OPT_RAW','AUD_RAW','MECH_RAW']):fixed[find(n)]=3.3 if raw&(1<<k) else 0
 resist=[]
 for i in range(17,26):
  c=C['R'+str(i)];v=float(c['value'].replace('k',''))*(1000 if 'k' in c['value'] else 1)
  a,b=[find(p['net']) for p in c['pins']];resist.append((a,b,v))
 nodes=sorted({p for a,b,v in resist for p in [a,b]}-set(fixed));ix={n:i for i,n in enumerate(nodes)};A=[[0.]*len(nodes) for n in nodes];b=[0.]*len(nodes)
 for a,z,v in resist:
  if a==z:continue
  for n,m in [(a,z),(z,a)]:
   if n not in ix:continue
   i=ix[n];A[i][i]+=1/v
   if m in fixed:b[i]+=fixed[m]/v
   else:A[i][ix[m]]-=1/v
 solved={**fixed,**dict(zip(nodes,gauss(A,b)))}
 return [solved[find(n)] for n in ['OPT_BBB','AUD_BBB','MECH_BBB']]
rows=[];fail=[]
for removed in [False,True]:
 for mask in ([0] if removed else range(8)):
  for raw in range(8):
   vs=calc(mask,raw,removed)
   for k,v in enumerate(vs):
    expected=3.3 if not removed and mask&raw&(1<<k) else 0
    row=dict(puentes_retirados=removed,mask=format(mask,'03b'),raw=format(raw,'03b'),canal=k,V_GPIO=round(v,6),V_esperado=expected,pasa=abs(v-expected)<1e-6);rows.append(row)
    if not row['pasa']:fail.append(row)
with (R/'verificaciones/selectores-DC.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
result={'lecturas':len(rows),'fallos':len(fail),'modelo':'Circuito resistivo obtenido de diseno.json, nodos de DO ideales 0/3.3V, JP4-6 cerrados; solucion nodal DC. No representa flancos ni rebote.'}
(R/'verificaciones/selectores-DC.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(result)
assert not fail
