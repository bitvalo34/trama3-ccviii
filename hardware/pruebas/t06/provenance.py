"""Hashes para enlazar compilacion y ejecucion, sin confundir PC con BBB."""
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
def source_hashes():
    names=("firmware/main.c","firmware/abi.h","firmware/AM335x_PRU0.cmd","src/host.c","build.sh","toolchain.py")
    return {n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in names}
def binary_hashes():
    return {n:hashlib.sha256((HERE/"build"/n).read_bytes()).hexdigest()
            for n in ("trama3-t06-host","trama3-t06-pru0.out") if (HERE/"build"/n).is_file()}
