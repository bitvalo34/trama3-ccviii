#!/usr/bin/env python3
"""Crea ZIP y tar.gz de fuentes, guia, pruebas y fixtures; excluye binarios/logs."""
import argparse
import hashlib
import io
import json
import tarfile
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def contents():
    selected={}
    for folder in ("hardware/pruebas","hardware/documentacion","tests/hardware"):
        for p in (ROOT/folder).rglob("*"):
            rel=p.relative_to(ROOT)
            if not p.is_file() or any(x in rel.parts for x in ("__pycache__","build","resultados")):continue
            if p.suffix in (".pyc",".out",".exe",".o",".obj"):continue
            selected[rel.as_posix()]=p.read_bytes()
    for f in ("hardware/configuracion/T04-resultados.md",
              "hardware/diseno-placas/diseno-electrico.md",
              "hardware/diseno-placas/verificaciones/revision-final.md",
              "hardware/diseno-placas/netlist/redes.csv",
              "hardware/diseno-placas/netlist/componentes.csv",
              "hardware/diseno-placas/netlist/kicad-export.xml",
              "docs/protocolo/TRAMA3_Protocolo_Revision_102.md"):
        selected[f]=(ROOT/f).read_bytes()
    for p in (ROOT/"hardware/diseno-placas").rglob("*.kicad_sch"):
        selected[p.relative_to(ROOT).as_posix()]=p.read_bytes()
    selected["LEEME.md"]=b"# TRAMA 3 T06/T08\n\nEntrada: hardware/documentacion/Guia_Completa_T06_T08.md\nSin pruebas fisicas realizadas. No actualizar tracker.\n"
    sums="".join(hashlib.sha256(data).hexdigest()+"  "+name+"\n" for name,data in sorted(selected.items()))
    selected["SHA256SUMS"]=sums.encode("ascii")
    return selected
def main():
    p=argparse.ArgumentParser();p.add_argument("--output",required=True);a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True);files=contents()
    with tarfile.open(str(out/"TRAMA3_T06_T08.tar.gz"),"w:gz") as t:
        for name,data in sorted(files.items()):
            item=tarfile.TarInfo(name);item.size=len(data);item.mode=0o755 if name.endswith(".sh") else 0o644
            item.mtime=0;t.addfile(item,io.BytesIO(data))
    with zipfile.ZipFile(str(out/"TRAMA3_T06_T08.zip"),"w",zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(files.items()):z.writestr(name,data)
        z.writestr("TRAMA3_T06_T08.tar.gz",(out/"TRAMA3_T06_T08.tar.gz").read_bytes())
    # Verificar bytes internos y hashes, sin ejecutar nada del archivo.
    with zipfile.ZipFile(str(out/"TRAMA3_T06_T08.zip")) as z:
        assert all(z.read(name)==data for name,data in files.items())
    with tarfile.open(str(out/"TRAMA3_T06_T08.tar.gz")) as t:
        assert all(t.extractfile(name).read()==data for name,data in files.items())
    report={"files":len(files),"archives":{},"physical_tests":"NOT_TESTED"}
    for name in ("TRAMA3_T06_T08.zip","TRAMA3_T06_T08.tar.gz"):
        data=(out/name).read_bytes();report["archives"][name]={"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}
    (out/"paquete-verificado.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
