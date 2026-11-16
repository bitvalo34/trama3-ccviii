"""Exclusive runtime transaction. Python 3.5+, injectable hardware for PC tests.
T06 detection/restoration is reused without modifying its implementation.
"""
import json
import os
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'hardware/pruebas'))
sys.path.insert(0, str(ROOT / 'hardware/pruebas/t06'))
from common import read, atomic_json, Blocked
from resources import Hardware, Transaction
from p2 import Outputs, LinuxBackend
from lab_profile import validate_lab

PIN_MODES = [('P8_15','pruin'), ('P8_16','pruin'), ('P9_24','pruin'),
             ('P9_27','pruin'), ('P9_14','pwm'), ('P8_11','pruout')]

class BoardOwner:
    def __init__(self, hw, directory, firmware, output_factory):
        self.hw=hw;self.directory=Path(directory);self.firmware=Path(firmware)
        self.output_factory=output_factory;self.outputs=None;self.tx=None
        self.locked=False;self.started=False;self.io=None;self.release_result=None
        self.boot=read(hw.p('/proc/sys/kernel/random/boot_id'))

    def acquire(self, profile):
        if self.started: raise Blocked('OWNER_ALREADY_STARTED')
        self.started=True
        if not self.boot: raise Blocked('BOOT_ID_UNAVAILABLE')
        # Atomic directory creation. Never steal a lock or overwrite recovery data.
        self.directory.mkdir(mode=0o700);self.locked=True
        try:
            atomic_json(self.directory/'owner.json', {'schema':1,'board':profile['board'],
                'pid':os.getpid(),'boot_id':self.boot,'status':'ACQUIRING'})
            atomic_json(self.directory/'profile.json',profile)
            self.hw.reserve()
            if self.hw.p('/run/trama3-t06/state.json').exists(): raise Blocked('T06_RECOVERY_PENDING')
            if not self.firmware.is_file(): raise Blocked('FIRMWARE_MISSING')
            lab=profile.get('experiment')=='optical-acoustic'
            if lab: validate_lab(profile)
            remote=self.hw.offline()
            if not lab:
                chip=self.hw.pwm();self.hw.pwm_free(chip)
            # C2/servo are physically disconnected, not exported or driven.
            modes=[x for x in PIN_MODES if not lab or x[0] not in ('P9_14','P9_24')]
            pins=[self.hw.pin_check(pin,mode) for pin,mode in modes]
            self.hw.check_i2c(profile)
            # Persist an empty transaction before the first change.
            self.tx=Transaction(self.hw,self.directory/'resources.json');self.tx.save()
            channel=None if lab else self.tx.pwm_export(chip)
            self.io=self.output_factory(channel,profile)
            c=profile['calibration'];self.outputs=Outputs(self.io,c.get('servo_low_us'),c.get('servo_high_us'),optical_acoustic=lab)
            self.outputs.initialize()
            self.clock_pin=next(rec for rec in pins if rec['pin']=='P8_11')
            for rec in pins: self.tx.pin(rec,'gpio_pd' if rec['pin']=='P8_11' else rec['mode'])
            self.tx.firmware_start(remote,self.firmware)
            atomic_json(self.directory/'owner.json', {'schema':1,'board':profile['board'],
                'pid':os.getpid(),'boot_id':self.boot,'status':'ACQUIRED'})
            return {'board':profile['board'],'pwm':str(channel),'remoteproc':str(remote),'abi':4}
        except Exception:
            self.release();raise

    def activate_clock(self):
        if not self.outputs or not self.outputs.ready or self.release_result is not None:raise Blocked('OWNER_NOT_ACTIVE')
        self.tx.pin(self.clock_pin,'pruout')

    def prepare(self,vector):
        if not self.outputs or self.release_result is not None: raise Blocked('OWNER_NOT_ACTIVE')
        return self.outputs.prepare(vector)

    def shutdown_outputs(self):
        errors=self.outputs.shutdown() if self.outputs else []
        if errors: raise IOError('; '.join(errors))

    def release(self):
        if self.release_result is not None: return self.release_result
        if not self.locked: return {'restored':True,'errors':[]}
        errors=[]
        if read(self.hw.p('/proc/sys/kernel/random/boot_id'))!=self.boot:
            self.release_result={'restored':False,'errors':['BOOT_CHANGED_REVIEW_REQUIRED']}
            return self.release_result
        try:self.shutdown_outputs()
        except Exception as exc:errors.append('outputs: '+str(exc))
        if self.tx:
            try:
                result=self.tx.cleanup();errors.extend(result['errors'])
            except Exception as exc:errors.append('transaction cleanup: '+str(exc))
        if self.io:
            try:self.io.register(0x00,0xff) # Return freshly-reset MCP port A to input.
            except Exception as exc:errors.append('MCP direction restore: '+str(exc))
            try:self.io.close()
            except Exception as exc:errors.append('i2c close: '+str(exc))
        if not errors:
            try:
                (self.directory/'owner.json').unlink()
                (self.directory/'profile.json').unlink()
                self.directory.rmdir();self.locked=False
            except Exception as exc:errors.append('journal removal: '+str(exc))
        if errors:
            try:atomic_json(self.directory/'cleanup-errors.json',{'errors':errors})
            except Exception as exc:errors.append('journal write: '+str(exc))
        self.release_result={'restored':not errors,'errors':errors}
        self.hw.unreserve()
        return self.release_result

