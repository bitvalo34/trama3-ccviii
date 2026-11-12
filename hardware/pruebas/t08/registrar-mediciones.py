#!/usr/bin/env python3
import argparse
import datetime
from pathlib import Path
from mediciones import template,write_csv,read_csv,ALL_POINTS
def main():
    p=argparse.ArgumentParser(description="Crear formulario vacio o registrar UNA medida real.")
    p.add_argument("--board",choices=("BBB-A","BBB-B"),required=True)
    p.add_argument("--file",required=True)
    p.add_argument("--point",choices=ALL_POINTS)
    p.add_argument("--value")
    p.add_argument("--uncertainty")
    p.add_argument("--method")
    p.add_argument("--instrument")
    p.add_argument("--evidence")
    p.add_argument("--date",help="Fecha real ISO del PC, si reloj BBB desajustado")
    p.add_argument("--notes",default="")
    a=p.parse_args();path=Path(a.file)
    if not a.point:
        if path.exists():p.error("No sobrescribir formulario existente")
        write_csv(path,template(a.board));print(str(path));return
    if not path.exists():p.error("Crear primero el formulario sin --point")
    if any(v is None for v in (a.value,a.method,a.instrument,a.evidence)):
        p.error("Registro exige value, method, instrument y evidence")
    rows=read_csv(path)
    if any(r["board"]!=a.board for r in rows):p.error("Placa incorrecta")
    for r in rows:
        if r["point"]==a.point:
            r.update(value=a.value,uncertainty=a.uncertainty or "",method=a.method,
                     instrument=a.instrument,evidence=a.evidence,
                     measured_at=a.date or datetime.datetime.utcnow().isoformat()+"Z",
                     notes=a.notes)
    # Conservar lectura previa en copia unica, nunca perder evidencia.
    if any(r["value"] for r in read_csv(path)):
        backup=path.with_name(path.name+"."+datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S%f")+".bak")
        backup.write_bytes(path.read_bytes())
    write_csv(path,rows);print(str(path))
if __name__=="__main__":main()
