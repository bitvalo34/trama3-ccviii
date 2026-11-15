"""FreeCAD 1.1 Python. Unidades mm. Regenerar desde parametros.json.
No controla hardware. Geometria aproximada identificada, circuito snapshot P2.
"""
from pathlib import Path
import json, math, csv
import FreeCAD as App, Part

R=Path(__file__).resolve().parent.parent
P=json.loads((R/'cad/parametros.json').read_text(encoding='utf-8'))
D=json.loads((R/'fuentes/T51-P2-LOCAL/diseno.json').read_text(encoding='utf-8'))
V=App.Vector
T=P['mdf_t']; TOTAL=2*P['mdf_y']+P['gap']
COL={'mdf':(.65,.43,.24),'pcb':(.62,.37,.16),'bbb':(.12,.16,.19),'blue':(.08,.30,.72),'metal':(.68,.71,.73),'black':(.09,.10,.12),'opt':(.82,.83,.77),'sound':(.18,.58,.60),'nylon':(.92,.66,.09),'clock':(.56,.23,.67),'power':(.78,.14,.13),'gpio':(.1,.45,.23),'foam':(.25,.26,.29)}
META=[]; HOLES=[]; active=None; node=None; shapes=[]

def tr(shape):
    s=shape.copy()
    if node=='B':
        s.rotate(V(0,0,0),V(0,0,1),180);s.translate(V(P['mdf_x'],TOTAL,0))
    return s

def obj(name,shape,color,kind='pieza',status='PROVISIONAL: cotejar pieza real'):
    o=active.addObject('PartDesign::Feature',(node+'_' if node else '')+name)
    o.Label=(node+' / ' if node else '')+name.replace('_',' ')
    o.Shape=tr(shape) if node else shape
    for prop,val in [('Estado',status),('Funcion',kind),('Revision',P['revision'])]:
        o.addProperty('App::PropertyString',prop,'Trazabilidad');setattr(o,prop,val)
    rgb=COL.get(color,color);o.addProperty('App::PropertyColor','ColorReferencia','Trazabilidad');o.ColorReferencia=rgb
    if App.GuiUp:
        o.ViewObject.ShapeColor=rgb;o.ViewObject.LineColor=(.1,.1,.1);o.ViewObject.DisplayMode='Flat Lines'
    shapes.append(o)
    b=o.Shape.BoundBox
    META.append({'id':o.Name,'node':node or 'enlace','kind':kind,'color':rgb,'bbox':[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]})
    return o

def box(name,x,y,z,w,h,d,color,kind='pieza'):
    return obj(name,Part.makeBox(w,h,d,V(x,y,z)),color,kind)

def cylshape(a,b,r):
    a,b=V(*a),V(*b);v=b-a
    return Part.makeCylinder(r,v.Length,a,v)

def route(name,pts,r,color,kind='cable local'):
    parts=[cylshape(a,b,r) for a,b in zip(pts,pts[1:]) if sum((x-y)**2 for x,y in zip(a,b))>1e-9]
    return obj(name,Part.makeCompound(parts),color,kind)

def cyl(name,x,y,z,r,h,color):return obj(name,Part.makeCylinder(r,h,V(x,y,z)),color)

def hole(ref,x,y,diam,component,fix,spacer='no',state='PENDIENTE: transferir desde pieza real'):
    HOLES.append({'id':node+'-'+ref,'nodo':node,'x_mm':round(x,3),'y_mm':round(y,3),'diametro_mm':diam,'componente':component,'fijacion':fix,'arandela':'plastica en PCB; metal ancha en MDF','separador':spacer,'borde_mm':round(min(x,y,300-x,200-y)-diam/2,3),'estado':state})

def fastener(name,x,y,z,stand,component):
    cyl(name+'_separador',x,y,T,2.8,stand,'metal' if component=='soporte' else 'opt')
    cyl(name+'_tornillo',x,y,0,1.5,z+2,'metal')
    cyl(name+'_cabeza',x,y,z,2.7,2,'metal')

