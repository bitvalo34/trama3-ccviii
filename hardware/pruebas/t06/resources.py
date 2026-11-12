"""Deteccion y adquisicion exclusiva. El constructor no modifica hardware."""
import glob
import hashlib
import os
import re
import shutil
import time
from pathlib import Path
from common import Blocked, read, checked, atomic_json

PININFO = {"P8_11": (13, 45), "P8_15": (15, 47), "P8_16": (14, 46),
           "P9_24": (97, 15), "P9_27": (105, 115), "P9_14": (18, 50)}
SAFE_MODES = ("default", "gpio_input", "gpio_pd", "gpio_pu")

class Hardware:
    def __init__(self, root="/", log=None):
        self.root = Path(root)
        self.log = log if log is not None else []
    def p(self, absolute):
        return self.root / absolute.lstrip("/")
    def write(self, path, value):
        with Path(path).open("w") as f:
            f.write(str(value))
        self.log.append({"write": str(path), "value": str(value), "exit_code": 0})
    def command(self, args):
        return checked(args, self.log)
    def pwm(self):
        found=[]
        for chip in self.p("/sys/class/pwm").glob("pwmchip*"):
            ident = str(chip.resolve()) + " " + str((chip / "device").resolve())
            if re.search(r"48302200", ident) or ("48302000" in ident and "ehrpwm" in ident):
                if read(chip / "npwm") == "2":
                    found.append(chip)
        if len(found)!=1:
            raise Blocked("No se identifica un unico eHRPWM1/P9_14; no se adivina pwmchip")
        return found[0]
    def pwm_free(self, chip):
        if list(chip.glob("pwm[0-9]*")):
            raise Blocked("eHRPWM1 ya exportado (canales A/B comparten periodo)")
        debug = read(self.p("/sys/kernel/debug/pwm"))
        if not debug:
            raise Blocked("Falta lectura debugfs PWM; no se puede descartar consumidor kernel")
        blocks = re.split(r"(?m)(?=^\S)", debug)
        relevant=[b for b in blocks if "48302200" in b or "48302000" in b]
        if len(relevant)!=1:
            raise Blocked("Identidad PWM no corroborada en debugfs")
        if re.search(r"requested|enabled", relevant[0]):
            raise Blocked("PWM solicitado por otro controlador; no tocar ninguno de sus canales")
    def remoteprocs(self):
        cores={}
        for r in self.p("/sys/class/remoteproc").glob("remoteproc*"):
            ident=str(r.resolve())+" "+str((r/"device").resolve())+" "+(read(r/"name",""))
            for key,addr in (("pru0","4a334000"),("pru1","4a338000")):
                if addr in ident:
                    if key in cores:
                        raise Blocked("Identidad PRU ambigua")
                    cores[key]=r
        if set(cores)!=set(("pru0","pru1")):
            raise Blocked("No se identifican ambos PRU por direccion AM335x")
        return cores
    def offline(self):
        cores=self.remoteprocs()
        if any(read(r/"state")!="offline" for r in cores.values()):
            raise Blocked("PRU ocupado; no se detiene firmware ajeno")
        # IEP tambien puede pertenecer a un driver Ethernet/ptp.
        if list(self.p("/sys/class/ptp").glob("ptp*")):
            raise Blocked("Existe reloj PTP; resolver propiedad IEP antes de usarlo")
        return cores["pru0"]
    def pin_state(self, pin):
        found = list(self.p("/sys/devices/platform").glob("**/*"+pin+"_pinmux/state"))
        if len(found)!=1:
            raise Blocked("Falta estado pinmux unico para "+pin)
        return found[0]
    def pin_check(self, pin, mode):
        state=self.pin_state(pin)
        old=read(state)
        if old not in SAFE_MODES:
            raise Blocked("{} ocupado/modo no seguro: {}".format(pin,old))
        available=self.command(["config-pin","-l",pin]).split()
        if mode not in available:
            raise Blocked("Modo no publicado: "+pin+" "+mode)
        pads=PININFO[pin]
        owners="\n".join(read(p,"") for p in self.p("/sys/kernel/debug/pinctrl").glob("*/pinmux-pins"))
        match=re.search(r"(?m)^pin "+str(pads[0])+r"\s.*$",owners)
        if not match or not (pin in match.group() or "MUX UNCLAIMED" in match.group()):
            raise Blocked("Propietario pinctrl desconocido/ajeno: "+pin)
        gpio=read(self.p("/sys/kernel/debug/gpio"))
        if gpio is None:
            raise Blocked("Sin inventario de consumidores GPIO")
        gpio_line=re.search(r"(?m)^\s*gpio-{}\s.*$".format(pads[1]),gpio)
        if gpio_line and not (pin in gpio_line.group() and re.search(r"\bin\b",gpio_line.group())):
            raise Blocked("GPIO solicitado por otro consumidor o salida: "+pin)
        return {"pin":pin,"path":str(state),"old":old,"mode":mode}
    def pin_set(self, rec, mode):
        self.command(["config-pin",rec["pin"],mode])
        if read(rec["path"])!=mode:
            raise Blocked("Pinmux no confirma "+rec["pin"])
    def wait_path(self, path, exists=True):
        limit=time.monotonic()+2
        while Path(path).exists()!=exists and time.monotonic()<limit:
            time.sleep(.02)
        if Path(path).exists()!=exists:
            raise Blocked("No aparecio/desaparecio "+str(path))

