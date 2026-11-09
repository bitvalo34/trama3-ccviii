"""Dossier imprimible con medidas nominales, explicaciones y tablas completas."""
from pathlib import Path
import json,csv,re,html,math,io
from PIL import Image as PILImage, ImageChops
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Image,KeepTogether,Flowable
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
R=Path(__file__).resolve().parent;D=json.loads((R/'netlist/diseno.json').read_text(encoding='utf8'))
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'));pdfmetrics.registerFont(TTFont('ArialBold','C:/Windows/Fonts/arialbd.ttf'));pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='ArialBold',italic='Arial',boldItalic='ArialBold')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyT',fontName='Arial',fontSize=9.5,leading=13,spaceAfter=6))
styles.add(ParagraphStyle(name='CellT',fontName='Arial',fontSize=7.3,leading=9.2,spaceAfter=0))
styles.add(ParagraphStyle(name='H1T',fontName='ArialBold',fontSize=17,leading=21,spaceAfter=12))
styles.add(ParagraphStyle(name='H2T',fontName='ArialBold',fontSize=12,leading=16,spaceBefore=9,spaceAfter=7,keepWithNext=True))
styles.add(ParagraphStyle(name='H3T',fontName='ArialBold',fontSize=10.5,leading=14,spaceBefore=8,spaceAfter=5,keepWithNext=True))
def fmt(t):
 t=html.escape(t)
 t=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:'<link href="'+m[2]+'" color="#244d70">'+m[1]+'</link>' if m[2].startswith('http') else m[1],t)
 t=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',t);t=re.sub(r'`([^`]+)`',r'\1',t)
 return t
def p(t,sty='BodyT'):return Paragraph(fmt(t),styles[sty])
def tab(rows,widths=None):
 vals=[[p(str(v),'CellT') for v in row] for row in rows]
 if widths is None:widths=[174*mm/len(rows[0])]*len(rows[0])
 t=Table(vals,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#ececec')),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#a0a0a0')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),3.3),('BOTTOMPADDING',(0,0),(-1,-1),3.3)]));return t
def cropped(path,maxw,maxh):
 im=PILImage.open(path).convert('RGB');box=ImageChops.difference(im,PILImage.new('RGB',im.size,'white')).getbbox();im=im.crop(box);buf=io.BytesIO();im.save(buf,format='PNG');buf.seek(0);scale=min(maxw/im.width,maxh/im.height);return Image(buf,width=im.width*scale,height=im.height*scale)
def md(path):
 lines=(R/path).read_text(encoding='utf8').splitlines();story=[];i=0
 while i<len(lines):
  l=lines[i].strip()
  if not l:i+=1;continue
  if l.startswith('|'):
   rows=[]
   while i<len(lines) and lines[i].strip().startswith('|'):
    cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
    if not all(re.fullmatch(r'[:\- ]+',c) for c in cells):rows.append(cells)
    i+=1
   story.extend([tab(rows),Spacer(1,7)]);continue
  if l.startswith('### '):story.append(p(l[4:],'H3T'))
  elif l.startswith('## '):story.append(p(l[3:],'H2T'))
  elif l.startswith('# '):story.append(p(l[2:],'H1T'))
  else:
   if l.startswith('- [ ]'):l='□ '+l[5:]
   elif l.startswith('- '):l='• '+l[2:]
   story.append(p(l))
  i+=1
 return story
palette={'POWER':'#efcc8b','SERVO':'#ddbaa0','CORE':'#9cc4d5','TX':'#c2d9ac','RX':'#b5cfb7','ENABLE':'#d8c6eb','CLOCK':'#d0d0df','CLOCK_RX':'#ead4a2'}
class Board(Flowable):
 def __init__(self,bottom=False,wires=False,focus=None,layer=None):Flowable.__init__(self);self.width=112*mm;self.height=177*mm;self.bottom=bottom;self.wires=wires;self.focus=focus;self.layer=layer
 def draw(self):
  c=self.canv;c.saveState();c.translate(11*mm,162*mm);c.scale(mm,-mm);fx=lambda x:90-x if self.bottom else x
  def text(x,y,t,size=1.7):
   c.saveState();c.translate(x,y);c.scale(1,-1);c.setFont('Arial',size);c.setFillColor(colors.black);c.drawCentredString(0,0,t);c.restoreState()
  c.setFillColor(colors.HexColor('#f4efdf'));c.setStrokeColor(colors.black);c.setLineWidth(.2);c.rect(0,0,90,150,fill=1)
  for r in range(56):
   n=r+1;s=''
   while n:n,k=divmod(n-1,26);s=chr(65+k)+s
   text(-3,5+r*2.54+.5,s)
   for k in range(32):c.setStrokeColor(colors.HexColor('#aaaaaa'));c.setLineWidth(.08);c.circle(fx(5+k*2.54),5+r*2.54,.6,fill=0)
  for k in range(32):text(fx(5+k*2.54),-2,str(k+1))
  if self.wires:
   for w in D['wires']:
    c.setStrokeColor(colors.HexColor({'rojo':'#b02020','negro':'#222222','azul':'#246399','violeta':'#8b3399','naranja':'#b26700'}[w['color']]));c.setLineWidth(.18)
    for a,b in zip(w['path'],w['path'][1:]):
     if self.layer is None or abs(a[2]-self.layer)<.01:c.line(fx(a[0]),a[1],fx(b[0]),b[1])
  for comp in D['components']:
   if self.focus and comp['zone'] not in self.focus:continue
   x,y,w,h,_=comp['box'];x=90-x-w if self.bottom else x;c.setStrokeColor(colors.black);c.setLineWidth(.17);c.setFillColor(colors.HexColor(palette[comp['zone']]));c.rect(x,y,w,h,fill=0 if self.bottom else 1);text(x+w/2,y+h/2+.5,comp['ref'],1.5)
   for pp in comp['pins']:c.setFillColor(colors.red if pp['number']=='1' else colors.black);c.circle(fx(pp['x']),pp['y'],.35,stroke=0,fill=1)
  c.setStrokeColor(colors.black);c.setLineWidth(.3);c.line(0,158,25.4,158);c.line(0,157,0,159);c.line(25.4,157,25.4,159);text(12.7,162,'25.4 mm — imprimir 100 %',2)
  c.restoreState()
def footer(c,doc):
 c.saveState();c.setFont('Arial',8);c.setFillColor(colors.HexColor('#555555'));c.drawString(18*mm,12*mm,'TRAMA 3 · T51-P1 · DIMENSIONES ESTIMADAS · T52 pendiente');c.drawRightString(192*mm,12*mm,str(doc.page));c.restoreState()
story=[p('TRAMA 3 — Interfaces A y B','H1T'),p('Diseño eléctrico, placas perforadas y montaje','H2T'),p('Revisión T51-P1 · 9 de noviembre de 2026'),p('**Documento de revisión previo a soldadura.** Se conserva el protocolo102. Geometría nominal: 90 × 150 mm por placa. Las medidas aproximadas están autorizadas para diseñar; todavía requieren contraste con las piezas reales.'),cropped(R/'planos/A-isometrica.png',170*mm,120*mm),Spacer(1,10),p('Fuente CAD: FreeCAD 1.1.4. Modelos nativos A y B y exportaciones STEP incluidas. Los colores identifican zonas; los cuerpos son aproximaciones volumétricas, no fotografías ni modelos oficiales del lote.'),p('Lectura sugerida: alcance y pendientes; diseño eléctrico; planos; compra adicional; montaje; revisión independiente; tablas de terminales y cables. Cada fila de los anexos aplica a ambas placas salvo identificación explícita A→B/B→A.'),PageBreak()]
story+=md('README.md')+[PageBreak()]+md('diseno-electrico.md')+[PageBreak()]
for title,b,w,focus,layer in [('Plano superior — colocación y pin1',False,False,None,None),('Plano inferior — espejo horizontal',True,True,None,None),('Cableado próximo a placa — z = −2.4 mm',True,True,None,-2.4),('Cruces inferiores — z = −3.9 mm',True,True,None,-3.9),('Cruces inferiores — z = −5.4 mm',True,True,None,-5.4),('Selectores EN y corte del servo',False,False,['ENABLE','SERVO'],None),('Alimentación y reloj aislado',False,False,['POWER','CLOCK','CLOCK_RX'],None)]:
 story.extend([p(title,'H1T'),p('Escala geométrica nominal 1:1. No usar como plantilla de fabricación hasta confirmar retícula y paso reales. Pin1 rojo. Cables identificados individualmente en CSV y visor de conexiones.'),Board(b,w,focus,layer),PageBreak()])
story.extend([p('Vistas ortográficas del CAD','H1T'),p('La geometría de A y B es la misma. Estas imágenes no sustituyen las plantillas vectoriales a escala. La vista inferior conserva el espejo horizontal del plano de soldadura.')])
story.append(Table([[p('Superior','H2T'),p('Inferior','H2T')],[cropped(R/'planos/A-superior.png',80*mm,165*mm),cropped(R/'planos/A-inferior.png',80*mm,165*mm)]],colWidths=[87*mm,87*mm]))
story.append(PageBreak());story.append(p('Altura y perfil','H1T'))
for nm,title in [('lateral','Lateral'),('posterior','Posterior')]:story.extend([p(title,'H2T'),cropped(R/f'planos/A-{nm}.png',170*mm,65*mm),Spacer(1,14)])
story.append(p('C1 alcanza 20 mm sobre placa; reservar acceso vertical para extraer el MCP. Las rutas inferiores alcanzan 5.8 mm bajo la placa en el modelo. Comprobar diámetros reales, radios de doblado y apoyo antes de elegir altura libre de montaje.'))
story.extend([PageBreak()]+md('materiales-adicionales.md')+[PageBreak()]+md('soldadura/guia-montaje.md')+[PageBreak()]+md('verificaciones/T51-T52-checklist.md')+[PageBreak()])
for path,title,cols,widths in [
 ('soldadura/arnes-BBB.csv','Anexo A — Arnés de cada BBB',['pin_placa','BBB','funcion'],[25,40,109]),
 ('soldadura/puentes.csv','Anexo B — Puentes y configuración',['ref','perforaciones','inicial','funcion'],[15,45,40,74]),
 ('soldadura/arneses-externos.csv','Anexo C — Todos los cables externos',['id','aplica','origen','destino','longitud_reserva_mm','conductor'],[12,18,43,30,20,51]),
 ('soldadura/coordenadas.csv','Anexo D — Todos los terminales de placa',['ref','pin','perforacion','red','x_mm','y_mm'],[17,12,25,78,21,21]),
 ('soldadura/cableado.csv','Anexo E — Todos los cables inferiores',['id','source','destination','start','end','cut_mm','net'],[15,25,25,18,18,17,56])]:
 story.append(p(title,'H1T'));story.append(p('Aplicar la misma tabla a A y B. Las rutas XYZ completas están en cableado.csv y en cada objeto W del FreeCAD. NC no se conecta. Las longitudes son iniciales; comprobar antes de cortar.'))
 with (R/path).open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
 story.append(tab([cols]+[[r[c] for c in cols] for r in rows],[x*mm for x in widths]));story.append(PageBreak())
report=json.loads((R/'verificaciones/resultado-integrado.json').read_text(encoding='utf8'));dc=json.loads((R/'verificaciones/selectores-DC.json').read_text(encoding='utf8'))
story.extend([p('Anexo F — Resultados de comprobación','H1T'),p('Comparación exacta KiCad/manifiesto: '+str(report['comprobaciones']['netlist_kicad_igual_manifest'])),p('Colisiones entre cables de redes distintas con diámetros modelados: '+str(not report['comprobaciones']['rutas_sin_interseccion_entre_redes'])),p('Holgura mínima nominal entre aislamientos: '+str(report['comprobaciones']['holgura_minima_aislamientos_mm'])+' mm. Comprobar diámetros exteriores y fabricación manual.'),p('Profundidad máxima de cable: '+str(report['comprobaciones']['profundidad_cable_mm'])+' mm bajo placa.'),p('Simulación DC de selectores: '+str(dc['lecturas'])+' lecturas; '+str(dc['fallos'])+' fallos. Se solucionaron las redes resistivas del manifiesto para combinaciones de RAW, EN y retirada de puentes.'),p('Estos resultados no validan el consumo, la dinámica ni el montaje físico. T52 requiere revisión independiente y cierre de los pendientes indicados.')])
out=R/'planos/T51_Dossier_Diseno_y_Montaje.pdf'
SimpleDocTemplate(str(out),pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=18*mm,bottomMargin=21*mm,title='TRAMA3 T51 - Diseno y montaje provisional',author='TRAMA3 - Erwin / revision pendiente Adrian').build(story,onFirstPage=footer,onLaterPages=footer)
print(out)
