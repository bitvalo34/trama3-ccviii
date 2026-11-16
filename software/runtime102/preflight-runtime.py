"""Read-only inventory; works with Python 3.5+. Never installs or enables IO."""
import json
import argparse
import datetime
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
    except OSError as error:
        return {'available': True, 'error': str(error)}

def read_text(path):
    try: return path.read_text().strip().strip('\x00')
    except OSError: return None

def resources(root=Path('/')):
    def p(name): return root / name.lstrip('/')
    remote=[]
    for entry in sorted(p('/sys/class/remoteproc').glob('remoteproc*')):
        remote.append({'path':str(entry),'name':read_text(entry/'name'),
                       'state':read_text(entry/'state'),'firmware':read_text(entry/'firmware')})
    pwm=[]
    for entry in sorted(p('/sys/class/pwm').glob('pwmchip*')):
        channels=[]
        for channel in sorted(entry.glob('pwm*')):
            if channel.is_dir():
                channels.append({'name':channel.name,'enable':read_text(channel/'enable'),
                    'period':read_text(channel/'period'),'duty_cycle':read_text(channel/'duty_cycle')})
        pwm.append({'path':str(entry),'device':str((entry/'device').resolve()),'channels':channels})
    return {'model':read_text(p('/proc/device-tree/model')),'remoteproc':remote,'pwm':pwm,
            'i2c_devices':[str(x) for x in sorted(p('/dev').glob('i2c-*'))],
            'runtime_journal_present':p('/run/trama3-runtime102').exists(),
            't06_journal_present':p('/run/trama3-t06/state.json').exists()}

def inventory():
    tools = {name: command(args) for name, args in [
        ('node', ['node', '--version']), ('gcc', ['gcc', '-dumpversion']),
        ('clpru', ['clpru', '--compiler_revision'])]}
    version = tools['node'].get('stdout', '')
    try: node_ok = int(version.lstrip('v').split('.')[0]) >= 16
    except ValueError: node_ok = False
    return {'origin': 'system_report', 'physical_status': 'NOT_TESTED',
            'status': 'READY_FOR_PC_TESTS' if node_ok else 'BLOCKED',
            'hardware_status': 'NOT_AUTHORIZED_BY_THIS_CHECK',
            'python': sys.version.split()[0], 'os': platform.platform(),
            'machine': platform.machine(), 'tools': tools,
            'shared_abi_required': 4,
            'dev_mem_present': Path('/dev/mem').exists(),
            'resources': resources() if sys.platform=='linux' else None,
            'note': 'Node version alone does not validate Debian ARM compatibility or P2 calibration.'}
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', choices=('BBB-A','BBB-B'))
    parser.add_argument('--output', type=Path)
    args=parser.parse_args()
    result=inventory();result['board_declared']=args.board
    result['utc_system_unverified']=datetime.datetime.utcnow().isoformat()+'Z'
    text=json.dumps(result,indent=2)
    if args.output:
        with args.output.open('x',encoding='utf-8') as f:f.write(text+'\n')
    print(text)
