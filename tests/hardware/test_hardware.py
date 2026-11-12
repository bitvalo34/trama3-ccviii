"""Pruebas sin hardware: fallos, restauracion, archivos y aceptacion."""
import contextlib
import copy
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(BASE/"hardware/pruebas"),str(BASE/"hardware/pruebas/t06"),str(BASE/"hardware/pruebas/t08")]
from common import Blocked,atomic_json,safe_text,execute
from resources import Hardware,Transaction
from analyze import analyze
from mediciones import template,evaluate,write_csv,read_csv,NUMERIC
from evaluar import evaluate as acceptance
from run import options

class FakeHardware(Hardware):
    def __init__(self,root):
        super().__init__(root)
        self.fail=None
    def write(self,path,value):
        if self.fail and self.fail in str(path):raise OSError("fallo inyectado")
        path=Path(path)
        if path.name=="export":
            c=path.parent/"pwm0";c.mkdir()
            for k,v in (("enable","0"),("duty_cycle","0"),("period","0"),("polarity","normal")):
                (c/k).write_text(v)
        elif path.name=="unexport":
            import shutil;shutil.rmtree(str(path.parent/"pwm0"))
        else:
            path.write_text({"start":"running","stop":"offline"}.get(str(value),str(value)))
        self.log.append((str(path),str(value)))
    def pin_set(self,rec,mode):
        if self.fail==rec["pin"]:raise OSError("pinmux fallo")
        Path(rec["path"]).write_text(mode)
    def command(self,args):
        return "default gpio_input gpio_pd gpio_pu pruout pruin pwm"
    def wait_path(self,path,exists=True):
        if Path(path).exists()!=exists:raise Blocked("estado de ruta")

def pulse_raw(n=25):
    e=[]
    for i in range(n):
        e.extend([[(i+1)*4000000,1<<15],[(i+1)*4000000+300000,0]])
    return dict(state=3,initial=0,generated=n,overflow=0,late=0,max_gap_ticks=200,events=e)

