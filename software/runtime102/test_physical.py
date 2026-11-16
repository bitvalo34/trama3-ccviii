import copy
import unittest
from pathlib import Path
import json
import subprocess
import sys
import tempfile
from p2 import Outputs
from lab_profile import validate_lab
import test_board_owner

class IO:
    def __init__(self): self.reg={0:255,10:0,20:0};self.writes=[];self.fail=False
    def read_register(self,r):return self.reg[r]
    def register(self,r,v):
        if self.fail and v:raise IOError('I2C failed')
        self.reg[r]=v;self.writes.append((r,v))
    def pwm_write(self,*args):raise AssertionError('servo accessed')
    def close(self):pass

def profile():
    p=json.loads((Path(__file__).parent/'profiles/BBB-A-optical-acoustic.json').read_text())
    p['mcp_reset_confirmed']=True
    c=p['calibration'];c.update(status='COMMISSIONING',evidence='TEST ONLY',checked_at='TEST',rx_invert=8,i2c_device='/dev/i2c-2',i2c_adapter_evidence='TEST')
    c['checks']={k:True for k in c['checks']}
    return p

class PhysicalOutputs(unittest.TestCase):
    def test_mcp_readback_and_no_pwm(self):
        io=IO();o=Outputs(io,optical_acoustic=True);o.initialize()
        for v in range(8):o.prepare(v);self.assertEqual(io.reg[20],v&3)
        self.assertEqual(o.shutdown(),[]);self.assertEqual(io.reg[20],0)
    def test_reset_during_frame_stops(self):
        io=IO();o=Outputs(io,optical_acoustic=True);o.initialize();io.reg[0]=255
        with self.assertRaisesRegex(IOError,'IODIRA'):o.prepare(3)
        self.assertFalse(o.ready);self.assertTrue(o.fault);self.assertEqual(io.reg[20],0)
    def test_write_failure_stops_without_ready(self):
        io=IO();o=Outputs(io,optical_acoustic=True);o.initialize();io.fail=True
        with self.assertRaises(IOError):o.prepare(1)
        self.assertFalse(o.ready);self.assertEqual(io.reg[20],0)
    def test_ignored_write_cannot_be_ready(self):
        class Ignored(IO):
            def register(self,r,v):pass
        o=Outputs(Ignored(),optical_acoustic=True)
        with self.assertRaisesRegex(IOError,'READBACK'):o.initialize()
        self.assertFalse(o.ready)
    def test_profiles_no_invented_calibration(self):
        p=profile();validate_lab(p)
        with self.assertRaisesRegex(ValueError,'FRAME_CALIBRATION'):validate_lab(p,frames=True)
        p['calibration'].update(status='MEASURED',clock_evidence='TEST');p['acoustic'].update(min_active=10,evidence='TEST')
        validate_lab(p,frames=True)
        for k in p['calibration']['checks']:
            q=copy.deepcopy(p);q['calibration']['checks'][k]=False
            with self.assertRaises(ValueError):validate_lab(q)

class LabOwner(unittest.TestCase):
    def test_lab_never_exports_pwm_or_changes_c2(self):
        base=test_board_owner.OwnerTests();base.setUp()
        try:
            base.owner.output_factory=lambda ch,p:IO()
            base.owner.acquire(profile());base.owner.activate_clock();base.owner.prepare(7)
            self.assertEqual((base.root/'pins/P9_14').read_text(),'default')
            self.assertEqual((base.root/'pins/P9_24').read_text(),'default')
            self.assertFalse(list((base.root/'sys/pwmchip4').glob('pwm*')))
            self.assertTrue(base.owner.release()['restored']);base.assert_restored()
        finally:base.tearDown()

class Calibration(unittest.TestCase):
    def test_reports_match_receiver_and_window_and_preserve_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=profile();source=root/'profile.json';source.write_text(json.dumps(p))
            reports=[]
            for kind in ('c0','clock','c1'):
                target=root/(kind+'.json');target.write_text(json.dumps({'status':'PASS','rx_node':'A','trial':kind,
                    'rx_configuration':{'rx_invert':8,'i2c_device':p['i2c_device'],'acoustic':p['acoustic']},
                    'calibration':{'suggested_min_active':30000000}}));reports.append(target)
            output=root/'measured.json'
            command=[sys.executable,str(Path(__file__).with_name('calibrate-physical.py')),'--profile',str(source),
                '--optical',str(reports[0]),'--clock',str(reports[1]),'--acoustic',str(reports[2]),'--output',str(output)]
            self.assertEqual(subprocess.call(command,stdout=subprocess.DEVNULL),0)
            measured=json.loads(output.read_text());validate_lab(measured,frames=True)
            self.assertEqual(json.loads(source.read_text())['calibration']['status'],'COMMISSIONING')
            self.assertEqual(measured['acoustic']['min_active'],30000000)
            bad=json.loads(reports[2].read_text());bad['rx_configuration']['acoustic']['start']=0;reports[2].write_text(json.dumps(bad))
            command[-1]=str(root/'bad.json')
            self.assertNotEqual(subprocess.call(command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL),0)
            self.assertFalse((root/'bad.json').exists())

if __name__=='__main__':unittest.main()
