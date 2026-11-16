#!/usr/bin/env python3
"""Aceptacion por evidencia seleccionada; nunca por existencia de un PASS."""
import argparse
import json
import sys
from pathlib import Path
from common import atomic_json
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/"t06"),str(ROOT/"t08")]
from analyze import analyze
from mediciones import evaluate as electrical,REVISION
REQUIRED=("build","pru-smoke","loopback","pwm-capture-1000","pwm-capture-1500","pwm-capture-2000","t08")
def summarize(states):
    return next((s for s in ("FAIL","BLOCKED","NOT_TESTED") if s in states),"PASS")
def evaluate(manifest,base):
    if not isinstance(manifest,dict):raise ValueError("Manifiesto debe ser objeto")
    boards={}
    for board in ("BBB-A","BBB-B"):
        selection=manifest.get(board,{})
        if not isinstance(selection,dict):raise ValueError("Registro de placa invalido")
        checks={};records={}
        for key in REQUIRED:
            ref=selection.get(key)
            # Legacy single-width record remains examinable, never satisfies all widths.
            if not ref and key=="pwm-capture-1500":ref=selection.get("pwm-capture")
            status="NOT_TESTED";reason="Evidencia no seleccionada"
            if ref:
                try:
                    p=(base/ref).resolve()
                    if base.resolve() not in p.parents:raise ValueError("Ruta fuera de evidencia")
                    r=json.loads(p.read_text(encoding="utf-8"))
                    test="pwm-capture" if key.startswith("pwm-capture") else key
                    if r.get("board")!=board or r.get("test")!=test:raise ValueError("Placa/prueba incorrecta")
                    if r.get("status") not in ("PASS","FAIL","BLOCKED","NOT_TESTED"):raise ValueError("Estado invalido")
                    expected_origin="software_build" if key=="build" else "physical" if key=="t08" else "hardware"
                    if r.get("origin")!=expected_origin:raise ValueError("Origen incompatible")
                    status=r["status"];reason="Registro "+ref
                    if status=="PASS":
                        if r.get("schema")!=2:raise ValueError("Evidencia historica; repetir con esquema 2")
                        if key=="t08":
                            if r.get("hardware_revision")!=REVISION:raise ValueError("Revision P2 incorrecta")
                            rows=[v["measurement"] for v in r["points"].values() if v.get("measurement")]
                            if electrical(rows,board)["status"]!="PASS":raise ValueError("Mediciones incompletas/incompatibles")
                        else:
                            if r.get("hardware_revision")!="BBB-BARE":raise ValueError("Nivel 1 requerido")
                            ident=r.get("identity",{})
                            if "BeagleBone Black" not in ident.get("model","") or not ident.get("kernel"):raise ValueError("Sin identidad BBB")
                            if not r.get("source_hashes") or len(r.get("binary_hashes",{}))!=2:raise ValueError("Sin trazabilidad de binarios")
                            if key=="build":
                                if r.get("command",{}).get("exit_code")!=0:raise ValueError("Compilacion no comprobada")
                            else:
                                if r.get("resources",{}).get("restored") is not True:raise ValueError("Recursos no restaurados")
                                c=r.get("confirmation",{})
                                if not c.get("sha256") or not c.get("evidence") or c.get("operator")!=r.get("operator"):raise ValueError("Sin confirmacion fisica trazable")
                                if not r.get("electrical_confirmation") or not r.get("active"):raise ValueError("Prueba no autorizada")
                                if key=="pru-smoke":
                                    if r.get("probe",{}).get("ready") is not True:raise ValueError("Sin heartbeat/READY")
                                else:
                                    params=r["parameters"]
                                    calc=analyze(r["raw"],params["period_us"],params["high_us"],test,params["cycles"],params.get("invert_mask",0))
                                    if calc["status"]!="PASS" or not calc["observed_input"]:raise ValueError("Captura no cumple")
                                    if key.startswith("pwm-capture"):
                                        if params["high_us"]!=int(key.rsplit("-",1)[1]) or params["period_us"]!=20000:
                                            raise ValueError("Ancho/50 Hz incorrectos")
                                        if not r.get("pwm",{}).get("frequency_checked"):raise ValueError("PWM no corroborado")
                    records[key]=r
                except (OSError,ValueError,KeyError,TypeError,AttributeError) as exc:
                    status="BLOCKED";reason=str(exc)
            checks[key]={"status":status,"reason":reason}
        build=records.get("build",{})
        if checks["build"]["status"]=="PASS":
            for key in REQUIRED[1:-1]:
                if checks[key]["status"]=="PASS":
                    r=records[key]
                    if any(r.get(k)!=build.get(k) for k in ("source_hashes","binary_hashes")):
                        checks[key]={"status":"BLOCKED","reason":"Build y ensayo usan versiones distintas"}
        boards[board]={"checks":checks,"T06":summarize([checks[k]["status"] for k in REQUIRED[:-1]]),"T08":checks["t08"]["status"]}
    result={"schema":2,"hardware_revision":REVISION,"boards":boards}
    for task in ("T06","T08"):
        result[task]={"status":summarize([b[task] for b in boards.values()]),
                      "conclusion":"Revisar evidencia individual; no modifica tracker"}
    return result
def markdown(report):
    lines=["# Aceptacion T06/T08 P2","", "| Placa | T06 | T08 |","|---|---|---|"]
    for b,r in report.get("boards",{}).items():
        lines.append("| {} | {} | {} |".format(b,r["T06"],r["T08"]))
        for test,c in r["checks"].items():lines.append("\n- {} {}: {} — {}".format(b,test,c["status"],c["reason"]))
    return "\n".join(lines)+"\n"
def main():
    p=argparse.ArgumentParser();p.add_argument("--manifest",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();m=Path(a.manifest);out=Path(a.output)
    if out.exists():p.error("No sobrescribir informe; use nombre nuevo")
    try:report=evaluate(json.loads(m.read_text()),m.parent)
    except (OSError,ValueError) as exc:report={"status":"BLOCKED","error":str(exc)}
    atomic_json(out,report);out.with_suffix(".md").write_text(markdown(report),encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
