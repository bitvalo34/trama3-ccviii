"""Ejecutar con Python de FreeCAD; modelos simplificados editables + STEP."""
from pathlib import Path
import json,math
import FreeCAD as App, Part
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'netlist/diseno.json').read_text(encoding='utf-8'))
V=App.Vector
def xyz(x,y,z):return V(x,150-y,z)
def body(doc,name,box,z=1.6):
 x,y,w,h,ht=box;o=doc.addObject('Part::Box',name);o.Length=w;o.Width=h;o.Height=ht;o.Placement.Base=xyz(x,y+h,z);return o
def tube(a,b,r):
 a,b=V(*a),V(*b);v=b-a
 return Part.makeCylinder(r,v.Length,a,v) if v.Length>1e-6 else Part.makeSphere(r,a)
def export(node):
 doc=App.newDocument('TRAMA3_'+node)
 board=doc.addObject('Part::Box','BoardBlank');board.Length=90;board.Width=150;board.Height=1.6
 for prop,val in [('Pitch',2.54),('HoleDiameter',1.),('MarginX',5.),('MarginY',5.)]:board.addProperty('App::PropertyLength',prop,'Reticula');setattr(board,prop,val)
 board.addProperty('App::PropertyString','Estado');board.Estado='ESTIMADO: medir placa y confirmar patron; sin autorizacion para soldar'
 holes=[]
 for r in range(56):
  for c in range(32):holes.append(Part.makeCylinder(.5,3,xyz(5+c*2.54,5+r*2.54,-.5)))
 cutter=doc.addObject('PartDesign::Feature','HoleArray');cutter.Shape=Part.makeCompound(holes)
 perf=doc.addObject('Part::Cut','Perfboard');perf.Base=board;perf.Tool=cutter
 perf.Label='Placa '+node+' - 90x150x1.6 - 1792 agujeros ESTIMADOS'
 doc.recompute()
 ring=Part.makeCylinder(.9,.035).cut(Part.makeCylinder(.5,.035))
 rings=[]
 for r in range(56):
  for c in range(32):
   q=ring.copy();q.translate(xyz(5+c*2.54,5+r*2.54,-.035));rings.append(q)
 pads=doc.addObject('PartDesign::Feature','Islas_cobre');pads.Shape=Part.makeCompound(rings);pads.Label='1792 islas individuales; diametro estimado 1.8mm'
 solids=[perf,pads]; groups={}
 for c in D['components']:
  if c['zone'] not in groups:groups[c['zone']]=doc.addObject('App::DocumentObjectGroup',c['zone'])
  ref=c['ref'];x,y,w,h,ht=c['box']
  if c['kind']=='electro':
   o=doc.addObject('Part::Cylinder',ref);o.Radius=w/2;o.Height=ht;o.Placement.Base=xyz(x+w/2,y+h/2,1.6)
  elif c['kind']=='R' or c['kind']=='diode':
   o=doc.addObject('Part::Cylinder',ref);o.Radius=1.3;o.Height=6.4;o.Placement=App.Placement(xyz(x,y+h/2,2.9),App.Rotation(V(0,0,1),V(1,0,0)))
  else:
   bbox=c['box'][:]
   if c['kind']=='header':bbox[4]=2.5
   if c['kind'] in ['solderpads','link','test']:bbox[4]=.5
   o=body(doc,ref,bbox)
  o.Label=ref+' | '+c['value'];o.addProperty('App::PropertyString','Estado');o.Estado=c['status'];o.addProperty('App::PropertyString','Nota');o.Nota=c['notes'];o.addProperty('App::PropertyString','Terminales');o.Terminales='; '.join(p['number']+':'+p['hole']+'='+str(p['net']) for p in c['pins']);groups[c['zone']].addObject(o);solids.append(o)
  pins=[]
  for p in c['pins']:
   pins.append(Part.makeCylinder(.3,8 if c['kind'] in ['header','test'] else 4,xyz(p['x'],p['y'],-1.2)))
  if c['kind'] in ['R','diode']:
   p,q=c['pins'];pins.append(tube(list(xyz(p['x'],p['y'],2.8)),list(xyz(x,y+h/2,2.9)),.25));pins.append(tube(list(xyz(q['x'],q['y'],2.8)),list(xyz(x+6.4,y+h/2,2.9)),.25))
  po=doc.addObject('PartDesign::Feature',ref+'_Pins');po.Shape=Part.makeCompound(pins);groups[c['zone']].addObject(po);solids.append(po)
  if ref=='U1':
   # Separar visualmente zocalo y cuerpo IC, volumen reservado original mantiene altura.
   o.Height=4
   ic=body(doc,'MCP23017_Body',[x+1,y+1,w-2,h-2,4],5.6);ic.Label='MCP23017 extraible; muesca hacia fila A';groups[c['zone']].addObject(ic);solids.append(ic)
 wg=doc.addObject('App::DocumentObjectGroup','Cables_inferiores')
 # Puente permanente NT1 y selectores de fallo en OFF. Otros JP abiertos.
 for ref in ['NT1','JP10','JP11','JP12']:
  cc=next(c for c in D['components'] if c['ref']==ref);ps=cc['pins'] if ref=='NT1' else cc['pins'][1:]
  aa,bb=ps;obj=doc.addObject('PartDesign::Feature',ref+'_Bridge');obj.Shape=tube(list(xyz(aa['x'],aa['y'],4)),list(xyz(bb['x'],bb['y'],4)),.55);obj.Label=ref+(' puente estrella' if ref=='NT1' else ' OFF 2-3');solids.append(obj)
  if ref!='NT1':
   sh=body(doc,ref+'_Shunt',[aa['x']-1.1,aa['y']-1.2,bb['x']-aa['x']+2.2,2.4,3],5);sh.Label=ref+' capuchon removible 2-3 OFF';solids.append(sh)
 for wire in D['wires']:
  pts=[list(xyz(*p)) for p in wire['path']];r=.6 if wire['wire'].startswith('22') else .4
  # rise to pad underside; strip only final 2mm in actual build.
  p0=pts[0];pn=pts[-1];pts=[[p0[0],p0[1],-.3]]+pts+[[pn[0],pn[1],-.3]]
  obj=doc.addObject('PartDesign::Feature',wire['id']);obj.Label=wire['id']+' '+wire['net'];obj.Shape=Part.makeCompound([tube(a,b,r) for a,b in zip(pts,pts[1:]) if a!=b]);obj.addProperty('App::PropertyString','Ruta');obj.Ruta=json.dumps(wire['path']);obj.addProperty('App::PropertyString','Conexion');obj.Conexion=wire['source']+' -> '+wire['destination'];wg.addObject(obj);solids.append(obj)
 # Componentes externos de referencia: separados, sin estructura mecanica.
 eg=doc.addObject('App::DocumentObjectGroup','Externos_referencia')
 for i,e in enumerate(D['external']):
  if e['ref']=='Q6':
   connector=next(c for c in D['components'] if c['ref']=='J12');x,y=connector['box'][:2];x-=1;y-=3;z=10
  else:x=105+(i%2)*52;y=8+(i//2)*32;z=1.6
  w,h,ht=e['size'];o=body(doc,e['ref']+'_EXT',[x,y,w,h,ht],z);o.Label=e['ref']+' '+e['value'];o.addProperty('App::PropertyString','Estado');o.Estado=e['status'];o.addProperty('App::PropertyString','Conector');o.Conector=e['connect'];eg.addObject(o)
  if e['ref']=='Q6':solids.append(o)
  if e['ref']=='Q6':
   for p in connector['pins']:
    lead=doc.addObject('PartDesign::Feature','Q6_Arnes_'+p['number']);lead.Shape=tube(list(xyz(p['x'],p['y'],1.6)),list(xyz(p['x'],p['y'],10)),.3 if p['number']=='1' else .6);lead.Label='Arnes J12.'+p['number']+' -> Q6.'+p['number'];solids.append(lead)
 doc.recompute()
 # Ocultar primitivas de construccion si se abre con GUI; colores aplicados por macro.
 out=ROOT/f'cad/placa-{node}'
 doc.saveAs(str(out/f'TRAMA3_Interfaz_{node}.FCStd'))
 Part.export(solids,str(out/f'TRAMA3_Interfaz_{node}.step'))
 # STEP y FCStd preservan BRep y objetos; no generar una malla pesada de los 1792 agujeros.
 check={'node':node,'solids':len(solids),'invalid_shapes':[o.Name for o in solids if not o.Shape.isValid()],'board_holes':1792,'note':'Volumes simplificados; externos excluidos de prueba de cabida salvo Q6. Cable aislado puede tocar aislamiento de otro cable; rutas sujetas a revision manual.'}
 (ROOT/f'verificaciones/cad-{node}.json').write_text(json.dumps(check,indent=2),encoding='utf-8')
 print(json.dumps(check));App.closeDocument(doc.Name)
for node in ['A','B']:export(node)
