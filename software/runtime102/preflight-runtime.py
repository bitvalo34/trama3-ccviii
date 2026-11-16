"""Read-only inventory; works with Python 3.5+. Never installs or enables IO."""
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

def command(args):
    if not shutil.which(args[0]): return {'available': False}
    try:
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate(timeout=5)
        return {'available': True, 'exit_code': p.returncode,
                'stdout': out.decode('utf-8', 'replace').strip(),
                'stderr': err.decode('utf-8', 'replace').strip()}
    except subprocess.TimeoutExpired:
        p.kill(); p.communicate()
        return {'available': True, 'error': 'timeout'}

def inventory():
    tools = {name: command(args) for name, args in [
        ('node', ['node', '--version']), ('gcc', ['gcc', '-dumpversion']),
        ('clpru', ['clpru', '--compiler_revision'])]}
    version = tools['node'].get('stdout', '')
    try: node_ok = int(version.lstrip('v').split('.')[0]) >= 18
    except ValueError: node_ok = False
    return {'origin': 'system_report', 'physical_status': 'NOT_TESTED',
            'status': 'READY_FOR_PC_TESTS' if node_ok else 'BLOCKED',
            'hardware_status': 'NOT_AUTHORIZED_BY_THIS_CHECK',
            'python': sys.version.split()[0], 'os': platform.platform(),
            'machine': platform.machine(), 'tools': tools,
            'shared_abi_required': 3,
            'dev_mem_present': Path('/dev/mem').exists(),
            'note': 'Node version alone does not validate Debian ARM compatibility or P2 calibration.'}
if __name__ == '__main__': print(json.dumps(inventory(), indent=2))
