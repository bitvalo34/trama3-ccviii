"""Empaqueta entregables sin documentos privados ni imagenes de QA."""
from pathlib import Path
import argparse,json,hashlib,shutil,zipfile
from PIL import Image,ImageDraw,ImageFont,ImageChops
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--dest',required=True);a=p.parse_args()
dest=Path(a.dest);dest.mkdir(parents=True,exist_ok=True);folder=dest/'TRAMA3_T09_T10';folder.mkdir(exist_ok=True)
files=[]
for path in R.rglob('*'):
    if not path.is_file():continue
    rel=path.relative_to(R)
    if 'qa' in rel.parts or '__pycache__' in rel.parts or path.name.endswith('-lectura.txt') or path.suffix in ['.pyc','.FCBak','.FCStd1'] or '.FCStd.' in path.name:continue
    files.append(path)
for path in files:
    target=folder/path.relative_to(R);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
manifest={str(p.relative_to(folder)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.rglob('*') if p.is_file() and p.name!='SHA256SUMS.json'}
(folder/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
out=dest/'TRAMA3_T09_T10_Entrega.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in folder.rglob('*'):
        if p.is_file():z.write(p,Path('TRAMA3_T09_T10')/p.relative_to(folder))
with zipfile.ZipFile(out,'r') as z:
    bad=z.testzip()
    if bad is not None:raise RuntimeError('ZIP no valido: '+bad)
im=Image.open(folder/'planos/Global-isometrica.png').convert('RGB');bb=ImageChops.difference(im,Image.new('RGB',im.size,'white')).getbbox();im=im.crop(bb);im.thumbnail((1500,1000))
preview=Image.new('RGB',(1600,im.height+200),'white');preview.paste(im,((1600-im.width)//2,110));draw=ImageDraw.Draw(preview)
fontpath=Path('C:/Windows/Fonts/arial.ttf')
font=ImageFont.truetype(str(fontpath),38);small=ImageFont.truetype(str(fontpath),25)
draw.text((50,25),'TRAMA 3 | Dos nodos completos',font=font,fill='#162d3e')
draw.text((50,73),'Propuesta P0 · P2-LOCAL · Separacion entre MDF: 360 mm',font=small,fill='#476272')
draw.text((50,preview.height-60),'Luz: PVC | Sonido: turquesa | Nylon: amarillo | Reloj: pares violetas',font=small,fill='#162d3e')
preview.save(dest/'TRAMA3-vista-global.png')
print(json.dumps({'carpeta':str(folder),'zip':str(out),'bytes':out.stat().st_size,'archivos':len(manifest),'preview':str(dest/'TRAMA3-vista-global.png')},ensure_ascii=False))
