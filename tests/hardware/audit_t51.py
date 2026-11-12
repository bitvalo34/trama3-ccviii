"""Audita conectividad exportada; NO mide electricidad ni autoriza montaje."""
import csv
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def audit():
    base=ROOT/"hardware/diseno-placas"
    tree=ET.parse(str(base/"netlist/kicad-export.xml"))
    nets={n.attrib["name"]:{c.attrib["ref"]+"."+c.attrib["pin"] for c in n}
          for n in tree.findall("./nets/net")}
    expected={
        "+5V_RAW":{"J1.1","J14.1","J11.1"},
        "+5V_FUSED":{"J14.2","J12.3"},
        "+5V_ACT":{"J12.2","C1.1","C2.1","J13.1","TP1.1"},
        "GATE_POL":{"J12.1","R30.1"},
        "+3V3_LOGIC":{"J10.1","U1.9","J5.1","J6.1","TP3.1"},
        "GND_ACT":{"NT1.1","J1.2","J4.1","Q3.1","Q4.1","TP2.1"},
        "GND_LOGIC":{"NT1.2","J10.2","U1.10","U2.3","TP4.1"},
        "CLK_REMOTE_A":{"J8.1","U2.1","D2.2"},
        "CLK_REMOTE_K":{"J8.2","U2.2","D2.1"},
        "CLK_RX_RAW":{"U2.4","R26.2","R27.1","TP8.1"},
        "+5V_SERVO":{"J13.2","J4.2","R12.1","R15.1","C3.1"},
        "SERVO_SIG":{"J13.5","J4.3","R16.1","TP9.1"},
        "C0_SEL":{"JP10.2","R20.1","R23.1"},
        "C1_SEL":{"JP11.2","R21.1","R24.1"},
        "C2_SEL":{"JP12.2","R22.1","R25.1"},
    }
    checks=[]
    for name,nodes in expected.items():
        checks.append({"net":name,"status":"PASS" if nodes<=nets.get(name,set()) else "FAIL"})
    with (base/"netlist/redes.csv").open(encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f):
            nodes=set(r["terminales"].split("; "))
            checks.append({"net_csv":r["red"],"status":"PASS" if nodes<=nets.get(r["red"],set()) else "FAIL"})
    # Dos redes distintas y la isla de LED remota no mezcla emisores/colectores locales.
    checks.append({"isolation_topology":"PASS" if
      not (nets["CLK_REMOTE_A"]|nets["CLK_REMOTE_K"]) & (nets["GND_LOGIC"]|nets["GND_ACT"]) else "FAIL"})
    hashes={}
    for p in (base/"esquematicos").glob("*.kicad_sch"):
        text=p.read_text(encoding="utf-8")
        assert "(kicad_sch" in text
        hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    return {"origin":"static_netlist_audit","status":"PASS" if all(c.get("status",c.get("isolation_topology"))=="PASS" for c in checks) else "FAIL",
            "checks":checks,"schematic_hashes":hashes,"physical":"NOT_TESTED",
            "note":"Coincidencia de redes no certifica componentes, polaridad fisica, transitorios ni fusible"}
if __name__=="__main__":
    print(json.dumps(audit(),indent=2))
