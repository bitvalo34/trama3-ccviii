#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from common import identity,execute,result_dir,atomic_json,default_results
p=argparse.ArgumentParser()
p.add_argument("--board",choices=("BBB-A","BBB-B"),required=True)
p.add_argument("--results",default=default_results())
a=p.parse_args();d=result_dir(a.results,a.board)
r=execute(["bash",str(HERE/"build.sh")],timeout=120)
report={"schema":1,"board":a.board,"test":"build","identity":identity(),
        "status":"PASS" if r["exit_code"]==0 and (HERE/"build/trama3-t06-pru0.out").exists() else "BLOCKED",
        "origin":"software_build","command":r,"physical_status":"NOT_TESTED"}
atomic_json(d/"build.json",report)
print(str(d));print(report["status"])
sys.exit(0 if report["status"]=="PASS" else 4)
