#!/usr/bin/env python3
"""Aceptacion explicita por manifiesto; no elige el mejor ensayo entre reintentos."""
import argparse
import json
from pathlib import Path
from common import atomic_json
REQUIRED=("loopback","pwm-capture","t08")
def summarize(states):
    for s in ("FAIL","BLOCKED","NOT_TESTED"):
        if s in states:return s
    return "PASS"
def evaluate(manifest,base):
    if not isinstance(manifest,dict):raise ValueError("Manifiesto debe ser objeto")
    for board in ("BBB-A","BBB-B"):
        if not isinstance(manifest.get(board,{}),dict):raise ValueError("Registro de placa invalido")
    boards={}
    for board in ("BBB-A","BBB-B"):
        checks={}
        for test in REQUIRED:
            ref=manifest.get(board,{}).get(test)
            status="NOT_TESTED";reason="Evidencia no seleccionada"
            if ref:
                try:
                    p=(base/ref).resolve()
                    if base.resolve() not in p.parents: raise ValueError("Ruta fuera del paquete de evidencia")
                    r=json.loads(p.read_text())
                    if r.get("board")!=board or r.get("test")!=test:raise ValueError("Placa/prueba incompatible")
                    if r.get("origin") not in ("hardware","physical"):raise ValueError("Origen no fisico")
                    if r.get("status") not in ("PASS","FAIL","BLOCKED","NOT_TESTED"):raise ValueError("Estado invalido")
                    status=r["status"];reason="Registro "+ref
                    if test!="t08" and status=="PASS":
                        if not r.get("resources",{}).get("restored"):raise ValueError("Recursos no restaurados")
                        if r.get("physical_status")!="PASS":raise ValueError("Sin prueba fisica")
                        if not r.get("analysis",{}).get("observed_input"):raise ValueError("Sin flancos de entrada")
                        if not r.get("electrical_confirmation"):raise ValueError("Sin checklist electrico")
                        # Recalcular desde muestras, no confiar en un PASS superficial.
                        import sys
                        sys.path.insert(0,str(Path(__file__).resolve().parent/"t06"))
                        from analyze import analyze
                        params=r["parameters"]
                        recalculated=analyze(r["raw"],params["period_us"],params["high_us"],test,params["cycles"])
                        if recalculated["status"]!="PASS":raise ValueError("Captura no cumple")
                        if test=="pwm-capture" and (params["period_us"]!=20000 or not r.get("pwm",{}).get("frequency_checked")):
                            raise ValueError("No demuestra PWM 50 Hz")
                    if test=="t08" and status=="PASS":
                        import sys
                        sys.path.insert(0,str(Path(__file__).resolve().parent/"t08"))
                        from mediciones import evaluate as electrical
                        rows=[v["measurement"] for v in r["points"].values()]
                        if electrical(rows,board)["status"]!="PASS":raise ValueError("Medidas incompletas/inconsistentes")
                except (OSError,ValueError,KeyError,TypeError,AttributeError) as exc:
                    status="BLOCKED";reason=str(exc)
            checks[test]={"status":status,"reason":reason}
        boards[board]={"checks":checks,"T06":summarize([checks[t]["status"] for t in REQUIRED[:2]]),
                       "T08":checks["t08"]["status"]}
    result={"schema":1,"boards":boards}
    for task in ("T06","T08"):
        s=summarize([b[task] for b in boards.values()])
        result[task]={"status":s,"conclusion":{"PASS":"Cumple registros requeridos en ambas BBB; revision humana pendiente",
              "FAIL":"Necesita correcciones","BLOCKED":"Bloqueada por evidencia/prerrequisito",
              "NOT_TESTED":"Lista para prueba; mediciones incompletas"}[s]}
    return result
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();m=Path(a.manifest)
    try: report=evaluate(json.loads(m.read_text()),m.parent)
    except (OSError,ValueError) as exc:report={"status":"BLOCKED","error":str(exc)}
    atomic_json(a.output,report);print(json.dumps(report,indent=2))
if __name__=="__main__":main()
