#!/usr/bin/env python3
"""Entrada T06; auditoria por defecto. Nunca instala paquetes ni conecta equipos."""
from __future__ import print_function
import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from common import default_results, Blocked, read, checked, atomic_json, identity, require_bbb, result_dir
from resources import Hardware, Transaction
from analyze import analyze
from toolchain import inspect_tools

ACTIONS=("preflight","pwm","pru-smoke","pru-tx","pru-rx","loopback","pwm-capture","inputs","cleanup")
CONNECTIONS={
 "pwm":"Sin servo/cargas. P9_14 solo a instrumento 3.3 V, GND P9_1.",
 "pru-smoke":"P8/P9 sin conexiones externas. No acredita captura fisica.",
 "pru-tx":"P8_11 solo a instrumento 3.3 V, GND P9_1; sin actuadores.",
 "pru-rx":"P9_14 -> 1 kohm -> P8_15, misma BBB; fuente PWM separada no gestionada por esta prueba.",
 "loopback":"P8_11 -> 1 kohm -> P8_15; misma BBB, sin placa T51, sin segunda BBB.",
 "pwm-capture":"P9_14 -> 1 kohm -> P8_15; misma BBB, sin servo/placa T51.",
 "inputs":"P8_16/P9_24/P9_27 -> 10 kohm -> GND P9_1; opcional mover UNO a P9_3 con placa apagada.",
 "cleanup":"Retirar cargas solo con alimentacion apagada; recuperar unicamente diario propio.",
 "preflight":"Solo lectura: no requiere conexiones."}

