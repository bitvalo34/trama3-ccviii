"""Produce a new measured profile from three completed offline diagnostics."""
import argparse
import hashlib
import json
from pathlib import Path
from lab_profile import validate_lab

def main():
    ap=argparse.ArgumentParser()
    for k in ('profile','optical','clock','acoustic','output'):ap.add_argument('--'+k,type=Path,required=True)
    a=ap.parse_args();p=json.loads(a.profile.read_text());validate_lab(p)
    refs={}
    for key,kind in (('optical','c0'),('clock','clock'),('acoustic','c1')):
        path=getattr(a,key);report=json.loads(path.read_text())
        if report.get('status')!='PASS' or report.get('rx_node')!=p['board'][-1] or report.get('trial')!=kind:
            raise SystemExit('Independent PASS report for this receiver required: '+key)
        config=report.get('rx_configuration',{})
        if config.get('rx_invert')!=p['rx_invert'] or config.get('i2c_device')!=p['i2c_device'] or any(
            config.get('acoustic',{}).get(k)!=p['acoustic'][k] for k in ('start','end','max_gap')):
            raise SystemExit('Report/profile polarity, bus or acoustic window changed: '+key)
        refs[key]=str(path)+' sha256:'+hashlib.sha256(path.read_bytes()).hexdigest()
        if key=='acoustic':
            threshold=report.get('calibration',{}).get('suggested_min_active')
            if type(threshold) is not int or threshold<=0:raise SystemExit('No measured acoustic separation')
            p['acoustic']['min_active']=threshold
            p['acoustic']['evidence']=refs[key]
    p['calibration']['clock_evidence']=refs['clock']
    p['calibration']['optical_evidence']=refs['optical']
    p['calibration']['status']='MEASURED'
    validate_lab(p,frames=True)
    with a.output.open('x') as f:json.dump(p,f,indent=2);f.write('\n')
    print('New measured profile: '+str(a.output)+'; original preserved. C2 remains unavailable.')
if __name__=='__main__':main()