def ring(name,x,y,z,r=4):
    # ojo cerrado vertical, plane XZ; pata independiente sin atravesar la base
    s=Part.makeTorus(r,.65,V(x,y,z),V(0,1,0))
    obj(name,s,'metal','armella; altura por medir')
    route(name+'_pata',[(x,y,T),(x,y,z-r)],.85,'metal','fijacion')

def spring(name,a,b):
    # representacion helicoidal sin atribuir constante elastica
    aa,bb=V(*a),V(*b);delta=bb-aa;L=delta.Length
    axis=delta.normalize();u=axis.cross(V(1,0,0));u.normalize();v=axis.cross(u)
    pts=[]
    for i in range(101):
        f=i/100;angle=f*10*2*math.pi
        p=aa+axis*(L*f)+(u*math.cos(angle)+v*math.sin(angle))*P['spring_radius']
        pts.append((p.x,p.y,p.z))
    route(name,pts,.45,'metal','resorte; k y precarga SIN MEDIR')

def board():
    x,y=P['board_x'],P['board_y'];z=T+P['board_standoff']
    base=Part.makeBox(150,90,1.6,V(x,y,z))
    # huecos nominales de fijacion; NO son plantilla medida de perfboard
    for i,(u,v) in enumerate([(4,4),(146,4),(4,86),(146,86)]):
        base=base.cut(Part.makeCylinder(1.6,2,V(x+u,y+v,z)))
        hole('PCB'+str(i+1),x+u,y+v,3.2,'Perfboard P2','M3 longitud calculada',str(P['board_standoff']))
        fastener('PCB'+str(i+1),x+u,y+v,z,P['board_standoff'],'pcb')
    obj('Perfboard_150x90',base,'pcb','placa soldada P2, rotacion rigida 90 grados')
    # local P2 (x,150-y) -> montaje (y, x), una rotacion sin espejo
    def pt(px,py,pz):return (x+py,y+px,z+pz)
    for c in D['components']:
        cx,cy,w,h,ht=c['box'];kind=c['kind'];name=c['ref']
        if kind=='electro':s=Part.makeCylinder(w/2,ht,V(*pt(cx+w/2,cy+h/2,1.6)))
        elif kind in ['R','diode']:
            a=pt(cx,cy+h/2,3);b=pt(cx+6.4,cy+h/2,3);s=cylshape(a,b,1.3)
        else:s=Part.makeBox(h,w,ht,V(*pt(cx,cy,1.6)))
        col='blue' if kind=='terminal' else 'metal' if kind in ['solderpads','test','link'] else 'opt' if kind=='R' else 'black'
        o=obj('P2_'+name,s,col,'referencia P2: '+c['value']);o.addProperty('App::PropertyString','Terminales');o.Terminales='; '.join(p['number']+'='+str(p['net']) for p in c['pins'])
        if c['pins']:
            obj('P2_'+name+'_pins',Part.makeCompound([Part.makeCylinder(.3,4,V(*pt(p['x'],p['y'],-1.2))) for p in c['pins']]),'metal','terminales referencia')
    # arnes inferior real de referencia, separado de MDF por 12 mm provisionales
    for wire in D['wires']:
        pts=[pt(*p) for p in wire['path']]
        if len(pts)>1:route('P2_'+wire['id'],pts,.5 if wire['wire'].startswith('22') else .32,'gpio','cable inferior referencia P2')
    # trama parcial de islas visible, sin recargar malla con 1792 cilindros
    pads=[]
    for ix in range(4,147,5):
        for iy in [6,84]:pads.append(Part.makeCylinder(.7,.1,V(x+ix,y+iy,z+1.6)))
    obj('Reticula_referencia',Part.makeCompound(pads),'metal','representacion parcial; no patron de taladro')

