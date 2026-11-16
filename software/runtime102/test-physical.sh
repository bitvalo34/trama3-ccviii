#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")/../.."
if [[ $(node -p 'process.versions.node.split(".")[0]') == 16 ]]; then
  # Only the pre-existing web regression tests need fetch; PHY uses no network.
  export NODE_OPTIONS="${NODE_OPTIONS:-} --experimental-fetch"
fi
node software/matrices102/test.cjs
for test in software/runtime102/test*.cjs; do
  echo "TEST $test"
  node "$test"
done
node software/runtime102/fault-suite.cjs "$(mktemp -d)/faults"
python3 -m unittest discover -s software/runtime102 -p 'test_*.py'
mkdir -p software/runtime102/native/build
gcc -std=c99 -O2 -Wall -Wextra -Werror software/runtime102/native/host.c -o software/runtime102/native/build/runtime102-host
gcc -std=c99 -O2 -Wall -Wextra -Werror software/runtime102/native/service.c software/runtime102/native/test_service.c -o software/runtime102/native/build/test-service
software/runtime102/native/build/test-service
