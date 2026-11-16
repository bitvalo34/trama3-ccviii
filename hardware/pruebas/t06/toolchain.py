"""Inventario de compilacion, sin instalaciones ni carga."""
import glob
import os
import shutil
import sys
from pathlib import Path
from common import execute,read
def select_runtime_root(roots):
    """Reject host libc: require the PRU v3 little-endian runtime as well."""
    for root in roots:
        root=Path(root)
        if all((root/item).is_file() for item in
               ("include/stdint.h", "lib/libc.a", "lib/rtspruv3_le.lib")):
            return root
    return None

def compiler_layout(compiler):
    compiler=Path(compiler).resolve()
    roots=[compiler.parents[1]]
    if compiler.parent==Path("/usr/bin"):
        roots.append(Path("/usr/share/ti/cgt-pru"))
    return compiler,select_runtime_root(roots),compiler.parent/"lnkpru"

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
        resolved,root,linker=compiler_layout(compiler)
        result.update({"lnkpru":str(linker),"headers":root is not None,
                       "runtime_root":str(root) if root else None,
                       "runtime_library":root is not None,
                       "linker_present":linker.is_file()})
        result["compiler_version"]=execute([compiler,"--compiler_revision"],log)
    if result["gcc"]:result["gcc_version"]=execute(["gcc","-dumpversion"],log)
    result["module"]={name:{k:read("/sys/module/"+name+"/"+k) for k in ("version","srcversion")}
                      for name in ("pru_rproc","pruss","pwm_tiehrpwm")}
    result["kernel_note"]="Version remoteproc ligada a uname -r; version separada puede no existir"
    result["compatible_candidate"]=bool(compiler and result.get("linker_present") and result.get("headers") and result.get("runtime_library") and result["gcc"])
    return result

if __name__=="__main__":
    compiler,root,linker=compiler_layout(sys.argv[1])
    if root is None or not linker.is_file():
        sys.stderr.write("BLOCKED: faltan headers/runtime PRU o lnkpru compatible\n")
        sys.exit(4)
    print(str(compiler))
    print(str(root))
