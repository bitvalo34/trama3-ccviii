"""Package source and docs only, with SHA256SUMS. No downloads or build artifacts."""
import hashlib
import sys
import zipfile
from pathlib import Path

def package(target):
    root = Path(__file__).resolve().parents[2]
    runtime = root / 'software' / 'runtime102'
    allowed = ('.cjs', '.js', '.py', '.c', '.h', '.sh', '.md', '.json', '.html')
    files = [p for p in runtime.rglob('*') if p.is_file() and p.suffix in allowed
             and not any(s in ('build', 'dist', '__pycache__') for s in p.relative_to(runtime).parts)]
    files += [root / 'software/matrices102' / n for n in ('engine.js', 'core.js')]
    files += [p for p in (root / 'hardware/documentacion/fuentes-P2').iterdir() if p.is_file()]
    files += [root / p for p in ('hardware/pruebas/common.py', 'hardware/pruebas/t06/toolchain.py',
              'hardware/pruebas/t06/resources.py',
              'hardware/pruebas/t06/firmware/AM335x_PRU0.cmd',
              'docs/protocolo/TRAMA3_Protocolo_Revision_102.md',
              'docs/planificacion/entregables-runtime102.md',
              'docs/planificacion/Informe_Runtime102_Base.md')]
    entries = [(p.relative_to(root).as_posix(), p.read_bytes()) for p in sorted(files)]
    manifest = ''.join(hashlib.sha256(data).hexdigest() + '  ' + name + '\n' for name, data in entries)
    with zipfile.ZipFile(str(target), 'x', zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries + [('SHA256SUMS', manifest.encode('utf-8'))]:
            info = zipfile.ZipInfo(name, (2026, 11, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    with zipfile.ZipFile(str(target)) as archive:
        for name, data in entries:
            if archive.read(name) != data: raise IOError('Archive mismatch: ' + name)
    return hashlib.sha256(Path(target).read_bytes()).hexdigest()
if __name__ == '__main__':
    if len(sys.argv) != 2: raise SystemExit('Usage: python package-runtime.py NEW_ZIP_PATH')
    print(package(sys.argv[1]) + '  ' + sys.argv[1])
