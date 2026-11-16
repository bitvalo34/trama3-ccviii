"""Regresiones P2, identidad de recursos y contrato continuo (datos sinteticos)."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import test_hardware as fixtures
from test_hardware import complete_measurements
from mediciones import evaluate,template,ALL_POINTS,CONTACTS
from common import Blocked
from confirmation import validate_confirmation
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"hardware/pruebas/interfaces"))
from stream102 import TickExtender,CaptureRing,HZ,WRAP

class P2Tests(unittest.TestCase):
    def rows(self):return complete_measurements()
    def test_p1_rejected(self):
        r=self.rows();r[0]["hardware_revision"]="P1"
        with self.assertRaises(ValueError):evaluate(r,"BBB-A")
    def test_retired_points(self):
        for point in ("J11","J12","MOD3","IRLML6402"):
            r=self.rows();r[0]["point"]=point
            with self.assertRaises(ValueError):evaluate(r,"BBB-A")
    def test_missing_p2_points(self):
        for point in ("q6_verificado","sw287_CENTRO","neg_in_sin_bypass"):
            self.assertNotEqual(evaluate([r for r in self.rows() if r["point"]!=point],"BBB-A")["status"],"PASS")
    def test_wrong_q6_topology(self):
        r=self.rows();x=next(x for x in r if x["point"]=="q6_verificado")
        d=json.loads(x["detail"]);d["nets"]["D"]="GND_ACT";x["detail"]=json.dumps(d)
        self.assertEqual(evaluate(r,"BBB-A")["status"],"BLOCKED")
    def test_center_is_not_off(self):
        r=self.rows();x=next(x for x in r if x["point"]=="sw287_CENTRO")
        d=json.loads(x["detail"]);d["closed"]=CONTACTS["sw287_OFF"];x["detail"]=json.dumps(d)
        self.assertEqual(evaluate(r,"BBB-A")["status"],"BLOCKED")
    def test_neg_in_bypass_fails(self):
        r=self.rows();next(x for x in r if x["point"]=="neg_in_sin_bypass")["value"]="no"
        self.assertEqual(evaluate(r,"BBB-A")["status"],"FAIL")
    def test_metadata_and_origin(self):
        for field,value in (("operator",""),("instrument",""),("evidence",""),("origin","simulated"),("measured_at","bad")):
            r=self.rows();r[0][field]=value
            self.assertEqual(evaluate(r,"BBB-A")["status"],"BLOCKED")
    def test_gpio_missing(self):
        r=[x for x in self.rows() if x["point"]!="P8_15_PEAK"]
        self.assertEqual(evaluate(r,"BBB-A")["status"],"NOT_TESTED")
    def test_full_frame_across_wraps(self):
        clock=TickExtender();clock.advance(0,0)
        for sec in range(1,90):self.assertEqual(clock.advance(sec*HZ%WRAP,1000000000),sec*HZ)
    def test_ambiguous_timestamp(self):
        with self.assertRaises(ValueError):TickExtender().advance(0,22000000000)
    def test_ring_overflow_stops_without_overwrite(self):
        ring=CaptureRing(3)
        for i in range(3):self.assertTrue(ring.push(i,0))
        self.assertFalse(ring.push(4,0));self.assertTrue(ring.overflow)
        self.assertEqual([x["sequence"] for x in ring.consume()],[0,1,2])
        with self.assertRaises(ValueError):ring.push(5,0)
    def test_vector_and_polarity(self):
        ring=CaptureRing();ring.push(1,(1<<5)|(1<<16),invert_mask=5)
        x=ring.consume()[0];self.assertEqual(x["raw_vector"],5);self.assertEqual(x["vector"],0)

class OwnershipTests(unittest.TestCase):
    setUp=fixtures.Tests.setUp
    tearDown=fixtures.Tests.tearDown
    file=fixtures.Tests.file
    # Reuse filesystem fixture; inherited regressions deliberately not duplicated by discovery below.
    def test_ptp_unknown_blocks(self):
        fixtures.Tests.test_remote_renumbered(self)
        self.file("sys/class/ptp/ptp0/clock_name","unknown")
        with self.assertRaises(Blocked):self.hw.offline()
    def test_cpts_identity(self):
        fixtures.Tests.test_remote_renumbered(self)
        self.file("sys/class/ptp/ptp0/clock_name","CTPS timer")
        real=Path.resolve
        def resolve(p):
            if p.as_posix().endswith("ptp0/device"):return Path("/sys/devices/platform/ocp/4a100000.ethernet")
            if p.as_posix().endswith("4a100000.ethernet/driver"):return Path("/sys/bus/platform/drivers/cpsw")
            return real(p)
        # Linux 4.14 spelling CTPS timer is accepted explicitly along with CPTS.
        with patch.object(Path,"resolve",resolve):self.hw.offline()

if __name__=="__main__":unittest.main()

class AcceptanceP2Tests(unittest.TestCase):
    def test_three_widths_build_and_both_boards(self):
        import tempfile
        from evaluar import evaluate as acceptance
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            manifest={"BBB-A":{}}
            hashes={"firmware":"a"*64}
            binaries={"host":"b"*64,"pru":"c"*64}
            identity={"model":"TI AM335x BeagleBone Black","kernel":"test"}
            def record(key,test,**extra):
                r=dict(schema=2,hardware_revision="BBB-BARE",board="BBB-A",test=test,
                       status="PASS",origin="hardware",identity=identity,source_hashes=hashes,
                       binary_hashes=binaries,active=True,electrical_confirmation=True,operator="fixture",
                       confirmation={"sha256":"d"*64,"operator":"fixture","evidence":"test"},
                       resources={"restored":True})
                r.update(extra)
                path=root/(key+".json");path.write_text(json.dumps(r))
                manifest["BBB-A"][key]=path.name
            record("build","build",origin="software_build",command={"exit_code":0})
            record("pru-smoke","pru-smoke",probe={"ready":True})
            record("loopback","loopback",raw=fixtures.pulse_raw(),parameters={"period_us":20000,"high_us":1500,"cycles":25})
            for width in (1000,1500,2000):
                raw=fixtures.pulse_raw()
                for i in range(1,len(raw["events"]),2):raw["events"][i][0]=raw["events"][i-1][0]+width*200
                record("pwm-capture-"+str(width),"pwm-capture",raw=raw,
                       parameters={"period_us":20000,"high_us":width,"cycles":25},pwm={"frequency_checked":True})
            result=acceptance(manifest,root)
            self.assertEqual(result["boards"]["BBB-A"]["T06"],"PASS")
            self.assertEqual(result["T06"]["status"],"NOT_TESTED")
            manifest["BBB-A"].pop("pwm-capture-2000")
            self.assertEqual(acceptance(manifest,root)["boards"]["BBB-A"]["T06"],"NOT_TESTED")
            r=json.loads((root/"loopback.json").read_text());r["binary_hashes"]["host"]="e"*64
            (root/"loopback.json").write_text(json.dumps(r))
            self.assertEqual(acceptance(manifest,root)["boards"]["BBB-A"]["T06"],"BLOCKED")
    def test_confirmation_requires_measurement(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"check.json"
            c=dict(schema=1,board="BBB-B",hardware_revision="BBB-BARE",level=1,fixture="none",
                   operator="fixture",checked_at="2026-11-15",evidence="test",instrument="test",
                   interface_disconnected=True,actuators_disconnected=True,wiring_done_unpowered=True,
                   pins_identified=True,supply_checked=True,p9_3_V=3.3,uncertainty_V=.01)
            p.write_text(json.dumps(c))
            self.assertTrue(validate_confirmation(str(p),"BBB-B","none","fixture")["sha256"])
            c["p9_3_V"]=5;p.write_text(json.dumps(c))
            with self.assertRaises(Blocked):validate_confirmation(str(p),"BBB-B","none","fixture")
