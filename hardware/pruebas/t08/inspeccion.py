#!/usr/bin/env python3
"""Auditoria de solo lectura. No prueba voltajes ni sustituye multimetro."""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import default_results, identity, read, execute, atomic_json, result_dir

def collect():
    info=identity(); commands=[]
    for cmd in (["uname","-r"],["uptime"],["free","-m"],["df","-Pk","/"],
                ["systemctl","--failed","--no-legend","--no-pager"],
                ["systemctl","is-system-running"],["cat","/proc/stat"]):
        execute(cmd,commands)
    # Publicar conteos por categoria, NO mensajes crudos con identificadores.
    kernel_result=execute(["dmesg"])
    kernel=kernel_result["stdout"]
    errors={k:len(re.findall(pattern,kernel,re.I)) if kernel_result["exit_code"]==0 else None for k,pattern in (
        ("io_error",r"I/O error"),("filesystem_error",r"EXT4-fs error"),
        ("brownout_report",r"under.?voltage|brownout"),
        ("pru_error",r"(?:pru|remoteproc).*?(?:fail|error)"))}
    cpu={"origin":"inferred_from_system_counters","percent":None,"interval_seconds":0.2}
    def counters():
        data=read("/proc/stat","").splitlines()
        if not data or not data[0].startswith("cpu "):return None
        values=[int(v) for v in data[0].split()[1:9]]
        return sum(values),values[3]+values[4]
    before=counters();time.sleep(.2);after=counters()
    if before and after and after[0]>before[0]:
        cpu["percent"]=100.0*(1.0-(after[1]-before[1])/(after[0]-before[0]))
    temperature=[]
    for p in Path("/sys/class/thermal").glob("thermal_zone*"):
        temperature.append({"type":read(p/"type"),"reported_millicelsius":read(p/"temp"),
                            "origin":"system_report","calibration":"not_verified"})
    power=[]
    # Solo campos publicos definidos; no seriales ni IDs de bateria.
    for p in Path("/sys/class/power_supply").glob("*"):
        power.append({k:read(p/k) for k in ("type","online","status","voltage_now","current_now")})
    cores=[]
    for p in Path("/sys/class/remoteproc").glob("remoteproc*"):
        cores.append({k:read(p/k) for k in ("name","state","firmware")})
    pwm=[]
    for p in Path("/sys/class/pwm").glob("pwmchip*"):
        pwm.append({"path":str(p),"device":str((p/"device").resolve()),"npwm":read(p/"npwm")})
    pins=[]
    for pin in ("P8_11","P8_15","P8_16","P9_24","P9_27","P9_14"):
        pins.append(execute(["config-pin","-q",pin]))
    return {"schema":1,"test":"sistema","identity":info,"origin":"system_report",
            "status":"NOT_TESTED","commands":commands,"temperature":temperature,
            "cpu_usage":cpu,"kernel_log_available":kernel_result["exit_code"]==0,
            "power_reported":power,"physical_voltage":None,
            "undervoltage":"NO_DISPONIBLE: conteos de log no son medicion del riel",
            "error_categories":errors,"pru":cores,"pwm":pwm,"pinmux":pins,
            "physical_status":"NOT_TESTED"}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--board",choices=("BBB-A","BBB-B"),required=True)
    p.add_argument("--results",default=default_results())
    a=p.parse_args(); d=result_dir(a.results,a.board)
    report=collect();report["board"]=a.board
    atomic_json(d/"sistema.json",report);print(str(d))
if __name__=="__main__": main()
