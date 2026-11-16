import json
import tempfile
import unittest
from pathlib import Path
from board_owner import BoardOwner, read
from mock_board import MockHardware, MockIO

class OwnerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.hw=MockHardware(self.root);self.hw.initialize()
        self.fw=self.root/'fixture.out';self.fw.write_bytes(b'fixture-not-firmware')
        self.profile={'board':'BBB-A','calibration':{'servo_low_us':1000,'servo_high_us':2000}}
        self.owner=self.new_owner()
    def tearDown(self):self.temp.cleanup()
    def new_owner(self):return BoardOwner(self.hw,self.root/'owner',self.fw,lambda ch,p:MockIO(ch))
    def assert_restored(self):
        self.assertEqual(read(self.hw.p('/sys/pru0/state')),'offline')
        self.assertEqual(read(self.hw.p('/sys/pru0/firmware')),'original.out')
        self.assertFalse((self.root/'owner').exists())
        self.assertFalse(list(self.hw.p('/sys/pwmchip4').glob('pwm*')))
        self.assertTrue(all(p.read_text()=='default' for p in self.hw.p('/pins').iterdir()))
    def test_lifecycle(self):
        self.owner.acquire(self.profile)
        self.assertEqual(read(self.hw.p('/pins/P8_11')),'gpio_pd')
        self.owner.activate_clock();self.owner.prepare(7)
        self.assertEqual(read(self.hw.p('/pins/P8_11')),'pruout')
        self.assertTrue(self.owner.release()['restored']);self.assert_restored()
        self.assertTrue(self.owner.release()['restored'])
    def test_second_instance_cannot_take_or_remove_owner(self):
        self.owner.acquire(self.profile)
        with self.assertRaises(FileExistsError):self.new_owner().acquire(self.profile)
        self.assertTrue((self.root/'owner').exists());self.owner.release();self.assert_restored()
    def test_foreign_pru(self):
        p=self.hw.p('/sys/pru1/state');p.write_text('running')
        with self.assertRaises(Exception):self.owner.acquire(self.profile)
        self.assertEqual(p.read_text(),'running');self.assertFalse(self.hw.log)
    def test_foreign_pwm(self):
        p=self.hw.p('/sys/pwmchip4/pwm1');p.mkdir()
        with self.assertRaises(Exception):self.owner.acquire(self.profile)
        self.assertTrue(p.exists());self.assertFalse(self.hw.log)
    def test_failure_after_mutation_rolls_back(self):
        self.hw.fail='state'
        with self.assertRaises(IOError):self.owner.acquire(self.profile)
        self.assert_restored()
    def test_pin_failure_rolls_back(self):
        self.hw.fail='P9_24'
        with self.assertRaises(IOError):self.owner.acquire(self.profile)
        self.assert_restored()
    def test_owner_changed_preserves_journal(self):
        self.owner.acquire(self.profile)
        self.hw.p('/sys/pru0/firmware').write_text('foreign.out')
        self.assertFalse(self.owner.release()['restored'])
        self.assertEqual(read(self.hw.p('/sys/pru0/firmware')),'foreign.out')
        self.assertTrue((self.root/'owner/resources.json').exists())
    def test_reboot_refuses_old_state(self):
        self.owner.acquire(self.profile);self.hw.p('/proc/sys/kernel/random/boot_id').write_text('new-boot')
        self.assertFalse(self.owner.release()['restored']);self.assertTrue((self.root/'owner').exists())
    def test_cleanup_failure_keeps_evidence(self):
        self.owner.acquire(self.profile);self.hw.fail='unexport'
        self.assertFalse(self.owner.release()['restored']);self.assertTrue((self.root/'owner/cleanup-errors.json').exists())
    def test_existing_lock_never_overwritten(self):
        p=self.root/'owner';p.mkdir();(p/'foreign').write_text('preserve')
        with self.assertRaises(FileExistsError):self.owner.acquire(self.profile)
        self.assertEqual((p/'foreign').read_text(),'preserve')
    def test_unexpected_journal_file_reports_cleanup_failure(self):
        self.owner.acquire(self.profile)
        (self.root/'owner/unexpected').write_text('preserve')
        result=self.owner.release()
        self.assertFalse(result['restored'])
        self.assertTrue((self.root/'owner/cleanup-errors.json').exists())
        self.assertEqual((self.root/'owner/unexpected').read_text(),'preserve')
if __name__=='__main__':unittest.main()