def bbb():
    x,y=P['bbb_x'],P['bbb_y'];z=T+P['bbb_standoff'];L=P['bbb_length'];W=P['bbb_width']
    box('BBB_PCB',x,y,z,L,W,1.6,'bbb','huella fabricante; fijaciones por transferir')
    for ref,yy in [('P8',y+2),('P9',y+W-7)]:
        box('BBB_'+ref,x+19,yy,z+1.6,58.4,5.1,8.5,'black','acceso vertical al header')
        holes=[]
        for i in range(23):
            for j in range(2):holes.append(Part.makeCylinder(.45,.2,V(x+20+i*2.54,yy+1.2+j*2.54,z+10.1)))
        obj('BBB_'+ref+'_contactos',Part.makeCompound(holes),'metal')
    box('BBB_CPU',x+35,y+18,z+1.6,14,14,2,'black')
    box('BBB_RJ45',x,y+15,z+1.6,21,16,13,'metal','puerto sin enlace de datos entre nodos')
    box('BBB_USB_A',x+L-17,y+18,z+1.6,17,14,13,'metal')
    box('BBB_MiniUSB',x+4,y-1,z+1.6,8,7,4,'metal','acceso desde borde trasero')
    box('BBB_microHDMI',x+35,y-1,z+1.6,8,6,3,'metal')
    # cotas nominales de zonas de soporte, no patron mecanico certificado
    for i,(u,v) in enumerate([(4,4),(L-4,4),(4,W-4),(L-4,W-4)]):
        hole('BBB'+str(i+1),x+u,y+v,3.2,'BBB: posicion candidata','M3; comprobar agujero real',str(P['bbb_standoff']))
        fastener('BBB'+str(i+1),x+u,y+v,z,P['bbb_standoff'],'bbb')
    route('BBB_alimentacion',[(x+8,y-1,z+4),(x+8,0,z+4),(x+8,-20,z+4)],1.7,'black','Mini USB individual; cable no enlaza nodos')

def lane_local(globalx):return globalx if node=='A' else P['mdf_x']-globalx

