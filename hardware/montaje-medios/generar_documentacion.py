"""Planos y manual derivados de parametros y CAD. Python reportlab/pypdfium2/Pillow."""
from pathlib import Path
import csv,json,re,html,math
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4,A3,landscape
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,CondPageBreak,Table,TableStyle,Image,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from PIL import Image as PILImage,ImageDraw,ImageFont,ImageChops
import pypdfium2 as pdfium
R=Path(__file__).resolve().parent
P=json.loads((R/'cad/parametros.json').read_text(encoding='utf8'))
M=json.loads((R/'cad/componentes-posiciones.json').read_text(encoding='utf8'))
holes=list(csv.DictReader((R/'planos/perforaciones.csv').open(encoding='utf-8-sig')))
dark=colors.HexColor('#162d3e');teal=colors.HexColor('#117d87');amber=colors.HexColor('#a45c06')

def cad_image(name):
    im=PILImage.open(R/'planos'/(name+'.png')).convert('RGB')
    bg=PILImage.new('RGB',im.size,'white');bb=ImageChops.difference(im,bg).getbbox()
    if bb:im=im.crop((max(0,bb[0]-30),max(0,bb[1]-30),min(im.width,bb[2]+30),min(im.height,bb[3]+30)))
    p=R/'evidencias/qa'/('recorte-'+name+'.png');p.parent.mkdir(exist_ok=True);im.save(p);return p,im.size

def locbox(o,node):
    x,y,z,xx,yy,zz=o['bbox']
    if node=='B':x,xx=300-xx,300-x;y,yy=400+P['gap']-yy,400+P['gap']-y
    return x,y,xx-x,yy-y

def footprint(node):
    result=[]
    selected=['Perfboard_150x90','BBB_PCB','SG90_base','SW2_final_carrera','SW287_cuerpo','F1_portafusible']
    for o in M:
        if o['node']!=node:continue
        name=o['id'][2:]
        if name in selected or re.match('C[01]_(AB|BA)_(tapa|manga|modulo)$',name):
            result.append((name,locbox(o,node),o['color']))
    return result

def boarddraw(c,node,originx,originy,crop=None):
    c.saveState();c.translate(originx*mm,originy*mm)
    if crop:
        p=c.beginPath();p.rect(0,0,165*mm,200*mm);c.clipPath(p,stroke=0);c.translate(-crop*mm,0)
    c.setLineWidth(.5);c.setStrokeColor(dark);c.rect(0,0,300*mm,200*mm)
    for v in range(0,301,10):
        c.setStrokeColor(colors.HexColor('#e2e8ec'));c.line(v*mm,0,v*mm,200*mm)
    for v in range(0,201,10):c.line(0,v*mm,300*mm,v*mm)
    for name,(x,y,w,h),color in footprint(node):
        c.setFillColor(colors.Color(*color,alpha=.14));c.setStrokeColor(colors.Color(*color));c.rect(x*mm,y*mm,w*mm,h*mm,fill=1)
        if name in ['Perfboard_150x90','BBB_PCB','SG90_base','SW2_final_carrera','SW287_cuerpo','F1_portafusible']:
            c.setFillColor(dark);c.setFont('Helvetica',6);c.drawString((x+1)*mm,(y+h/2)*mm,name.replace('_',' '))
        if name.endswith(('_tapa','_manga')):
            channel,direction,_=name.split('_');role='TX' if node==direction[0] else 'RX'
            c.setFillColor(dark);c.setFont('Helvetica-Bold',6);c.drawCentredString((x+w/2)*mm,(y-4 if channel=='C0' else y+h+3)*mm,channel+' '+role+' '+direction)
    for r in holes:
        if r['nodo']!=node:continue
        x,y=float(r['x_mm']),float(r['y_mm']);rad=float(r['diametro_mm'])/2
        c.setStrokeColor(amber);c.circle(x*mm,y*mm,rad*mm);c.line((x-2)*mm,y*mm,(x+2)*mm,y*mm);c.line(x*mm,(y-2)*mm,x*mm,(y+2)*mm)
        c.setFont('Helvetica',5);c.setFillColor(amber);c.drawString((x+2)*mm,(y+2)*mm,r['id'])
    # sistema coordenadas
    c.setStrokeColor(dark);c.setFillColor(dark);c.setFont('Helvetica-Bold',7)
    c.line(0,0,30*mm,0);c.line(0,0,0,30*mm);c.drawString(27*mm,2*mm,'X');c.drawString(2*mm,27*mm,'Y')
    c.restoreState()

