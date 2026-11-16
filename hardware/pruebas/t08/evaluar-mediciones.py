#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import atomic_json
from mediciones import read_csv,evaluate
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--board",choices=("BBB-A","BBB-B"),required=True)
    p.add_argument("--file",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--origin",choices=("physical","simulated"),default="physical")
    a=p.parse_args()
    try: result=evaluate(read_csv(a.file),a.board,a.origin)
    except (ValueError,OSError) as exc:
        result={"schema":1,"board":a.board,"test":"t08","origin":a.origin,"status":"BLOCKED","error":str(exc)}
    out=Path(a.output)
    if out.exists():p.error("No sobrescribir informe; use nombre nuevo")
    atomic_json(out,result)
    lines=["# T08 "+a.board,"",result["status"],"", "| Punto | Estado | Motivo |", "|---|---|---|"]
    for key,v in sorted(result.get("points",{}).items()):
        lines.append("| {} | {} | {} |".format(key,v["status"],v["reason"]))
    out.with_suffix(".md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(result["status"])
    return {"PASS":0,"FAIL":5,"BLOCKED":4,"NOT_TESTED":3}[result["status"]]
if __name__=="__main__":sys.exit(main())