def external():
    # Roles se intercambian en el otro extremo; nunca reflejar PCB ni pinouts.
    for direction in ['AB','BA']:
        tx=(node==direction[0]);x=lane_local(P['lanes']['C0_'+direction]);z=T+P['optic_z'];y=(TOTAL-P['pvc_length'])/2
        # cuna reutilizable / calce recortado de material disponible, dimensiones a verificar
        box('C0_'+direction+'_calce',x-P['support_w']/2,173,T,P['support_w'],18,P['support_h'],'foam','calce firme; altura editable debe coincidir con eje menos radio PVC')
        ringShape=Part.makeCylinder(P['pvc_od']/2+1,8,V(x,178,z),V(0,1,0)).cut(Part.makeCylinder(P['pvc_od']/2,8,V(x,178,z),V(0,1,0)))
        obj('C0_'+direction+'_abrazadera',ringShape,'metal','abrazadera 1 pulgada: comprobar diametro')
        for i,dx in enumerate([-18,18]):hole('PVC'+direction+str(i),x+dx,181,3.2,'abrazadera PVC','tornillo disponible; medir',state='PENDIENTE paso real abrazadera')
        # sensor externo; solo LED/LDR mira al tubo; PCB nunca forzado dentro
        plate=Part.makeBox(34,2,34,V(x-17,y-2,z-17)).cut(Part.makeCylinder(3,3,V(x,y-3,z),V(0,1,0)))
        obj('C0_'+direction+'_tapa',plate,'black','tapa opaca desmontable con pasacables')
        if tx:
            obj('C0_'+direction+'_LED',Part.makeCylinder(2.5,5,V(x,y-1,z),V(0,1,0)),'power','LED TX')
        else:
            box('C0_'+direction+'_LDR_modulo',x-7,y-10,z-16,14,1.6,32,'blue','modulo externo 32x14 referencia P2; montaje vertical')
            obj('C0_'+direction+'_LDR',Part.makeCylinder(2.5,3,V(x,y-3,z),V(0,1,0)),'pcb','LDR RX')
            box('C0_'+direction+'_pot',x+4,y-15,z-4,5,5,5,'blue','potenciometro accesible desde atras')
        # cincho como retencion tapa/modulo, sin cubrir zona sensible
    for direction in ['AB','BA']:
        tx=(node==direction[0]);x=lane_local(P['lanes']['C1_'+direction]);z=T+P['audio_z'];y=160
        box('C1_'+direction+'_espuma',x-12,y-24,T,24,25,12,'foam','aislante vibracion; espesor provisional')
        # adaptador hueco de manga flexible, no obstruye sonido
        a=Part.makeCylinder(12,12,V(x,y-12,z),V(0,1,0));b=Part.makeCylinder(6.35,13,V(x,y-12.5,z),V(0,1,0))
        obj('C1_'+direction+'_manga',a.cut(b),'foam','acople hueco blando; medir diametros')
        if tx:obj('C1_'+direction+'_buzzer',Part.makeCylinder(6,9,V(x,y-20,z),V(0,1,0)),'black','buzzer activo 5V; pinout real')
        else:
            box('C1_'+direction+'_modulo',x-8.5,y-47,z-8,17,45,1.6,'blue','modulo sonido 45x17 referencia P2; variante real por medir')
            obj('C1_'+direction+'_microfono',Part.makeCylinder(4.5,6,V(x,y-18,z),V(0,1,0)),'metal','microfono sin espuma en apertura')
        for i,dx in enumerate([-12,12]):hole('AUD'+direction+str(i),x+dx,180,3.2,'cincho manguera','cincho con holgura',state='PROPUESTA: confirmar ruta libre')
    # Servo vertical y mecanismo receptor por tension sobre palanca.
    txdir='AB' if node=='A' else 'BA';rxdir='BA' if node=='A' else 'AB'
    sx=lane_local(P['lanes']['C2_'+txdir]);sy=P['servo_y'];sz=T+5
    box('SG90_base',sx-17,sy-9,T,34,32,5,'black','base comprada; patron pendiente')
    box('SG90_cuerpo',sx-11.5,sy,sz,23,12.2,29,'blue','referencia TowerPro; cotejar lote')
    box('SG90_orejas',sx-16,sy,sz+20,32,12.2,2,'blue')
    cyl('SG90_eje',sx,sy+8,sz+29,2.4,2,'opt')
    hornz=T+P['nylon_z'];route('SG90_brazo',[(sx,sy+8,hornz),(sx+P['servo_radius'],sy+8,hornz)],2,'opt','brazo r8; orientado perpendicular al tiro')
    for i,dx in enumerate([-13,13]):hole('SER'+str(i+1),sx+dx,sy+6,3.2,'base servo','M3x16 si pila permite',state='PENDIENTE: transferir base comprada')
    ring('Guia_TX',sx+P['servo_radius'],P['eye_y'],hornz)
    hole('E_TX',sx+P['servo_radius'],P['eye_y'],2,'armella TX','piloto segun rosca real')
    route('Nylon_local_TX',[(sx+P['servo_radius'],sy+8,hornz),(sx+P['servo_radius'],P['eye_y'],hornz),(sx,200,hornz)],.25,'nylon','nylon 0.5 mm')
    rx=lane_local(P['lanes']['C2_'+rxdir]);ry=P['switch_y']
    box('SW2_escuadra_base',rx-12,ry-2,T,24,25,2,'metal','escuadra 1 pulgada; dimensiones por medir')
    box('SW2_escuadra_vertical',rx-12,ry,T+2,24,2,25,'metal')
    box('SW2_final_carrera',rx-14,ry+2,T+9,28,16,15,'black','envolvente 28x16x15 P2; COM/NO; NO es SW287')
    # Palanca desde pivote hacia frente, nylon tira hacia ojo mas bajo.
    route('SW2_palanca',[(rx,ry+4,T+25),(rx,ry+24,T+32)],1,'metal','palanca: solo atar en extremo reforzado sin deformar')
    ring('Guia_RX',rx,P['eye_y'],T+P['eye_rx_z'])
    route('Nylon_local_RX',[(rx,200,T+P['nylon_z']),(rx,P['eye_y'],T+P['eye_rx_z']),(rx,ry+24,T+32)],.25,'nylon','tiro inclinado deprime palanca')
    spring('Resorte_retorno',(rx,ry+24,T+32),(rx,ry-13,T+43))
    ring('Ancla_retorno',rx,ry-13,T+43)
    for ref,xx,yy in [('E_RX',rx,P['eye_y']),('E_RET',rx,ry-13)]:hole(ref,xx,yy,2,'armella','piloto segun rosca real')
    for i,dx in enumerate([-8,8]):hole('SW2_'+str(i),rx+dx,ry+12,3.2,'escuadra switch','M3x16 si pila permite')
    # SW287 elevado en escuadra, accesible por lateral derecho.
    swx,swy=250,96
    box('SW287_escuadra',swx-13,swy-13,T,26,26,2,'metal')
    box('SW287_panel_vertical',swx-13,swy-13,T+2,26,2,23,'metal')
    panel=Part.makeBox(26,26,2,V(swx-13,swy-13,T+25)).cut(Part.makeCylinder(6,3,V(swx,swy,T+24.5)))
    obj('SW287_panel_horizontal',panel,'metal','repisa perforada; comprobar escuadra real')
    box('SW287_cuerpo',swx-15,swy-10,T+5,30,25,20,'black','envolvente provisional; terminales aislados')
    cyl('SW287_casquillo',swx,swy,T+25,6,7,'metal')
    route('SW287_palanca',[(swx,swy,T+32),(swx+5,swy,T+49)],2.5,'metal','OFF mantenimiento')
    for i,dx in enumerate([-9,9]):hole('SW1_'+str(i),swx+dx,swy,3.2,'soporte SW287','M3x16; confirmar soporte')
    # F1 fuera de la perfboard y accesible; fusible no caracterizado
    box('F1_portafusible',186,88,T+3,35,12,12,'black','F1 provisional T08')
    for i,fx in enumerate([182,225]):hole('F1_CINCHO'+str(i),fx,94,3.2,'portafusibleF1','cincho; no tuerca',state='PROPUESTA: comprobar acceso portafusible')
    route('F1_cincho',[(182,94,T),(182,94,T+16),(225,94,T+16),(225,94,T)],.8,'black','retencion portafusible; permitir abrirlo')
    # rutas: potencia derecha, senales a y115, reloj por bordes
    route('Arnes_BBB_J10',[(x,y,T+27) for x,y in [(210,60),(177,75),(177,112),(145,112),(145,65)]],1.5,'gpio','diez hilos desmontables; ruta conceptual')
    route('Arnes_potencia',[(30,25,T+22),(30,8,T+5),(285,8,T+5),(285,92,T+5),(250,96,T+10)],1.5,'power','potencia local; sin NEG_IN comun')
    route('Arnes_servo',[(250,96,T+8),(290,115,T+8),(sx,122,T+8),(sx,sy,T+8)],1.1,'power','GND/+5V_SERVO/SIG agrupados; nunca sobre brazo')
    for name,xx in [('opticTX',lane_local(P['lanes']['C0_'+txdir])),('opticRX',lane_local(P['lanes']['C0_'+rxdir])),('audioTX',lane_local(P['lanes']['C1_'+txdir])),('audioRX',lane_local(P['lanes']['C1_'+rxdir]))]:
        route('Arnes_'+name,[(140,90,T+22),(170,115,T+8),(xx,115,T+8),(xx,132,T+25)],.9,'gpio' if 'RX' in name else 'power','ruta local prevista; terminal exacto en CSV')
    route('Arnes_SW2',[(155,95,T+22),(175,119,T+7),(rx,119,T+7),(rx,ry,T+17)],.7,'gpio')
    for dir,xedge in [('AB',5),('BA',295)]:
        lx=lane_local(xedge)
        route('CLK_'+dir+'_local',[(100,95,T+22),(100,112,T+7),(lx,112,T+7),(lx,200,T+7)],1,'clock','par trenzado, sin GND remoto')

