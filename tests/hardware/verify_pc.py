#!/usr/bin/env python3
"""Verificacion reproducible sin BBB. Salidas se escriben fuera de las fuentes."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True)
    a=ap.parse_args();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,TEMP=str(out),TMP=str(out),PYTHONIOENCODING='utf-8')
    records=[]
    def check(label,cmd,expected=0):
        try:
            r=subprocess.run([str(x) for x in cmd],cwd=str(ROOT),env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=90)
            status='PASS' if r.returncode==expected else 'FAIL'
            text=r.stdout+r.stderr
            if 'NtCreateDirectoryObject' in text and '0xC0000022' in text:
                status='BLOCKED'
            record={'test':label,'status':status,'exit_code':r.returncode,'output':text.replace(str(ROOT),'<repo>').replace(str(out),'<validation>')}
        except (OSError,subprocess.TimeoutExpired) as e:
            record={'test':label,'status':'BLOCKED','output':str(e)}
        records.append(record);print(label+': '+record['status']);return record['status']=='PASS'
    check('python_unittest',[sys.executable,'tests/hardware/test_hardware.py'])
    check('netlist_static',[sys.executable,'tests/hardware/audit_t51.py'])
    gcc=shutil.which('gcc')
    if not gcc and os.name=='nt' and Path('C:/mingw64/bin/gcc.exe').exists():gcc='C:/mingw64/bin/gcc.exe'
    if gcc:
        exe=out/('firmware-model.exe' if os.name=='nt' else 'firmware-model')
        if check('compile_firmware_model',[gcc,'-std=c99','-O2','-Wall','-Wextra','-Wno-unknown-pragmas','-Itests/hardware','tests/hardware/test_firmware.c','-o',exe]):
            check('run_firmware_model',[exe])
        if os.name!='nt':
            host=out/'host-check'
            if check('compile_host_native',[gcc,'-std=c99','-O2','-Wall','-Wextra','-Werror','hardware/pruebas/t06/src/host.c','-o',host]):
                check('host_usage_no_hardware',[host],2)
    bash=shutil.which('bash')
    if os.name=='nt' and Path('C:/Program Files/Git/bin/bash.exe').exists():bash='C:/Program Files/Git/bin/bash.exe'
    if bash:
        for script in sorted((ROOT/'hardware/pruebas').rglob('*.sh')):
            check('bash_syntax:'+script.name,[bash,'-n',script.as_posix()])
    check('empty_acceptance',[sys.executable,'hardware/pruebas/evaluar.py','--manifest','hardware/pruebas/aceptacion-vacia.json','--output',out/'empty.json'])
    empty=json.loads((out/'empty.json').read_text()) if (out/'empty.json').exists() else {'T06':{},'T08':{}}
    records.append({'test':'empty_never_pass','status':'PASS' if all(empty[t].get('status')=='NOT_TESTED' for t in ('T06','T08')) else 'FAIL'})
    csv=out/'blank.csv'
    if csv.exists():csv=out/'blank-next.csv'
    check('create_csv',[sys.executable,'hardware/pruebas/t08/registrar-mediciones.py','--board','BBB-A','--file',csv])
    check('evaluate_blank_csv',[sys.executable,'hardware/pruebas/t08/evaluar-mediciones.py','--board','BBB-A','--file',csv,'--output',out/'blank.json'],3)
    check('audit_pc_blocks',[sys.executable,'hardware/pruebas/t06/run.py','preflight','--board','BBB-A','--results',out/'audit'],4)
    broken=[]
    for folder in ('hardware/documentacion','hardware/pruebas'):
        for doc in (ROOT/folder).rglob('*.md'):
            text=doc.read_text(encoding='utf-8')
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if '://' in link or link.startswith('#'):continue
                if not (doc.parent/link.split('#')[0]).exists():broken.append(str(doc.relative_to(ROOT))+': '+link)
    records.append({'test':'local_document_links','status':'FAIL' if broken else 'PASS','broken':broken})
    report={'origin':'software_validation','physical_tests':'NOT_TESTED','python':sys.version.split()[0],'platform':sys.platform,
            'status':'FAIL' if any(r['status']=='FAIL' for r in records) else 'BLOCKED' if any(r['status']=='BLOCKED' for r in records) else 'PASS','checks':records}
    (out/'validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=True)+'\n')
    print(report['status']);return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(main())
