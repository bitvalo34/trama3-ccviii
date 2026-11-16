"""Recover only an abandoned runtime journal, never kill a live owner."""
import json
import os
from pathlib import Path
from board_owner import LinuxHardware, Transaction, read
from p2 import LinuxBackend

def main():
    if os.geteuid()!=0:raise SystemExit('Root required')
    directory=Path('/run/trama3-runtime102')
    owner=json.loads((directory/'owner.json').read_text())
    if owner['boot_id']!=read('/proc/sys/kernel/random/boot_id'):raise SystemExit('Boot changed: preserve journal for review')
    try:os.kill(owner['pid'],0)
    except ProcessLookupError:pass
    else:raise SystemExit('Owner PID exists: use Ctrl+C in its terminal; no recovery performed')
    hw=LinuxHardware();hw.reserve()
    try:
        # Bus and output state are recorded before acquire; never guess a bus.
        profile=json.loads((directory/'profile.json').read_text())
        if profile.get('experiment')!='optical-acoustic':raise SystemExit('Use the original recovery procedure for full-media profiles')
        tx=Transaction(hw,directory/'resources.json');tx.data=json.loads(tx.path.read_text())
        io=LinuxBackend(profile['i2c_device'],None)
        try:
            if io.read_register(0x0a)!=0:raise SystemExit('Unknown MCP bank; remove actuator power and inspect')
            io.register(0x14,0)
            if io.read_register(0x14)!=0:raise SystemExit('MCP OFF not confirmed; remove actuator power')
            result=tx.cleanup()
            io.register(0x00,0xff)
            if io.read_register(0x00)!=0xff:raise SystemExit('MCP directions not restored')
        finally:io.close()
        print(json.dumps(result,indent=2))
        if not result['restored']:raise SystemExit('Preserve recovery journal; cleanup failed')
        for name in ('owner.json','profile.json','cleanup-errors.json'):
            p=directory/name
            if p.exists():p.unlink()
        directory.rmdir()
    finally:hw.unreserve()
if __name__=='__main__':main()
