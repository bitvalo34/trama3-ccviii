import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('preflight',str(Path(__file__).with_name('preflight-runtime.py')))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class InventoryTests(unittest.TestCase):
    def test_read_only_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            files={'proc/device-tree/model':'TI AM335x BeagleBone Black\x00',
                'sys/class/remoteproc/remoteproc1/name':'pru0',
                'sys/class/remoteproc/remoteproc1/state':'offline',
                'sys/class/pwm/pwmchip4/pwm0/enable':'0',
                'sys/class/pwm/pwmchip4/pwm0/period':'0',
                'sys/class/pwm/pwmchip4/pwm0/duty_cycle':'0',
                'dev/i2c-2':'', 'run/trama3-t06/state.json':'{}'}
            for name,value in files.items():
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value)
            before={str(p):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            result=module.resources(root)
            self.assertEqual(result['model'],'TI AM335x BeagleBone Black')
            self.assertEqual(result['remoteproc'][0]['state'],'offline')
            self.assertTrue(result['t06_journal_present'])
            self.assertEqual(result['pwm'][0]['channels'][0]['enable'],'0')
            self.assertEqual(before,{str(p):p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_missing_resources(self):
        with tempfile.TemporaryDirectory() as directory:
            result=module.resources(Path(directory))
            self.assertEqual(result['remoteproc'],[])
            self.assertIsNone(result['model'])

if __name__=='__main__':unittest.main()
