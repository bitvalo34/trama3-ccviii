"""Internal JSONL worker. Mock by default; Linux owner must supply calibrated IO."""
import json
import sys
from p2 import Outputs

class MockIO:
    def register(self, reg, value): pass
    def pwm_write(self, name, value): pass

def serve(outputs, source, sink):
    try:
        for line in source:
            if len(line) > 4096: raise ValueError('Command too large')
            request = json.loads(line)
            ident = request['id']
            try:
                op = request['op']
                if op == 'initialize': outputs.initialize()
                elif op == 'prepare': outputs.prepare(request['vector'])
                elif op == 'shutdown':
                    errors = outputs.shutdown()
                    if errors: raise IOError('; '.join(errors))
                else: raise ValueError('Unknown operation')
                reply = {'id': ident, 'ok': True}
            except Exception as exc:
                reply = {'id': ident, 'ok': False, 'error': str(exc)}
            sink.write(json.dumps(reply) + '\n'); sink.flush()
            if request.get('op') == 'shutdown': break
    finally:
        errors = outputs.shutdown()
        if errors: raise IOError('; '.join(errors))

if __name__ == '__main__':
    if sys.argv[1:] != ['--mock']:
        raise SystemExit('Only --mock CLI enabled; hardware requires resource owner')
    serve(Outputs(MockIO(), 1000, 2000), sys.stdin, sys.stdout)
