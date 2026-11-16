"""Internal resource owner RPC. Mock CLI for PC; hardware requires explicit flags."""
import argparse
import json
import sys
from pathlib import Path
from board_owner import linux_owner, BoardOwner

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--profile',required=True);parser.add_argument('--firmware',required=True)
    parser.add_argument('--mock-root');parser.add_argument('--active',action='store_true')
    args=parser.parse_args();profile=json.loads(Path(args.profile).read_text())
    if args.mock_root:
        if args.active:raise ValueError('Conflicting modes')
        from mock_board import MockHardware, MockIO
        root=Path(args.mock_root)
        # The caller creates a new sandbox; never reinitialize an existing owner.
        if not root.exists():root.mkdir();hw=MockHardware(root);hw.initialize()
        else:hw=MockHardware(root)
        owner=BoardOwner(hw,root/'owner',args.firmware,lambda ch,p:MockIO(ch))
        profile=dict(profile);profile['calibration']={'servo_low_us':1000,'servo_high_us':2000}
    elif args.active:
        c=profile.get('calibration',{})
        if c.get('status')!='MEASURED' or c.get('board')!=profile.get('board') or not c.get('evidence'):
            raise ValueError('CALIBRATION_REQUIRED')
        owner=linux_owner(profile,args.firmware)
    else:raise ValueError('Specify --mock-root or --active')
    try:
        for line in sys.stdin:
            if len(line)>4096:raise ValueError('Command too large')
            r=json.loads(line);op=r['op']
            try:
                data=None
                if op=='acquire':data=owner.acquire(profile)
                elif op=='activate':owner.activate_clock()
                elif op=='prepare':owner.prepare(r['vector'])
                elif op=='shutdown':owner.shutdown_outputs()
                elif op=='release':
                    data=owner.release()
                    if not data['restored']:raise IOError('; '.join(data['errors']))
                else:raise ValueError('Unknown operation')
                reply={'id':r['id'],'ok':True,'data':data}
            except Exception as exc:reply={'id':r['id'],'ok':False,'error':str(exc)}
            sys.stdout.write(json.dumps(reply)+'\n');sys.stdout.flush()
            if op=='release':break
    finally:
        result=owner.release()
        if not result['restored']:raise RuntimeError('; '.join(result['errors']))
if __name__=='__main__':main()
