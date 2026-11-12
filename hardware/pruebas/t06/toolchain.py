"""Inventario de compilacion, sin instalaciones ni carga."""
import glob
import os
import shutil
import sys
from pathlib import Path
from common import execute,read
def inspect_tools(log):
    compiler=os.environ.get("CLPRU") or shutil.which("clpru")
    candidates=[]
    if not compiler:
        for root in ("/usr/share/ti","/usr/lib/ti","/opt"):
            for pattern in ("*/bin/clpru","*/*/bin/clpru","*/*/*/bin/clpru","*/*/*/*/bin/clpru"):
                candidates.extend(glob.glob(root+"/"+pattern))
        candidates=sorted(set(candidates))
        if len(candidates)==1:compiler=candidates[0]
    result={"python":sys.version.split()[0],"gcc":shutil.which("gcc"),
            "clpru":compiler,"candidates":candidates}
    if compiler:
        root=Path(compiler).resolve().parents[1]
        result.update({"lnkpru":str(root/"bin/lnkpru"),"headers":(root/"include/stdint.h").is_file(),
                       "runtime_library":(root/"lib/libc.a").is_file(),
                       "linker_present":(root/"bin/lnkpru").is_file()})
        result["compiler_version"]=execute([compiler,"--compiler_revision"],log)
    if result["gcc"]:result["gcc_version"]=execute(["gcc","-dumpversion"],log)
    result["module"]={name:{k:read("/sys/module/"+name+"/"+k) for k in ("version","srcversion")}
                      for name in ("pru_rproc","pruss","pwm_tiehrpwm")}
    result["kernel_note"]="Version remoteproc ligada a uname -r; version separada puede no existir"
    result["compatible_candidate"]=bool(compiler and result.get("linker_present") and result.get("headers") and result.get("runtime_library") and result["gcc"])
    return result
