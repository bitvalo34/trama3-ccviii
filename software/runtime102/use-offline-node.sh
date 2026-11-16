#!/bin/bash
# Run from the extracted source root. No system installation, no network.
set -euo pipefail
cd -- "$(dirname -- "$0")/../.."
archive=${1:-offline/node-v16.20.2-linux-armv7l.tar.xz}
[[ $(uname -m) == armv7l ]] || { echo 'This Node archive is ARMv7 only'; exit 2; }
python3 - "$archive" <<'PY'
import hashlib,sys
from pathlib import Path
p=Path(sys.argv[1]);expected={x.split()[1]:x.split()[0] for x in (p.parent/'NODE_SHASUMS256.txt').read_text().splitlines()}
if hashlib.sha256(p.read_bytes()).hexdigest()!=expected[p.name]:raise SystemExit('Node archive hash mismatch')
PY
mkdir -p tools/node16
tar -xJf "$archive" --strip-components=1 -C tools/node16 node-v16.20.2-linux-armv7l/bin/node
tools/node16/bin/node --version
tools/node16/bin/node -e "require('node:crypto').randomInt(1,100); new TextDecoder(); console.log('Node APIs ready; hardware NOT_TESTED')"
echo 'Run: export PATH="$PWD/tools/node16/bin:$PATH"'