def options(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("action",choices=ACTIONS,nargs="?",default="preflight")
    p.add_argument("--board",choices=("BBB-A","BBB-B"),required=True)
    p.add_argument("--active",action="store_true",help="autoriza cambio temporal de hardware")
    p.add_argument("--fixture",choices=("none","loopback","pwm-loopback","inputs"),default="none")
    p.add_argument("--electrical-checked",action="store_true",help="confirma checklist fisico previo")
    p.add_argument("--period-us",type=int,default=20000)
    p.add_argument("--high-us",type=int,default=1500)
    p.add_argument("--cycles",type=int,default=25)
    p.add_argument("--seconds",type=float,default=2.0)
    p.add_argument("--results",default=default_results())
    a=p.parse_args(argv)
    if not 1000<=a.period_us<=100000 or not 100<=a.high_us<a.period_us:
        p.error("Periodo 1000..100000 us; ancho >=100 us y menor al periodo")
    if not 2<=a.cycles<=200 or not .5<=a.seconds<=10:
        p.error("Ciclos 2..200; duracion 0.5..10 s")
    if a.action in ("pwm","pwm-capture") and (a.period_us!=20000 or not 1000<=a.high_us<=2000):
        p.error("PWM P9_14: periodo fijo 20000 us; ancho 1000..2000 us")
    if a.action in ("pru-tx","loopback") and a.period_us*(a.cycles+2)>a.seconds*1e6:
        p.error("Duracion insuficiente para ciclos y guardas")
    return a

def lock_resources(hw):
    import fcntl
    base=hw.p("/run/trama3-t06")
    base.mkdir(mode=0o700,exist_ok=True)
    st=base.lstat()
    if base.is_symlink() or st.st_uid!=0 or st.st_mode&0o077:
        raise Blocked("Directorio de bloqueo debe pertenecer a root y modo 700")
    fd=os.open(str(base/"lock"),os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    try: fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except IOError:
        os.close(fd); raise Blocked("Otra prueba T06 tiene el bloqueo")
    return fd,base/"state.json"

def preflight(hw, info):
    problems=[]; detected={}
    detected["toolchain"]=inspect_tools(hw.log)
    if not detected["toolchain"]["compatible_candidate"]: problems.append("Toolchain incompleto; ver detected.toolchain y build.sh")
    for name,fn in (("pwm",hw.pwm),("remoteprocs",hw.remoteprocs)):
        try:
            value=fn()
            detected[name]={k:str(v) for k,v in value.items()} if isinstance(value,dict) else str(value)
        except Blocked as exc: problems.append(str(exc))
    for pin in ("P8_11","P8_15","P8_16","P9_24","P9_27","P9_14"):
        try: detected[pin]=read(hw.pin_state(pin))
        except Blocked as exc: problems.append(str(exc))
    detected["dev_mem"]=hw.p("/dev/mem").exists()
    detected["host_built"]=(HERE/"build/trama3-t06-host").is_file()
    detected["firmware_built"]=(HERE/"build/trama3-t06-pru0.out").is_file()
    detected["free_bytes"]=__import__("shutil").disk_usage(str(HERE)).free
    try: require_bbb(info)
    except Blocked as exc: problems.append(str(exc))
    return {"status":"BLOCKED" if problems else "NOT_TESTED","detected":detected,
            "problems":problems,"physical_status":"NOT_TESTED"}

def perform(a,hw,tx):
    action=a.action
    expected={"loopback":"loopback","pwm-capture":"pwm-loopback","pru-rx":"pwm-loopback","inputs":"inputs"}.get(action,"none")
    if a.fixture!=expected or not a.electrical_checked:
        raise Blocked("Falta --electrical-checked y/o fixture correcto: "+expected)
    use_pwm=action in ("pwm","pwm-capture")
    use_pru=action not in ("pwm",)
    chip=None; remote=None; records={}
    if use_pru:
        remote=hw.offline()
        for f in ("trama3-t06-pru0.out","trama3-t06-host"):
            if not (HERE/"build"/f).is_file(): raise Blocked("Ejecutar bash build.sh; falta "+f)
        if not hw.p("/dev/mem").exists(): raise Blocked("No existe /dev/mem; no forzar kernel")
    desired={}
    if use_pwm:
        chip=hw.pwm(); hw.pwm_free(chip); desired["P9_14"]="pwm"
    if action in ("pru-tx","loopback"): desired["P8_11"]="pruout"
    if action in ("pru-rx","loopback","pwm-capture"): desired["P8_15"]="pruin"
    if action=="inputs":
        for p in ("P8_16","P9_24","P9_27"): desired[p]="pruin"
    # Validar TODO antes de la primera mutacion.
    for pin,mode in desired.items(): records[pin]=hw.pin_check(pin,mode)
    if "P8_11" in desired:
        # Cleanup necesita un modo de entrada corroborado, nunca dos salidas.
        if "gpio_pd" not in hw.command(["config-pin","-l","P8_11"]).split():
            raise Blocked("No se dispone de gpio_pd para desacoplar TX")
    if use_pru:
        tx.firmware_start(remote,HERE/"build/trama3-t06-pru0.out")
        probe=json.loads(hw.command([str(HERE/"build/trama3-t06-host"),"probe"]))
        if not probe.get("ready"): raise Blocked("Firmware no responde/ABI incorrecta")
    # Firmware ya puso R30 bajo ANTES de seleccionar pruout.
    for pin in sorted(desired,key=lambda x:x=="P8_11"):
        tx.pin(records[pin],desired[pin])
    config=None
    if use_pwm:
        hw.pwm_free(chip)  # segunda comprobacion antes de adquirir canal
        tx.pwm_export(chip); ch=chip/"pwm0"
        hw.write(ch/"enable",0)
        hw.write(ch/"duty_cycle",0)
        hw.write(ch/"period",20000000)
        hw.write(ch/"polarity","normal")
        hw.write(ch/"duty_cycle",a.high_us*1000)
        expected_values={"period":"20000000","duty_cycle":str(a.high_us*1000),"polarity":"normal"}
        if any(read(ch/k)!=v for k,v in expected_values.items()):
            raise Blocked("PWM readback no coincide")
        hw.write(ch/"enable",1)
        if read(ch/"enable")!="1": raise Blocked("PWM no habilitado")
        config={"configured":True,"enabled_readback":True,"observed":False,
                "frequency_checked":False,"pulse_width_checked":False,
                "period_ns":20000000,"high_ns":a.high_us*1000,"chip":str(chip),"config_status":"PASS"}
    if action=="pwm":
        time.sleep(a.seconds)
        return {"status":"NOT_TESTED","pwm":config,"note":"Configuracion verificada; falta observar señal"}
    if action=="pru-smoke":
        return {"status":"PASS","scope":"software_start_only","physical_status":"NOT_TESTED"}
    mode={"pru-tx":1,"pru-rx":2,"loopback":3,"pwm-capture":2,"inputs":4}[action]
    rawtext=hw.command([str(HERE/"build/trama3-t06-host"),"run",str(mode),
                       str(a.period_us),str(a.high_us),str(a.cycles),str(int(a.seconds*1000))])
    raw=json.loads(rawtext)
    analysis=analyze(raw,a.period_us,a.high_us,action,a.cycles)
    if config and analysis["status"]=="PASS":
        config.update({"observed":True,"frequency_checked":True,"pulse_width_checked":True})
    return {"status":analysis["status"],"raw":raw,"analysis":analysis,"pwm":config,
            "physical_status":analysis["status"] if analysis["observed_input"] else "NOT_TESTED"}

def main(argv=None):
    a=options(argv); print(CONNECTIONS[a.action])
    dest=result_dir(a.results,a.board)
    log=[]; hw=Hardware(log=log); info=identity()
    report={"schema":1,"board":a.board,"test":a.action,"identity":info,
            "origin":"hardware" if a.active else "system_report","active":a.active,
            "status":"NOT_TESTED","commands":log,"electrical_confirmation":a.electrical_checked,
            "fixture":a.fixture,"parameters":{"period_us":a.period_us,"high_us":a.high_us,"cycles":a.cycles,"seconds":a.seconds}}
    tx=None; fd=None
    try:
        if not a.active:
            report.update(preflight(hw,info))
        else:
            require_bbb(info)
            if os.geteuid()!=0: raise Blocked("Prueba activa requiere sudo; auditoria no")
            fd,journal=lock_resources(hw)
            if a.action=="cleanup":
                if not journal.exists():
                    report.update({"status":"NOT_TESTED","note":"Sin diario propio; no tocar recursos"})
                else:
                    tx=Transaction(hw,journal); tx.data=json.loads(journal.read_text())
                    if tx.data.get("boot_id")!=read(hw.p("/proc/sys/kernel/random/boot_id")):
                        tx=None; raise Blocked("Diario de otro arranque: no aplicar estados antiguos")
                    report["status"]="PASS"
            else:
                if journal.exists(): raise Blocked("Existe diario incompleto: ejecutar cleanup --active")
                if a.action=="preflight":
                    report.update(preflight(hw,info))
                else:
                    tx=Transaction(hw,journal)
                    def stop(signum,frame): raise KeyboardInterrupt("Señal "+str(signum))
                    for s in (signal.SIGINT,signal.SIGTERM,signal.SIGHUP): signal.signal(s,stop)
                    report.update(perform(a,hw,tx))
    except (Blocked,OSError,ValueError) as exc:
        report.update({"status":"BLOCKED","error":str(exc)})
    except KeyboardInterrupt as exc:
        report.update({"status":"FAIL","error":"Interrumpido: "+str(exc)})
    finally:
        if tx:
            final=tx.cleanup(); report["resources"]=final
            if not final["restored"]: report["status"]="FAIL"
        if fd is not None: os.close(fd)
        atomic_json(dest/(a.action+".json"),report)
        print(str(dest))
        print(report["status"])
    return {"PASS":0,"NOT_TESTED":0,"FAIL":5,"BLOCKED":4}[report["status"]]

if __name__=="__main__": sys.exit(main())