def make_node(n):
    global node
    node=n
    box('MDF_300x200',0,0,0,P['mdf_x'],P['mdf_y'],T,'mdf','base; espesor provisional')
    board();bbb();external()
    node=None

def links():
    z=T+P['optic_z'];start=(TOTAL-P['pvc_length'])/2
    for d in ['AB','BA']:
        x=P['lanes']['C0_'+d]
        s=Part.makeCylinder(P['pvc_od']/2,P['pvc_length'],V(x,start,z),V(0,1,0)).cut(Part.makeCylinder(P['pvc_id']/2,P['pvc_length']+.2,V(x,start-.1,z),V(0,1,0)))
        obj('C0_'+d+'_PVC_480',s,'opt','conducto optico hueco; OD/ID provisionales')
        # parabola con longitud de eje calculada igual al corte de manguera
        ax=P['lanes']['C1_'+d];dy=TOTAL-320;target=P['hose_length']
        if target<dy:raise ValueError('Manguera menor que distancia entre bocas')
        def path(H):return [(ax,160+dy*i/100,T+P['audio_z']+4*H*(i/100)*(1-i/100)) for i in range(101)]
        def length(pts):return sum(math.dist(a,b) for a,b in zip(pts,pts[1:]))
        lo,hi=0,300
        for i in range(50):
            mid=(lo+hi)/2
            if length(path(mid))>target:hi=mid
            else:lo=mid
        pts=path((lo+hi)/2)
        # sweep suave hueco a lo largo de BSpline (longitud numerica eje en evidencia)
        curve=Part.BSplineCurve();curve.interpolate([V(*p) for p in pts[::5]])
        spine=Part.Wire(curve.toShape());normal=V(*pts[1])-V(*pts[0])
        ow=Part.Wire(Part.makeCircle(P['hose_od']/2,V(*pts[0]),normal));iw=Part.Wire(Part.makeCircle(P['hose_id']/2,V(*pts[0]),normal))
        s=spine.makePipeShell([ow],True,False).cut(spine.makePipeShell([iw],True,False))
        obj('C1_'+d+'_manguera_480',s,'sound','manguera hueca; curva ilustrativa ajustable')
        nx=P['lanes']['C2_'+d];nz=T+P['nylon_z']
        # resorte serie de proteccion junto al extremo TX, fuera de MDF
        a,b=(205,205+P['spring_free_length']) if d=='AB' else (TOTAL-205-P['spring_free_length'],TOTAL-205)
        route('C2_'+d+'_nylon1',[(nx,200,nz),(nx,a,nz)],.25,'nylon','nylon 0.5 mm')
        spring('C2_'+d+'_resorte_serie',(nx,a,nz),(nx,b,nz))
        route('C2_'+d+'_nylon2',[(nx,b,nz),(nx,TOTAL-200,nz)],.25,'nylon','nylon 0.5 mm')
    for d,x in [('AB',5),('BA',295)]:
        # Dos conductores identificables y trenzado simplificado
        for k in range(2):
            pts=[]
            for i in range(121):
                yy=200+P['gap']*i/120;angle=2*math.pi*12*i/120+k*math.pi
                pts.append((x+.65*math.cos(angle),yy,T+7+.65*math.sin(angle)))
            route('CLK_'+d+('_mas' if k==0 else '_menos'),pts,.35,'clock' if k==0 else 'black','par reloj aislado; no GND')

