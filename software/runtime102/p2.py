"""P2 output controller, Python >=3.5. Backend injected; no hardware on import.
No default servo endpoints: calibration must belong to the actual board.
"""
import os
from pathlib import Path

class LinuxBackend:
    def __init__(self, i2c, pwm):
        import fcntl
        self.fd = os.open(i2c, os.O_RDWR)
        try:
            fcntl.ioctl(self.fd, 0x0703, 0x20)
        except Exception:
            os.close(self.fd)
            raise
        self.pwm = Path(pwm) if pwm is not None else None
    def read_register(self, reg):
        if os.write(self.fd, bytes([reg])) != 1:
            raise IOError('Incomplete MCP23017 register selection')
        data = os.read(self.fd, 1)
        if len(data) != 1: raise IOError('Incomplete MCP23017 read')
        return data[0]
    def register(self, reg, value):
        if os.write(self.fd, bytes([reg, value])) != 2:
            raise IOError('Incomplete MCP23017 write')
    def pwm_write(self, name, value):
        if name not in ('enable','period','duty_cycle'):
            raise ValueError('PWM attribute')
        (self.pwm / name).write_text(str(value))
    def close(self):
        os.close(self.fd)

class Outputs:
    def __init__(self, backend, servo_low_us=None, servo_high_us=None, optical_acoustic=False):
        self.optical_acoustic=optical_acoustic
        if not optical_acoustic and not all(type(v) is int and 1000 <= v <= 2000 for v in (servo_low_us,servo_high_us)):
            raise ValueError('Servo calibration outside tested pulse envelope')
        if not optical_acoustic and servo_low_us == servo_high_us:
            raise ValueError('Distinct mechanical states required')
        self.io=backend;self.servo=(servo_low_us,servo_high_us);self.ready=False;self.fault=False
    def initialize(self):
        # Requires exclusive freshly-reset MCP (BANK=0) and inactive PWM with
        # valid period, checked by supervisor. Never attach to an unknown consumer.
        try:
            if self.optical_acoustic:
                # A fresh BANK=0 reset is required, not inferred from a write.
                if self.io.read_register(0x00)!=0xff or self.io.read_register(0x0a)!=0:
                    raise IOError('MCP_RESET_STATE')
            self.io.register(0x14,0) # OLATA OFF before IODIRA output
            self.io.register(0x00,0xfc) # GPA0/GPA1 only
            if self.optical_acoustic: self.verify(0)
            else:
                self.io.pwm_write('period',20000000)
                self.io.pwm_write('duty_cycle',0)
            self.ready=True
        except Exception:
            self.fault=True;self.shutdown();raise
    def prepare(self,vector):
        if type(vector) is not int or not 0<=vector<=7:
            raise ValueError('Vector')
        if not self.ready or self.fault:
            raise RuntimeError('Outputs unavailable')
        try:
            if self.optical_acoustic and self.io.read_register(0x00)!=0xfc:
                raise IOError('MCP_IODIRA_CHANGED')
            self.io.register(0x14,vector&3)
            if self.optical_acoustic: self.verify(vector&3)
            else:
                self.io.pwm_write('duty_cycle',self.servo[(vector>>2)&1]*1000)
                self.io.pwm_write('enable',1)
        except Exception:
            self.fault=True;self.shutdown();raise
        # Caller publishes READY only after successful completion; NOT settlement.
        return {'iodira':0xfc,'olata':vector&3,'readback_verified':self.optical_acoustic}
    def verify(self, value):
        state={reg:self.io.read_register(reg) for reg in (0x00,0x0a,0x14)}
        if state!={0x00:0xfc,0x0a:0,0x14:value}:
            raise IOError('MCP_READBACK '+str(state))
        return state
    def shutdown(self):
        self.ready=False;errors=[]
        operations=[lambda:self.io.register(0x14,0)]
        if self.optical_acoustic:
            operations.append(lambda:self.verify(0))
        else: operations.append(lambda:self.io.pwm_write('enable',0))
        for fn in operations:
            try:fn()
            except Exception as exc:errors.append(str(exc))
        if errors:self.fault=True
        return errors
