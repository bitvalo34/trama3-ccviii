import importlib.util
import sys
import unittest
import io
from pathlib import Path
# fcntl is Linux-only; tests exercise injected IO and never create LinuxBackend.
if sys.platform=='win32':
    import types
    sys.modules['fcntl']=types.ModuleType('fcntl')
spec=importlib.util.spec_from_file_location('p2',str(Path(__file__).with_name('p2.py')))
p2=importlib.util.module_from_spec(spec);spec.loader.exec_module(p2)
class IO:
    def __init__(self):self.log=[];self.fail=False
    def register(self,*args):
        if self.fail and args==(0x14,3):raise IOError('I2C failed')
        self.log.append(('reg',)+args)
    def pwm_write(self,*args):self.log.append(('pwm',)+args)
class TestOutputs(unittest.TestCase):
    def test_worker_reports_shutdown_failure(self):
        sys.path.insert(0,str(Path(__file__).parent))
        spec=importlib.util.spec_from_file_location('worker',str(Path(__file__).with_name('p2-worker.py')))
        worker=importlib.util.module_from_spec(spec);spec.loader.exec_module(worker)
        class Broken(IO):
            def pwm_write(self,*args):raise IOError('disable failed')
        output=io.StringIO()
        with self.assertRaises(IOError):
            worker.serve(p2.Outputs(Broken(),1000,2000),io.StringIO('{"id":1,"op":"shutdown"}\n'),output)
        self.assertIn('"ok": false',output.getvalue())
    def test_order_and_mapping(self):
        io=IO();o=p2.Outputs(io,1000,2000);o.initialize()
        self.assertEqual(io.log[:2],[('reg',0x14,0),('reg',0,0xfc)])
        o.prepare(7);self.assertEqual(io.log[-3:],[('reg',0x14,3),('pwm','duty_cycle',2000000),('pwm','enable',1)])
    def test_fault_latches_and_disables(self):
        io=IO();o=p2.Outputs(io,1000,2000);o.initialize();io.fail=True
        with self.assertRaises(IOError):o.prepare(3)
        self.assertTrue(o.fault);self.assertFalse(o.ready)
        self.assertEqual(io.log[-1],('pwm','enable',0))
        with self.assertRaises(RuntimeError):o.prepare(0)
    def test_no_uncalibrated_endpoints(self):
        for a,b in [(0,2000),(1000,2100),(1500,1500)]:
            with self.assertRaises(ValueError):p2.Outputs(IO(),a,b)
if __name__=='__main__':unittest.main()