def export(which):
    global active,shapes,META,HOLES
    shapes=[];META=[];HOLES=[]
    active=App.newDocument('TRAMA3_'+which)
    cfg=active.addObject('Spreadsheet::Sheet','Parametros')
    cfg.set('A1','PARAMETROS DE REFERENCIA; editar JSON y regenerar')
    row=2
    for k,v in P.items():
        cfg.set('A'+str(row),k);cfg.set('B'+str(row),str(v));row+=1
    if which=='Global':make_node('A');make_node('B');links()
    else:make_node(which)
    active.recompute()
    invalid=[o.Name for o in shapes if o.Shape.isNull() or not o.Shape.isValid()]
    if invalid:raise ValueError('Geometrias invalidas '+str(invalid))
    # guardar B individual en coordenadas locales para plantilla
    if which=='B':
        for o in shapes:
            s=o.Shape.copy();s.translate(V(-P['mdf_x'],-TOTAL,0));s.rotate(V(),V(0,0,1),180);o.Shape=s
        active.recompute()
    active.saveAs(str(R/'cad'/('TRAMA3_'+which+'.FCStd')))
    Part.export(shapes,str(R/'cad'/('TRAMA3_'+which+'.step')))
    # Malla OBJ de referencia con grupos y colores; no sustituye STEP.
    objlines=['mtllib TRAMA3_'+which+'.mtl'];mtl=[];offset=1
    for idx,o in enumerate(shapes):
        verts,faces=o.Shape.tessellate(.7)
        color=tuple(o.ColorReferencia[:3]);mat='mat'+str(idx)
        mtl+=['newmtl '+mat,'Kd '+' '.join(map(str,color)),'Ka 0.2 0.2 0.2']
        objlines+=['g '+o.Name,'usemtl '+mat]
        objlines+=['v %.4f %.4f %.4f'%(v.x,v.y,v.z) for v in verts]
        objlines+=['f %d %d %d'%(a+offset,b+offset,c+offset) for a,b,c in faces];offset+=len(verts)
    (R/'cad'/('TRAMA3_'+which+'.obj')).write_text('\n'.join(objlines),encoding='utf-8')
    (R/'cad'/('TRAMA3_'+which+'.mtl')).write_text('\n'.join(mtl),encoding='utf-8')
    if which=='Global':
        with (R/'planos/perforaciones.csv').open('w',newline='',encoding='utf-8-sig') as f:
            w=csv.DictWriter(f,fieldnames=list(HOLES[0]));w.writeheader();w.writerows(HOLES)
        (R/'cad/componentes-posiciones.json').write_text(json.dumps(META,indent=2),encoding='utf-8')
        (R/'evidencias/cad-validacion.json').write_text(json.dumps({'estado':'VALIDO_GEOMETRIA_NOMINAL_NO_VALIDACION_FISICA','objetos':len(shapes),'invalidos':invalid,'base_mm':[300,200,T],'gap_mm':P['gap'],'longitud_total_mm':TOTAL,'PVC_uso_mm':2*P['pvc_length']+6,'manguera_uso_mm':2*P['hose_length'],'carrera_cuerda_mm':2*P['servo_radius']*math.sin(math.radians(P['servo_delta_deg']/2)),'advertencias':['Sin mediciones de piezas ni ensayo electrico','No prueba exhaustiva de colisiones entre todos los solidos','Conectores/soportes/huellas provisionales; transferir agujeros','Modelo resorte no implica k ni par','Lado soldado puede sobresalir mas que modelo: medir']},indent=2),encoding='utf-8')
    if App.GuiUp:
        import FreeCADGui as Gui
        from PySide import QtWidgets
        view=Gui.activeDocument().activeView()
        for name,method in [('isometrica','viewAxonometric'),('superior','viewTop'),('lateral','viewRight'),('frontal','viewFront')]:
            getattr(view,method)();view.fitAll();QtWidgets.QApplication.processEvents()
            view.saveImage(str(R/'planos'/(which+'-'+name+'.png')),1800,1300,'White')
        if which=='Global':
            for o in shapes:o.ViewObject.Visibility=any(k in o.Name for k in ['C2_','SG90','SW2','Guia_','Ancla_','Resorte','Nylon','MDF'])
            view.viewAxonometric();view.fitAll();QtWidgets.QApplication.processEvents();view.saveImage(str(R/'planos/Global-nylon.png'),1800,1300,'White')
            for o in shapes:o.ViewObject.Visibility=True
        view.viewAxonometric();view.fitAll();active.recompute();active.save()
    print(which,len(shapes),'shapes valid')
    App.closeDocument(active.Name)

if __name__=='__main__':
    for which in ['Global','A','B']:export(which)