def templates():
    for n in ['A','B']:
        path=R/'planos'/f'MDF-{n}-perforaciones.pdf';c=canvas.Canvas(str(path),pagesize=landscape(A3));c.setTitle('MDF '+n+' plantilla1:1 provisional')
        c.setFillColor(dark);c.setFont('Helvetica-Bold',17);c.drawString(25*mm,280*mm,'MDF '+n+' | Perforaciones y presentacion a escala 1:1')
        c.setFont('Helvetica',9);c.drawString(25*mm,272*mm,'P0 PROVISIONAL. No taladrar hasta transferir agujeros reales y comprobar huellas, espesor y tornillos.')
        boarddraw(c,n,35,45)
        c.setFont('Helvetica',9);c.drawString(35*mm,251*mm,'FRENTE Y=200 hacia el otro nodo');c.drawString(35*mm,36*mm,'TRASERA Y=0 | Origen (0,0) izquierda | mm | Contorno 300 x 200')
        c.setStrokeColor(dark);c.line(35*mm,23*mm,135*mm,23*mm);c.line(35*mm,21*mm,35*mm,25*mm);c.line(135*mm,21*mm,135*mm,25*mm)
        c.drawString(45*mm,16*mm,'100 mm: medir antes de usar. Imprimir A3 al 100%.')
        c.line(355*mm,55*mm,355*mm,155*mm);c.saveState();c.translate(360*mm,60*mm);c.rotate(90);c.drawString(0,0,'Referencia vertical 100 mm');c.restoreState()
        c.showPage()
        for side,offset in [('izquierda',0),('derecha',135)]:
            c.setPageSize(A4);c.setFillColor(dark);c.setFont('Helvetica-Bold',13);c.drawString(18*mm,281*mm,'MDF '+n+' | A4 '+side+' | 100%')
            c.setFont('Helvetica',8);c.drawString(18*mm,274*mm,'NO TALADRAR: transferir fijaciones reales. Solape 30 mm.')
            boarddraw(c,n,22,48,offset)
            c.setFont('Helvetica',8);c.drawString(22*mm,256*mm,'FRENTE Y=200');c.drawString(22*mm,40*mm,'X local '+str(offset)+'..'+str(offset+165)+' mm')
            marker=150-offset
            c.setStrokeColor(teal);c.setDash(2,2);c.line((22+marker)*mm,48*mm,(22+marker)*mm,248*mm);c.setDash()
            c.drawString(22*mm,32*mm,'Unir ambas mitades por X=150 y los bordes Y=0/200.')
            c.line(22*mm,22*mm,122*mm,22*mm);c.drawString(22*mm,15*mm,'Referencia 100 mm. No ajustar a pagina.')
            c.showPage()
        c.save()

