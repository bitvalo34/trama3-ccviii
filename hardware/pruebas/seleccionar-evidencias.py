#!/usr/bin/env python3
"""Selecciona explicitamente un ensayo; un fallo posterior no se oculta por antiguedad."""
import argparse
import json
from pathlib import Path
from common import atomic_json
p=argparse.ArgumentParser()
p.add_argument("--manifest",required=True)
p.add_argument("--board",choices=("BBB-A","BBB-B"),required=True)
p.add_argument("--test",choices=("loopback","pwm-capture","t08"),required=True)
p.add_argument("--file",required=True)
a=p.parse_args()
m=Path(a.manifest).resolve();f=Path(a.file).resolve()
try: relative=f.relative_to(m.parent)
except ValueError:p.error("La evidencia debe estar dentro de la carpeta del manifiesto")
r=json.loads(f.read_text())
if r.get("board")!=a.board or r.get("test")!=a.test:p.error("Placa/prueba no coincide")
data=json.loads(m.read_text()) if m.exists() else {"BBB-A":{},"BBB-B":{}}
data.setdefault(a.board,{})[a.test]=relative.as_posix()
atomic_json(m,data)
print(str(m))
