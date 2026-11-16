#!/usr/bin/env python3
"""Auditoria documental de netlist P2; no valida placa soldada."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
p=root/"hardware/documentacion/fuentes-P2/diseno.json"
d=json.loads(p.read_text(encoding="utf-8"))
parts={x["ref"]:x for x in d["components"]}
ext={x["ref"]:x for x in d["external"]}
checks=[]
def check(label,ok):checks.append({"check":label,"status":"PASS" if ok else "FAIL"})
check("revision P2",d["revision"]=="T51-P2-LOCAL")
for ref in ("J11","J12","MOD3"):check("retirado "+ref,ref not in parts and ref not in ext)
check("Q6 IRLZ44N","IRLZ44N" in parts["Q6"]["value"])
pins={str(x["number"]):x["net"] for x in parts["Q6"]["pins"]}
check("Q6 G/D/S",pins=={"1":"+5V_ACT","2":"NEG_IN","3":"GND_ACT"})
check("SW287","SW-287" in ext["SW1"]["value"])
check("SW287 terminal3 aislado",ext["SW1"]["pins"]["3"] is None)
check("R30","100" in parts["R30"]["value"])
check("J1 NEG_IN",next(x for x in parts["J1"]["pins"] if x["number"]=="2")["net"]=="NEG_IN")
report={"origin":"static_netlist","hardware_status":"NOT_TESTED","checks":checks}
print(json.dumps(report,indent=2))
raise SystemExit(0 if all(x["status"]=="PASS" for x in checks) else 1)