def svg_and_dxf():
    for n in ['A','B']:
        svg=['<svg xmlns="http://www.w3.org/2000/svg" width="340mm" height="250mm" viewBox="-20 -25 340 250">','<style>text{font:4px Arial;fill:#162d3e}.warn{fill:#a45c06}.dim{stroke:#6b7e8a;fill:none;stroke-width:.3}</style>',f'<text x="0" y="-16">MDF {n} - plano superior / P0 provisional / mm</text>','<g transform="translate(0 200) scale(1 -1)"><rect x="0" y="0" width="300" height="200" fill="#f6eee4" stroke="#162d3e" stroke-width=".6"/>']
        dxf=['0','SECTION','2','HEADER','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','ENTITIES']
        def ln(x1,y1,x2,y2,layer='CONTORNO'):
            dxf.extend(['0','LINE','8',layer,'10',str(x1),'20',str(y1),'30','0','11',str(x2),'21',str(y2),'31','0'])
        for a,b in [((0,0),(300,0)),((300,0),(300,200)),((300,200),(0,200)),((0,200),(0,0))]:ln(*a,*b)
        for name,(x,y,w,h),color in footprint(n):
            co='#'+''.join('%02x'%int(v*255) for v in color)
            svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{co}" fill-opacity=".2" stroke="{co}" stroke-width=".5"/>')
            for a,b in [((x,y),(x+w,y)),((x+w,y),(x+w,y+h)),((x+w,y+h),(x,y+h)),((x,y+h),(x,y))]:ln(*a,*b,'HUELLAS')
        for h in holes:
            if h['nodo']!=n:continue
            x,y,d=float(h['x_mm']),float(h['y_mm']),float(h['diametro_mm'])
            svg.append(f'<circle cx="{x}" cy="{y}" r="{d/2}" fill="none" stroke="#a45c06" stroke-width=".3"/>')
            dxf.extend(['0','CIRCLE','8','CANDIDATOS_NO_TALADRAR','10',str(x),'20',str(y),'30','0','40',str(d/2)])
            dxf.extend(['0','TEXT','8','ETIQUETAS','10',str(x+2),'20',str(y+2),'30','0','40','2','1',h['id']])
        svg.append('</g>')
        for name,(x,y,w,h),col in footprint(n):
            label={'Perfboard_150x90':'PERFBOARD P2 150 x 90','BBB_PCB':'BBB 86.36 x 53.34','SG90_base':'SERVO TX','SW2_final_carrera':'SW2 RX','SW287_cuerpo':'SW287','F1_portafusible':'F1'}.get(name)
            if label:svg.append(f'<text x="{x+2}" y="{200-y-h/2}">{label}</text>')
        svg.extend(['<text x="100" y="-5">FRENTE Y=200</text>','<text x="0" y="209">Origen(0,0), X derecha, Y frente. Ver CSV para coordenadas y estado.</text>','<text class="warn" x="0" y="217">Agujeros candidatos. Confirmar todas las fijaciones antes de taladrar.</text>','<path class="dim" d="M0,-8 H300 M0,-10 V-6 M300,-10 V-6"/><text x="135" y="-10">300 mm</text>','</svg>'])
        (R/'planos'/f'MDF-{n}-superior.svg').write_text('\n'.join(svg),encoding='utf8')
        dxf.extend(['0','ENDSEC','0','EOF']);(R/'planos'/f'MDF-{n}-perforaciones.dxf').write_text('\n'.join(dxf),encoding='ascii')

def caption_page(c,title,subtitle,page):
    w,h=landscape(A3);c.setFillColor(dark);c.setFont('Helvetica-Bold',18);c.drawString(20*mm,h-20*mm,title)
    c.setFont('Helvetica',10);c.drawString(20*mm,h-28*mm,subtitle)
    c.setFont('Helvetica',8);c.drawString(20*mm,12*mm,'MONTAJE-P0 | P2-LOCAL | dimensiones no verificadas en hardware');c.drawRightString(w-20*mm,12*mm,str(page))

def plans():
    path=R/'planos/Planos_montaje.pdf';c=canvas.Canvas(str(path),pagesize=landscape(A3));page=0
    for which,title,sub in [('Global-isometrica','Ensamble global de los dos transceptores','Dos C0 PVC, dos C1 mangueras, dos C2 nylon y dos pares CLK. Gap 360 mm; conjunto 300 x 760 mm.'),('A-superior','Nodo A vista superior','Frente Y200; PCB y BBB atras; seis medios y mecanismos al frente.'),('B-superior','Nodo B vista superior local','B se gira 180 grados en el conjunto; PCB conserva su circuito y pinouts, solo cambia posicion de modulos.'),('A-lateral','Nodo A alturas laterales','MDF 6 provisional; separadores PCB12/BBB8; ejes opticos40/acusticos32/nylon36 sobre MDF.'),('B-lateral','Nodo B alturas laterales','Confirmar terminales inferiores, aleta Q6, altura real de switch y soportes.'),('Global-frontal','Vista frontal de los enlaces','Carriles globales X30/75 C0; X120/160 C1; X215/275 C2; reloj por X5/295.'),('Global-nylon','Trayectorias de nylon y retorno','Brazo r8 y giro20 grados propuestos. Carrera ideal2.78 mm; resortes sin k ni fuerza atribuidas.')]:
        page+=1;caption_page(c,title,sub,page)
        p,size=cad_image(which);c.drawImage(str(p),20*mm,28*mm,width=380*mm,height=220*mm,preserveAspectRatio=True,anchor='c',mask='auto')
        c.showPage()
    for n in ['A','B']:
        page+=1;caption_page(c,'Nodo '+n+' cotas y fijaciones','Coordenadas en CSV. Cruces provisionales: transferir desde componentes antes de taladrar.',page)
        boarddraw(c,n,35,45)
        c.setFont('Helvetica',9);c.drawString(35*mm,36*mm,'300 mm horizontal x 200 mm frontal. Origen trasero izquierdo.')
        c.showPage()
    page+=1;caption_page(c,'Rutas internas y conexiones globales','Potencia roja; senales verdes; reloj violeta; optica gris; sonido turquesa; nylon amarillo.',page)
    p,size=cad_image('Global-superior');c.drawImage(str(p),20*mm,30*mm,width=240*mm,height=220*mm,preserveAspectRatio=True,anchor='c')
    texts=['POTENCIA: Y8 y X285 local.','BBB-J10: Y112 / X177.','SENSORES: corredor Y115-119.','CLK AB: borde global X5.','CLK BA: borde global X295.','J9A.1/2 -> J8B.1/2.','J9B.1/2 -> J8A.1/2.','Sin conductor GND entre nodos.','NEG_IN solo retorna por Q6.','Longitud de par propuesta:1100 mm.','No llevar datos por USB/Ethernet.','Ver arneses.csv para cada conductor.']
    for i,t in enumerate(texts):c.setFont('Helvetica',10);c.drawString(265*mm,(239-i*12)*mm,t)
    c.showPage();c.save()

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyES',fontName='Helvetica',fontSize=10,leading=14,spaceAfter=7,textColor=dark))
styles.add(ParagraphStyle(name='SmallES',fontName='Helvetica',fontSize=8,leading=10,spaceAfter=3,textColor=dark))
styles.add(ParagraphStyle(name='CodeES',fontName='Courier',fontSize=7.3,leading=10,spaceAfter=6,backColor=colors.HexColor('#edf2f4')))
for sn in ['Heading1','Heading2','Heading3','Title']:
    styles[sn].textColor=dark;styles[sn].fontName='Helvetica-Bold'
    styles[sn].keepWithNext=True