def complete_measurements():
    rows=template("BBB-A")
    for r in rows:
        p=r["point"]
        r.update(instrument="SIMULADO",measured_at="2026-11-12T00:00:00Z",evidence="fixture")
        if p in NUMERIC:
            lo,hi,_,_=NUMERIC[p]
            r["value"]=str((lo+hi)/2)
            r["uncertainty"]="0.001"
        else:r["value"]="yes"
    return rows

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name);self.hw=FakeHardware(self.root)
    def tearDown(self):self.tmp.cleanup()
    def file(self,p,value):
        q=self.root/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(value);return q
    def test_default_audit(self):
        a=options(["--board","BBB-A"]);self.assertFalse(a.active);self.assertEqual(a.action,"preflight")
    def test_invalid_arguments(self):
        for extra in (["--high-us","0"],["--seconds","nan"],["--cycles","999"],["--period-us","2"]):
            with self.subTest(extra=extra),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
                options(["--board","BBB-B"]+extra)
    def test_pwm_limits(self):
        with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
            options(["pwm","--board","BBB-A","--high-us","2500"])
    def test_clean_pulses(self):
        r=analyze(pulse_raw(),20000,1500,"loopback",25)
        self.assertEqual(r["status"],"PASS");self.assertEqual(r["frequency_hz"],50)
    def test_missing_pulses(self):
        r=pulse_raw();r["events"]=[]
        self.assertEqual(analyze(r,20000,1500,"loopback",25)["status"],"FAIL")
    def test_wrong_high(self):
        self.assertEqual(analyze(pulse_raw(),20000,1000,"loopback",25)["status"],"FAIL")
    def test_extra_pulses(self):
        self.assertEqual(analyze(pulse_raw(26),20000,1500,"loopback",25)["status"],"FAIL")
    def test_overflow_late_and_timeout(self):
        for key,value in (("overflow",1),("late",1),("state",4),("max_gap_ticks",3000)):
            r=pulse_raw();r[key]=value
            with self.subTest(key=key):self.assertEqual(analyze(r,20000,1500,"loopback",25)["status"],"FAIL")
    def test_partial_first_pulse(self):
        r=pulse_raw();r["initial"]=1<<15;r["events"]=r["events"][1:]
        self.assertEqual(analyze(r,20000,1500,"pwm-capture",25)["status"],"PASS")
    def test_single_snapshot_all_bits(self):
        r=pulse_raw();r["events"][0][1]|=(1<<5)|(1<<14)|(1<<16)
        s=analyze(r,20000,1500,"inputs",25)["snapshots"][0]
        self.assertEqual((s["clock"],s["C0"],s["C1"],s["C2"]),(1,1,1,1))
    def test_timestamp_reversal(self):
        r=pulse_raw();r["events"][2][0]=1
        self.assertEqual(analyze(r,20000,1500,"loopback",25)["status"],"FAIL")
    def test_no_data_not_zero(self):
        self.assertEqual(evaluate(template("BBB-A"),"BBB-A")["status"],"NOT_TESTED")
    def test_simulation_never_physical_pass(self):
        self.assertEqual(evaluate(complete_measurements(),"BBB-A","simulated")["status"],"NOT_TESTED")
    def test_complete_form_logic(self):
        self.assertEqual(evaluate(complete_measurements(),"BBB-A")["status"],"PASS")
    def test_nan_inf_blank_uncertainty(self):
        for value in ("nan","inf","-inf","oops"):
            rows=complete_measurements()
            next(r for r in rows if r["point"]=="P9_3")["value"]=value
            self.assertEqual(evaluate(rows,"BBB-A")["status"],"BLOCKED")
    def test_overvoltage_stops(self):
        rows=complete_measurements()
        next(r for r in rows if r["point"]=="P8_15_PEAK")["value"]="5"
        self.assertEqual(evaluate(rows,"BBB-A")["status"],"FAIL")
    def test_uncertainty_boundary(self):
        rows=complete_measurements()
        next(r for r in rows if r["point"]=="P9_3").update(value="3.14",uncertainty=".02")
        self.assertEqual(evaluate(rows,"BBB-A")["status"],"FAIL")
    def test_false_check_stops(self):
        rows=complete_measurements();rows[0]["value"]="no"
        self.assertEqual(evaluate(rows,"BBB-A")["status"],"FAIL")
    def test_wrong_board_and_duplicates(self):
        for rows in (template("BBB-B"),template("BBB-A")*2):
            with self.assertRaises(ValueError):evaluate(rows,"BBB-A")
    def test_csv_roundtrip(self):
        p=self.root/"medidas.csv";r=template("BBB-A");write_csv(p,r)
        self.assertEqual(read_csv(p),r)
    def test_unknown_point(self):
        r=template("BBB-A");r[0]["point"]="P9_99"
        with self.assertRaises(ValueError):evaluate(r,"BBB-A")
    def test_wrong_instrument_method(self):
        r=complete_measurements()
        next(x for x in r if x["point"]=="P8_15_PEAK")["method"]="multimeter"
        self.assertEqual(evaluate(r,"BBB-A")["status"],"BLOCKED")
    def test_ownership_pwm(self):
        chip=self.root/"chip";chip.mkdir();(chip/"pwm1").mkdir()
        with self.assertRaises(Blocked):self.hw.pwm_free(chip)
        self.assertEqual(self.hw.log,[])
    def test_kernel_pwm_claim(self):
        chip=self.root/"chip";chip.mkdir()
        self.file("sys/kernel/debug/pwm","platform/48302200.pwm, 2 PWM devices\n pwm-0 requested enabled\n")
        with self.assertRaises(Blocked):self.hw.pwm_free(chip)
    def test_free_pwm(self):
        chip=self.root/"chip";chip.mkdir()
        self.file("sys/kernel/debug/pwm","platform/48302200.pwm, 2 PWM devices\n pwm-0 free\n pwm-1 free\n")
        self.hw.pwm_free(chip)
    def test_detect_pwm_renumbered(self):
        real_resolve=Path.resolve
        for number in (0,4,17):
            chip=self.root/"sys/class/pwm"/("pwmchip"+str(number))
            chip.mkdir(parents=True);(chip/"npwm").write_text("2")
            with patch.object(Path,"resolve",lambda p:Path("/sys/devices/48302000.epwmss/48302200.pwm")):
                self.assertEqual(self.hw.pwm(),chip)
            import shutil;shutil.rmtree(str(chip))
    def test_detect_ambiguous(self):
        for n in (0,4):self.file("sys/class/pwm/pwmchip{}/npwm".format(n),"2")
        with patch.object(Path,"resolve",lambda p:Path("/sys/devices/48302200.pwm")):
            with self.assertRaises(Blocked):self.hw.pwm()
    def test_remote_renumbered(self):
        for number,name in ((5,"4a334000.pru"),(9,"4a338000.pru")):
            self.file("sys/class/remoteproc/remoteproc{}/name".format(number),name)
            self.file("sys/class/remoteproc/remoteproc{}/state".format(number),"offline")
        self.assertTrue(str(self.hw.offline()).endswith("remoteproc5"))
    def test_busy_pru(self):
        self.test_remote_renumbered()
        self.file("sys/class/remoteproc/remoteproc9/state","running")
        with self.assertRaises(Blocked):self.hw.offline()
    def test_restore_pwm_pin_and_journal(self):
        chip=self.root/"chip";chip.mkdir()
        state=self.file("pin/state","default")
        tx=Transaction(self.hw,self.root/"state.json")
        tx.pin({"pin":"P9_14","path":str(state),"old":"default","mode":"pwm"},"pwm")
        tx.pwm_export(chip);self.hw.write(chip/"pwm0/enable","1")
        final=tx.cleanup()
        self.assertTrue(final["restored"]);self.assertEqual(state.read_text(),"default")
        self.assertFalse((chip/"pwm0").exists());self.assertFalse(tx.path.exists())
    def test_restore_failure_keeps_journal(self):
        state=self.file("pin/state","default");tx=Transaction(self.hw,self.root/"state.json")
        tx.pin({"pin":"P8_11","path":str(state),"old":"default","mode":"pruout"},"pruout")
        self.hw.fail="P8_11"
        self.assertFalse(tx.cleanup()["restored"]);self.assertTrue(tx.path.exists())
    def test_partial_pin_mutation_recovery(self):
        state=self.file("pin/state","default");tx=Transaction(self.hw,self.root/"state.json")
        rec={"pin":"P8_11","path":str(state),"old":"default","mode":"pruout"}
        self.hw.fail="P8_11"
        with self.assertRaises(OSError):tx.pin(rec,"pruout")
        self.hw.fail=None
        self.assertTrue(tx.cleanup()["restored"])
    def test_preexisting_firmware_not_overwritten(self):
        r=self.root/"r";r.mkdir();(r/"firmware").write_text("original")
        (r/"state").write_text("offline");self.file("lib/firmware/keep","keep")
        source=self.file("build/test.out","firmware")
        tx=Transaction(self.hw,self.root/"state.json");tx.firmware_start(r,source)
        self.assertEqual((r/"state").read_text(),"running")
        self.assertTrue(tx.cleanup()["restored"])
        self.assertEqual((r/"firmware").read_text(),"original");self.assertEqual(self.hw.p("/lib/firmware/keep").read_text(),"keep")
    def test_empty_acceptance(self):
        r=acceptance({},self.root)
        self.assertEqual(r["T06"]["status"],"NOT_TESTED");self.assertEqual(r["T08"]["status"],"NOT_TESTED")
    def test_fake_pass_rejected(self):
        self.file("fake.json",json.dumps({"board":"BBB-A","test":"loopback","origin":"hardware","status":"PASS"}))
        r=acceptance({"BBB-A":{"loopback":"fake.json"}},self.root)
        self.assertEqual(r["T06"]["status"],"BLOCKED")
    def test_simulated_result_rejected(self):
        self.file("fake.json",json.dumps({"board":"BBB-A","test":"loopback","origin":"simulated","status":"PASS"}))
        self.assertEqual(acceptance({"BBB-A":{"loopback":"fake.json"}},self.root)["T06"]["status"],"BLOCKED")
    def test_path_escape_rejected(self):
        self.assertEqual(acceptance({"BBB-A":{"t08":"../other.json"}},self.root)["T08"]["status"],"BLOCKED")
    def test_atomic_json(self):
        p=self.root/"r.json";atomic_json(p,{"v":None});self.assertIsNone(json.loads(p.read_text())["v"])
    def test_redaction(self):
        self.assertNotIn("aa:bb:cc:dd:ee:ff",safe_text("aa:bb:cc:dd:ee:ff serial=secret"))
    def test_py35_syntax(self):
        import ast
        if sys.version_info<(3,8):self.skipTest("AST feature_version requiere Python >=3.8 en PC")
        for p in (BASE/"hardware/pruebas").rglob("*.py"):
            ast.parse(p.read_text(encoding="utf-8"),feature_version=(3,5))
    def test_empty_input_snapshots_fail(self):
        r=pulse_raw();r["events"]=[]
        self.assertEqual(analyze(r,20000,1500,"inputs",25)["status"],"FAIL")
    def test_malformed_capture_rejected(self):
        for raw in ({},[],dict(pulse_raw(),events=[[1]]),dict(pulse_raw(),events=[[1,"nan"]]),dict(pulse_raw(),state=True)):
            with self.subTest(raw=raw),self.assertRaises(ValueError):analyze(raw,20000,1500,"loopback",25)
    def test_timeout_keeps_command_evidence(self):
        log=[]
        r=execute([sys.executable,"-c","import time;time.sleep(2)"],log,timeout=.05)
        self.assertEqual(r["exit_code"],124);self.assertEqual(log,[r])
    def test_firmware_cleanup_idempotent(self):
        r=self.root/"r";r.mkdir();(r/"firmware").write_text("original")
        (r/"state").write_text("offline");self.file("lib/firmware/keep","keep")
        tx=Transaction(self.hw,self.root/"state.json")
        tx.firmware_start(r,self.file("build/test.out","firmware"))
        self.assertTrue(tx.cleanup()["restored"])
        self.assertTrue(tx.cleanup()["restored"])
    def test_changed_firmware_owner_keeps_pins(self):
        r=self.root/"r";r.mkdir();(r/"firmware").write_text("original")
        (r/"state").write_text("offline");self.file("lib/firmware/keep","keep")
        tx=Transaction(self.hw,self.root/"state.json")
        tx.firmware_start(r,self.file("build/test.out","firmware"))
        state=self.file("pin/state","default")
        tx.pin({"pin":"P8_11","path":str(state),"old":"default","mode":"pruout"},"pruout")
        (r/"firmware").write_text("foreign.out")
        before=list(self.hw.log)
        self.assertFalse(tx.cleanup()["restored"])
        self.assertEqual(self.hw.log,before);self.assertEqual(state.read_text(),"pruout")
    def test_invalid_manifest_type(self):
        for m in ([],{"BBB-A":[]}):
            with self.assertRaises(ValueError):acceptance(m,self.root)

if __name__=="__main__":unittest.main(verbosity=2)