class LinuxHardware(Hardware):
    def reserve(self):
        import fcntl
        base=self.p('/run/trama3-t06');base.mkdir(mode=0o700,exist_ok=True)
        st=base.stat()
        if base.is_symlink() or st.st_uid!=0 or st.st_mode&0o077:raise Blocked('UNSAFE_T06_LOCK_DIRECTORY')
        fd=os.open(str(base/'lock'),os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
        try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except Exception:os.close(fd);raise Blocked('T06_OR_RUNTIME_BUSY')
        self.lock_fd=fd
    def unreserve(self):
        if getattr(self,'lock_fd',None) is not None:os.close(self.lock_fd);self.lock_fd=None
    def check_i2c(self,profile):
        if 'TI AM335x BeagleBone Black' not in read(self.p('/proc/device-tree/model'),''):raise Blocked('BOARD_MODEL')
        if profile.get('experiment')=='optical-acoustic': validate_lab(profile)
        elif profile.get('i2c_device')!='/dev/i2c-2':raise Blocked('I2C_BUS_NOT_REVIEWED')
        if profile.get('mcp_reset_confirmed') is not True:raise Blocked('MCP_RESET_NOT_CONFIRMED')
        if 'gpio_pd' not in self.command(['config-pin','-l','P8_11']).split():raise Blocked('CLOCK_ISOLATION_MODE_MISSING')
        for pin in ('P9_19','P9_20'):
            if read(self.pin_state(pin))!='i2c':raise Blocked('I2C_PINMUX_NOT_READY: '+pin)
        bus=profile['i2c_device'].split('-')[-1]
        adapter=self.p('/sys/class/i2c-dev/i2c-'+bus+'/device').resolve()
        if profile.get('experiment')=='optical-acoustic' and '4819c000' not in str(adapter):
            raise Blocked('I2C_ADAPTER_NOT_P9_19_P9_20')
        if self.p('/sys/bus/i2c/devices/'+bus+'-0020/driver').exists():raise Blocked('MCP_KERNEL_DRIVER_OWNS_ADDRESS')
        if not self.p(profile['i2c_device']).exists():raise Blocked('I2C_DEVICE_MISSING')

def linux_owner(profile,firmware):
    if sys.platform!='linux' or os.geteuid()!=0:raise Blocked('LINUX_ROOT_REQUIRED')
    return BoardOwner(LinuxHardware(),'/run/trama3-runtime102',firmware,
        lambda channel,p:LinuxBackend(p['i2c_device'],channel))
