"""Render BRep mediante FreeCAD GUI; no modifica ni controla otras aplicaciones."""
from pathlib import Path
import json
import FreeCAD as App, FreeCADGui as Gui
from PySide import QtWidgets
R=Path(__file__).resolve().parent
D=json.loads((R/'netlist/diseno.json').read_text(encoding='utf8'))
colors={'POWER':(.88,.64,.3),'SERVO':(.63,.4,.25),'CORE':(.2,.45,.65),'TX':(.35,.55,.25),'RX':(.2,.6,.5),'ENABLE':(.55,.35,.7),'CLOCK':(.35,.4,.6),'CLOCK_RX':(.8,.6,.25)}
refs={c['ref']:c for c in D['components']}
Gui.showMainWindow()
for node in ['A','B']:
 doc=App.openDocument(str(R/f'cad/placa-{node}/TRAMA3_Interfaz_{node}.FCStd'))
 for o in doc.Objects:
  if not hasattr(o,'Shape'):continue
  o.ViewObject.Visibility=o.Name not in ['BoardBlank','HoleArray'] and not o.Name.endswith('_EXT')
  if o.Name=='Q6_EXT':o.ViewObject.Visibility=True
  if o.Name=='Perfboard':o.ViewObject.ShapeColor=(.70,.47,.24)
  elif o.Name=='Islas_cobre':o.ViewObject.ShapeColor=(.85,.53,.25)
  elif o.Name in refs:o.ViewObject.ShapeColor=colors[refs[o.Name]['zone']]
  elif o.Name.endswith('_Pins') or o.Name.endswith('_Bridge'):o.ViewObject.ShapeColor=(.75,.75,.77)
  elif o.Name.endswith('_Shunt'):o.ViewObject.ShapeColor=(.12,.12,.12)
  elif o.Name.startswith('W') and o.Name[1:].isdigit():
   net=next(w['net'] for w in D['wires'] if w['id']==o.Name)
   o.ViewObject.ShapeColor=(.1,.1,.12) if 'GND' in net else (.8,.12,.1) if net.startswith('+5') else (.55,.18,.65) if 'REMOTE' in net else (.1,.3,.8)
  o.ViewObject.DisplayMode='Flat Lines';o.ViewObject.LineColor=(.12,.12,.12);o.ViewObject.LineWidth=.5
 view=Gui.activeDocument().activeView()
 view.setAnimationEnabled(False) if hasattr(view,'setAnimationEnabled') else None
 for name,method in [('isometrica','viewAxonometric'),('superior','viewTop'),('inferior','viewBottom'),('lateral','viewRight'),('posterior','viewRear')]:
  getattr(view,method)()
  if name=='inferior':view.setCameraOrientation(App.Rotation(App.Vector(0,1,0),180).Q)
  view.fitAll();QtWidgets.QApplication.processEvents()
  view.saveImage(str(R/f'planos/{node}-{name}.png'),1600,1200,'White')
 view.viewAxonometric();view.fitAll();doc.recompute();doc.save();App.closeDocument(doc.Name)
print('RENDER CAD TERMINADO')
Gui.getMainWindow().close()