class Transaction:
    def __init__(self, hw, journal):
        self.hw=hw
        self.path=Path(journal)
        self.data={"schema":1,"pins":[],"pwm":None,"pru":None,"firmware":None,
                   "boot_id":read(hw.p("/proc/sys/kernel/random/boot_id"))}
    def save(self):
        atomic_json(self.path,self.data)
    def pin(self, record, mode):
        # Guardar ANTES de una mutacion para poder recuperar una escritura parcial.
        if not any(r["pin"]==record["pin"] for r in self.data["pins"]):
            self.data["pins"].append(record)
            self.save()
        self.hw.pin_set(record,mode)
    def pwm_export(self, chip):
        # export EBUSY no nos concede propiedad. La bandera se activa solo al obtenerlo.
        self.hw.write(chip/"export",0)
        self.data["pwm"]=str(chip); self.save()
        self.hw.wait_path(chip/"pwm0")
    def firmware_start(self, remote, source):
        old=read(remote/"firmware")
        if old is None: raise Blocked("No hay selector firmware remoteproc")
        digest=hashlib.sha256(Path(source).read_bytes()).hexdigest()
        # Nombre con contenido, nunca reemplazar un binario previo.
        dest=self.hw.p("/lib/firmware/trama3-t06-"+digest[:16]+".out")
        if dest.exists():
            if hashlib.sha256(dest.read_bytes()).hexdigest()!=digest:
                raise Blocked("Colision firmware: no sobrescribir")
        else:
            with dest.open("xb") as f: f.write(Path(source).read_bytes())
            self.data["firmware"]=str(dest)
        self.data["pru"]={"path":str(remote),"old":old,"name":dest.name}
        self.save()
        self.hw.write(remote/"firmware",dest.name)
        if read(remote/"firmware")!=dest.name:
            raise Blocked("Selector firmware no confirmado")
        self.hw.write(remote/"state","start")
        if read(remote/"state")!="running":
            raise Blocked("remoteproc no running")
    def cleanup(self):
        errors=[]
        pru=self.data["pru"]
        if pru:
            r=Path(pru["path"])
            current=read(r/"firmware")
            if current!=pru["name"] and not (current==pru["old"] and read(r/"state")=="offline"):
                return {"restored":False,"errors":["Propietario PRU cambio; conservar diario y no alterar pines/recursos ajenos"]}
        def attempt(label, fn):
            try: fn()
            except Exception as exc: errors.append(label+": "+str(exc))
        pwm=self.data["pwm"]
        if pwm:
            ch=Path(pwm)/"pwm0"
            if ch.exists():
                attempt("PWM duty=0",lambda:self.hw.write(ch/"duty_cycle",0))
                attempt("PWM disable",lambda:self.hw.write(ch/"enable",0))
                if read(ch/"enable")!="0": errors.append("PWM sigue habilitado")
                # No afirmar nivel bajo tras disable: kernel no lo garantiza.
        # Desacoplar salida PRU antes de detener; no tocar entrada ni cargas.
        for rec in self.data["pins"]:
            if rec["pin"]=="P8_11":
                attempt("aislar salida PRU",lambda:self.hw.pin_set(rec,"gpio_pd"))
        pru=self.data["pru"]
        if pru:
            r=Path(pru["path"])
            current=read(r/"firmware")
            if current==pru["old"] and read(r/"state")=="offline":
                pass  # Recuperacion idempotente de una restauracion parcial.
            elif current!=pru["name"]:
                errors.append("Firmware cambio de propietario; no detener recurso ajeno")
            else:
                if read(r/"state")=="running":
                    attempt("PRU stop",lambda:self.hw.write(r/"state","stop"))
                if read(r/"state")!="offline": errors.append("PRU no offline")
                else: attempt("restaurar selector firmware",lambda:self.hw.write(r/"firmware",pru["old"]))
        for rec in reversed(self.data["pins"]):
            attempt("restaurar "+rec["pin"],lambda rec=rec:self.hw.pin_set(rec,rec["old"]))
        if pwm and (Path(pwm)/"pwm0").exists():
            attempt("PWM unexport",lambda:self.hw.write(Path(pwm)/"unexport",0))
            attempt("verificar unexport",lambda:self.hw.wait_path(Path(pwm)/"pwm0",False))
        # Solo borrar firmware propio cuando PRU efectivamente offline.
        fw=self.data["firmware"]
        if fw and Path(fw).exists() and (not pru or read(Path(pru["path"])/"state")=="offline"):
            attempt("retirar firmware temporal",lambda:Path(fw).unlink())
        if not errors and self.path.exists(): self.path.unlink()
        return {"restored":not errors,"errors":errors}
