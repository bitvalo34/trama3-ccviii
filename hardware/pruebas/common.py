"""Utilidades comunes. Python >=3.5, biblioteca estandar, sin red."""
from __future__ import print_function
import datetime
import json
import os
import re
import subprocess
import platform
import uuid
from pathlib import Path

class Blocked(RuntimeError):
    pass

def read(path, default=None):
    try:
        return Path(path).read_text().replace("\x00", "").strip()
    except (IOError, OSError, UnicodeError):
        return default

def safe_text(text):
    text = re.sub(r"(?i)\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b", "[MAC]", text)
    text = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[IP]", text)
    text = re.sub(r"(?i)(serial|password|token|secret)\s*[:=]\s*\S+", r"\1=[omitido]", text)
    return text

def execute(args, log=None, timeout=15):
    try:
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True, env=dict(os.environ, LC_ALL="C"))
        try:
            out, err = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            p.kill()
            out, err = p.communicate()
            result = {"command": args, "exit_code": 124,
                      "stdout": safe_text(out), "stderr": "Timeout: " + safe_text(err)}
            if log is not None:
                log.append(result)
            return result
        result = {"command": args, "exit_code": p.returncode,
                  "stdout": safe_text(out), "stderr": safe_text(err)}
    except OSError as exc:
        result = {"command": args, "exit_code": 127, "stdout": "", "stderr": str(exc)}
    if log is not None:
        log.append(result)
    return result

def checked(args, log=None, timeout=15):
    r = execute(args, log, timeout)
    if r["exit_code"]:
        raise Blocked("Comando fallo: {}: {}".format(args[0], r["stderr"][:300]))
    return r["stdout"]

def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w") as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(str(tmp), str(path))

def result_dir(base, board):
    if board not in ("BBB-A", "BBB-B"):
        raise ValueError("Placa no admitida")
    stamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dest = Path(base) / board / (stamp + "-" + uuid.uuid4().hex[:8])
    dest.mkdir(parents=True)
    return dest

def identity(root="/"):
    root = Path(root)
    return {"model": read(root / "proc/device-tree/model"),
            "debian": read(root / "etc/debian_version"),
            "os_release": read(root / "etc/os-release"),
            "kernel": platform.release(),
            "utc_board": datetime.datetime.utcnow().isoformat() + "Z",
            "clock_note": "Reloj BBB no contrastado; registrar tambien fecha PC."}

def require_bbb(info):
    if not info["model"] or "AM335" not in info["model"] or "BeagleBone Black" not in info["model"]:
        raise Blocked("Solo BeagleBone Black AM335x; identidad no comprobada")
    if not info["debian"] or info["debian"].split(".")[0] not in ("9", "10"):
        raise Blocked("Perfil validable solo Debian 9 o 10")

def default_results():
    # sudo conserva la carpeta del operador; sin HOME usar directorio actual.
    user=os.environ.get('SUDO_USER')
    if user:
        try:
            import pwd
            return str(Path(pwd.getpwnam(user).pw_dir)/'trama3-resultados')
        except (ImportError,KeyError):
            pass
    try: base=Path.home()
    except RuntimeError: base=Path.cwd()
    return str(base/'trama3-resultados')