styles['Heading1'].fontSize=19;styles['Heading1'].leading=24
styles['Heading2'].fontSize=13;styles['Heading2'].leading=17
styles['Heading3'].fontSize=11;styles['Heading3'].leading=15

def fmt(s):
    s=html.escape(s).replace('⇄',' &lt;-&gt; ').replace('→',' -&gt; ').replace('←',' &lt;- ').replace('≤',' &lt;= ').replace('≥',' &gt;= ').replace('×',' x ').replace('±',' +/- ').replace('τ','tau').replace('β','beta').replace('α','alpha').replace('δ','delta')
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s);s=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',s)
    s=re.sub(r'\[([^]]+)\]\([^)]+\)',r'\1',s)
    return s

def md_story(path):
    lines=path.read_text(encoding='utf8').splitlines();out=[];i=0
    while i<len(lines):
        s=lines[i].strip();i+=1
        if not s:continue
        if s.startswith('```'):
            code=[]
            while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
            i+=1
            # long commands wrap at spaces; no truncation
            for line in code:out.append(Paragraph(html.escape(line),styles['CodeES']))
        elif s.startswith('|'):
            table=[s]
            while i<len(lines) and lines[i].startswith('|'):table.append(lines[i]);i+=1
            rows=[]
            for line in table:
                cells=[x.strip() for x in line.strip('|').split('|')]
                if all(re.fullmatch(r'[:\- ]+',x) for x in cells):continue
                rows.append(cells)
            count=max(len(r) for r in rows);avail=A4[0]-76
            if count==4:width=[avail*.20,avail*.27,avail*.27,avail*.26]
            elif count==3:width=[avail*.25,avail*.40,avail*.35]
            else:width=[avail/count]*count
            t=Table([[Paragraph(fmt(x),styles['SmallES']) for x in r] for r in rows],colWidths=width,repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dce8ed')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#c7d2d9')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));out+=[t,Spacer(1,9)]
        elif s.startswith('#'):
            level=len(s)-len(s.lstrip('#'));out.append(Paragraph(fmt(s[level:].strip()),styles['Heading'+str(min(level,3))]))
        else:
            para=[s]
            while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','```')) and not re.match(r'^\d+\. ',lines[i]):para.append(lines[i].strip());i+=1
            out.append(Paragraph(fmt(' '.join(para)),styles['BodyES']))
    return out

def manual():
    story=[Paragraph('Construcción de los dos nodos TRAMA 3',styles['Title']),Spacer(1,14),Paragraph('T09 luz y sonido · T10 nylon, servos y relojes',styles['Heading2']),Paragraph('Erwin y Adrián · Propuesta P0 · 14 noviembre 2026',styles['BodyES'])]
    p,size=cad_image('Global-isometrica');factor=min(510/size[0],368/size[1]);story.append(Image(str(p),width=size[0]*factor,height=size[1]*factor))
    story.append(Paragraph('Dos bases de 300 x 200 mm; separación propuesta de 360 mm. Referencia eléctrica T51-P2-LOCAL. Diseño preparado para presentación en seco, medición y construcción por etapas.',styles['BodyES']))
    story.append(Paragraph('<b>Antes de cortar o perforar:</b> medir espesor, huellas, conductos y fijaciones. Las pruebas activas dependen de T06/T08 adaptados a T51 y de T18. No se acreditan resultados físicos.',styles['BodyES']))
    story.append(PageBreak())
    for path in [R/'README.md',R/'construccion/01-diseno-y-medidas.md',R/'construccion/02-construccion.md',R/'construccion/03-cableado-P2.md',R/'calibracion/04-pruebas.md']:
        story.append(CondPageBreak(120));story+=md_story(path);story.append(Spacer(1,16))
    story.append(Paragraph('Tablas para montaje y registro',styles['Heading1']))
    story.append(Paragraph('Los CSV del paquete son editables con Excel o un editor. No se modifica el tracker. Las filas de resultado quedan vacías hasta tomar medidas.',styles['BodyES']))
    for name in ['distribucion.csv','medidas-criticas.csv','fijaciones.csv','arneses.csv','J10.csv']:
        story.append(Paragraph('materiales/'+name,styles['Heading3']))
    for name in ['registros.csv','muestras.csv','diafonia.csv','resortes.csv','reloj.csv','desviaciones-P2.csv']:
        story.append(Paragraph('calibracion/'+name,styles['Heading3']))
    story.append(PageBreak());story.append(Paragraph('Distribución de materiales y faltantes condicionales',styles['Heading1']))
    rows=list(csv.DictReader((R/'materiales/distribucion.csv').open(encoding='utf-8-sig')))
    data=[['Material / función','Disponible','A / B / enlace','Sobrante / faltante']]
    for r in rows:
        data.append([r['material']+'<br/>'+r['funcion'],r['disponible'],str(r['nodo_A'])+' / '+str(r['nodo_B'])+' / '+str(r['entre_nodos']),str(r['sobrante'])+' / '+str(r['faltante_condicional'])])
    t=Table([[Paragraph(html.escape(x).replace('&lt;br/&gt;','<br/>'),styles['SmallES']) for x in r] for r in data],colWidths=[150,100,125,144],repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dce8ed')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#c7d2d9')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.append(t)
    def foot(c,d):
        c.setFillColor(colors.HexColor('#687e8b'));c.setFont('Helvetica',8);c.drawString(38,25,'TRAMA 3 / MONTAJE-P0 / P2-LOCAL / verificaciones físicas pendientes');c.drawRightString(A4[0]-38,25,str(d.page))
    SimpleDocTemplate(str(R/'construccion/Guia_completa.pdf'),pagesize=A4,leftMargin=38,rightMargin=38,topMargin=35,bottomMargin=40,title='Construccion TRAMA3 T09 T10',author='TRAMA3').build(story,onFirstPage=foot,onLaterPages=foot)

def renderpdfs():
    out=R/'evidencias/qa';out.mkdir(exist_ok=True)
    records=[]
    for p in [R/'construccion/Guia_completa.pdf',R/'planos/Planos_montaje.pdf',R/'planos/MDF-A-perforaciones.pdf',R/'planos/MDF-B-perforaciones.pdf']:
        doc=pdfium.PdfDocument(str(p));thumbs=[]
        for idx in range(len(doc)):
            img=doc[idx].render(scale=1.3).to_pil();img.save(out/(p.stem+'-'+str(idx+1)+'.png'))
            im=img.copy();im.thumbnail((250,350));panel=PILImage.new('RGB',(270,380),'white');panel.paste(im,((270-im.width)//2,20));ImageDraw.Draw(panel).text((8,360),p.stem+' p'+str(idx+1),fill='black');thumbs.append(panel)
        for start in range(0,len(thumbs),12):
            part=thumbs[start:start+12];sheet=PILImage.new('RGB',(1080,380*math.ceil(len(part)/4)),(215,222,226))
            for j,t in enumerate(part):sheet.paste(t,((j%4)*270,(j//4)*380))
            sheet.save(out/(p.stem+'-contacto-'+str(start//12+1)+'.png'))
        records.append({'archivo':str(p.relative_to(R)),'paginas':len(doc)})
    (R/'evidencias/pdf-render.json').write_text(json.dumps(records,indent=2),encoding='utf8');print(records)

if __name__=='__main__':templates();svg_and_dxf();plans();manual();renderpdfs()
