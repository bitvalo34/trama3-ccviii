"""Check bundled P2 snapshot against PR 7. Read-only, no hardware validation."""
import hashlib
import json
from pathlib import Path

EXPECTED = {
    'sustituciones-locales.md': '86d28ccdea8334689bbecd355e4e9f2d768798896941986faec8e629396a0243',
    'arneses-externos.csv': '88ceb4e44b5d927a8dfc9e6a3584c58b6339e144864efd9c1d44f4a5c75890a0',
    'diseno-electrico.md': '9afebb4206b467a755fff03f97f83bfa7c7117e3a26647c67f7b7f8d153c070a',
    'BOM-ensamble.csv': 'ffd913175dbf67dc1719f43390e7bd054bd7a7a349ed455e1dfe45484757922b',
    'diseno.json': '2ba7a705dc2285efd07a5b686844e1f41aad57f27415824777854a78cab281b4'
}
if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2] / 'hardware/documentacion/fuentes-P2'
    checks = {}
    for name, expected in EXPECTED.items():
        try: checks[name] = hashlib.sha256((root / name).read_bytes()).hexdigest() == expected
        except OSError: checks[name] = False
    passed = all(checks.values())
    print(json.dumps({'status': 'PASS' if passed else 'FAIL', 'checks': checks,
          'physical_status': 'NOT_TESTED', 'origin': 'source_hash_verification',
          'source': 'https://github.com/bitvalo34/trama3-ccviii/pull/7',
          'commit': '9ba0bcaa271740effe206ec1ef79b72c070168e6'}, indent=2))
    raise SystemExit(0 if passed else 1)
