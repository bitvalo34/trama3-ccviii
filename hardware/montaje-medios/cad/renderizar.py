from pathlib import Path
import FreeCAD as App, FreeCADGui as Gui
from PySide import QtWidgets, QtCore
R=Path(__file__).resolve().parent.parent
Gui.showMainWindow()
for which in ['Global','A','B']:
    doc=App.openDocument(str(R/'cad'/('TRAMA3_'+which+'.FCStd')))
    objects=[o for o in doc.Objects if hasattr(o,'Shape')]
    for o in objects:
        o.ViewObject.Visibility=True
        o.ViewObject.ShapeColor=tuple(o.ColorReferencia[:3]);o.ViewObject.LineColor=(.17,.17,.17)
        o.ViewObject.DisplayMode='Flat Lines';o.ViewObject.LineWidth=.5
    view=Gui.activeDocument().activeView()
    view.setCameraType('Orthographic')
    if hasattr(view,'setAnimationEnabled'):view.setAnimationEnabled(False)
    for name,method in [('isometrica','viewAxonometric'),('superior','viewTop'),('lateral','viewRight'),('frontal','viewFront')]:
        getattr(view,method)();view.fitAll();QtWidgets.QApplication.processEvents()
        loop=QtCore.QEventLoop();QtCore.QTimer.singleShot(600,loop.quit);loop.exec_()
        view.saveImage(str(R/'planos'/(which+'-'+name+'.png')),1800,1300,'White')
    if which=='Global':
        for o in objects:o.ViewObject.Visibility=any(k in o.Name for k in ['C2_','SG90','SW2','Guia_','Ancla_','Resorte','Nylon','MDF'])
        view.viewAxonometric();view.fitAll();QtWidgets.QApplication.processEvents();view.saveImage(str(R/'planos/Global-nylon.png'),1800,1300,'White')
        for o in objects:o.ViewObject.Visibility=True
    view.viewAxonometric();view.fitAll();doc.recompute();doc.save();App.closeDocument(doc.Name)
(R/'evidencias/render-completado.txt').write_text('13 vistas exportadas por FreeCAD GUI. Inspeccion visual pendiente.\n',encoding='utf-8')
Gui.getMainWindow().close()
