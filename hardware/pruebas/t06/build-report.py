#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from common import identity,execute,result_dir,atomic_json,default_results,require_bbb,Blocked
from provenance import source_hashes,binary_hashes
import shutil
p=argparse.ArgumentParser()
p.add_argument("--board",choices=("BBB-A","BBB-B"),required=True)
p.add_argument("--results",default=default_results())
a=p.parse_args();d=result_dir(a.results,a.board)
info=identity()
try:
    require_bbb(info)
    if shutil.disk_usage(str(HERE)).free<16*1024*1024:raise Blocked("Menos de 16 MiB libres para fuentes/logs/build")
    r=execute(["bash",str(HERE/"build.sh")],timeout=120)
except (Blocked,OSError) as exc:
    r={"exit_code":4,"stderr":str(exc),"stdout":""}
report={"schema":2,"hardware_revision":"BBB-BARE","source_hashes":source_hashes(),"binary_hashes":binary_hashes(),"board":a.board,"test":"build","identity":info,
        "status":"PASS" if r["exit_code"]==0 and (HERE/"build/trama3-t06-pru0.out").exists() else "BLOCKED",
        "origin":"software_build","command":r,"physical_status":"NOT_TESTED"}
atomic_json(d/"build.json",report)
print(str(d));print(report["status"])
sys.exit(0 if report["status"]=="PASS" else 4)
