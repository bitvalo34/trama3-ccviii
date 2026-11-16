"""Offline laboratory delivery. No download, installation or hardware access."""
import argparse
import hashlib
import io
import subprocess
import tarfile
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('output',type=Path)
    ap.add_argument('--offline',type=Path);ap.add_argument('--commit')
    args=ap.parse_args();root=Path(__file__).resolve().parents[2]
    names=subprocess.check_output(['git','ls-files'],cwd=str(root)).decode().splitlines()
    entries={}
    prefixes=('software/runtime102/','software/matrices102/','hardware/pruebas/',
              'hardware/documentacion/','tests/hardware/','docs/protocolo/','docs/planificacion/')
    for name in names:
        if not name.startswith(prefixes):continue
        if Path(name).suffix not in ('.cjs','.js','.py','.c','.h','.sh','.md','.json','.html','.csv','.cmd','.ps1','.txt'):continue
        if name in ('software/matrices102/ejemplo-corte-dos-medios.json','software/matrices102/resultados-integracion.json'):continue
        entries[name]=(root/name).read_bytes()
    commit=args.commit or subprocess.check_output(['git','rev-parse','HEAD'],cwd=str(root)).decode().strip()
    entries['software/runtime102/SOURCE_COMMIT']=(commit+'\n').encode()
    if args.offline:
        for name in ('node-v16.20.2-linux-armv7l.tar.xz','NODE_SHASUMS256.txt'):
            entries['offline/'+name]=(args.offline/name).read_bytes()
    manifest=''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n' for name,data in sorted(entries.items()))
    entries['SHA256SUMS']=manifest.encode()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('xb') as target:
        with tarfile.open(fileobj=target,mode='w:gz') as archive:
            for name,data in sorted(entries.items()):
                info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o644
                archive.addfile(info,io.BytesIO(data))
    with tarfile.open(str(args.output),'r:gz') as archive:
        for name,data in entries.items():
            if archive.extractfile(name).read()!=data:raise IOError('Archive mismatch: '+name)
    print(hashlib.sha256(args.output.read_bytes()).hexdigest()+'  '+args.output.name)
if __name__=='__main__':main()
