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
    atomic_json(a.output,result);print(result["status"])
    return {"PASS":0,"FAIL":5,"BLOCKED":4,"NOT_TESTED":3}[result["status"]]
if __name__=="__main__":sys.exit(main())
