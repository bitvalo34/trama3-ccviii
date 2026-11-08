
import os,tempfile,subprocess,pathlib,shutil
repo=pathlib.Path(__file__).resolve().parents[2]
src=(repo/'hardware/configuracion/t04-bbb.sh').read_text()
cases=['ok','busy','uart','mode_missing','apply_failure','no_confirmation']
for case in cases:
 with tempfile.TemporaryDirectory() as td:
  root=pathlib.Path(td);sys=root/'sys';proc=root/'proc';home=root/'home';bin=root/'bin'
  for p in [sys,proc,home,bin]:p.mkdir()
  (proc/'device-tree').mkdir();(proc/'device-tree/model').write_text('TI AM335x BeagleBone Black')
  for i,addr in enumerate(['4a334000','4a338000']):
   p=sys/('class/remoteproc/remoteproc'+str(i));p.mkdir(parents=True)
   (p/'name').write_text(addr+'.pru')
   (p/'state').write_text('running' if case=='busy' and i==0 else 'offline')
  for pin in ['P8_11','P8_15','P8_16','P9_24','P9_27']:
   p=sys/('devices/platform/ocp/ocp:'+pin+'_pinmux');p.mkdir(parents=True)
   (p/'state').write_text('uart' if case=='uart' and pin=='P9_24' else 'gpio')
  (bin/'sudo').write_text('#!/bin/bash\n[ "$1" = -n ] && shift\nexec "$@"\n')
  (bin/'config-pin').write_text('''#!/bin/bash
case "$1" in
-l) if [ "$CASE" = mode_missing ] && [ "$2" = P9_27 ]; then echo gpio; else echo "gpio pruin pruout"; fi;;
-q) cat "$FIX/sys/devices/platform/ocp/ocp:$2""_pinmux/state";;
*) if [ "$CASE" = apply_failure ] && [ "$1" = P8_16 ] && [ "$2" = pruin ]; then exit 1; fi
printf '%s' "$2" > "$FIX/sys/devices/platform/ocp/ocp:$1""_pinmux/state";;
esac
''')
  for p in bin.iterdir():p.chmod(0o755)
  code=src.replace('/proc/',str(proc)+'/').replace('/sys/',str(sys)+'/')
  script=root/'test.sh';script.write_text(code)
  env=dict(os.environ,HOME=str(home),PATH=str(bin)+':'+os.environ['PATH'],CASE=case,FIX=str(root),T04_SIN_CARGAS='SI' if case!='no_confirmation' else '')
  run=subprocess.run(['bash',str(script),'A','pin-test'],env=env,capture_output=True,text=True,timeout=30)
  expected=0 if case=='ok' else 5 if case=='apply_failure' else 4
  assert run.returncode==expected,(case,run.returncode,run.stdout,run.stderr)
  for p in sys.glob('devices/platform/ocp/*/state'):
   expectedstate='uart' if case=='uart' and 'P9_24' in str(p) else 'gpio'
   assert p.read_text()==expectedstate,(case,p,p.read_text())
  if case=='ok':assert run.stdout.count('RESTAURADO ')==5
  print(case,'OK (simulado; no hardware)')
