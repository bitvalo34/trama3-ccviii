"""Filesystem-backed peripheral model; does not open any real device."""
from pathlib import Path
from board_owner import Hardware, read, Blocked

class MockHardware(Hardware):
    def __init__(self,root,fail=None):
        super(MockHardware,self).__init__(root);self.fail=fail;self.failed=False
    def initialize(self):
        for name,value in [('proc/sys/kernel/random/boot_id','mock-boot'),
            ('sys/pru0/state','offline'),('sys/pru0/firmware','original.out'),
            ('sys/pru1/state','offline')]:
            p=self.p('/'+name);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value)
        self.p('/lib/firmware').mkdir(parents=True,exist_ok=True)
        self.p('/sys/pwmchip4').mkdir(parents=True,exist_ok=True)
        for pin in ('P8_11','P8_15','P8_16','P9_24','P9_27','P9_14'):
            p=self.p('/pins/'+pin);p.parent.mkdir(parents=True,exist_ok=True);p.write_text('default')
    def offline(self):
        if any(read(self.p('/sys/'+n+'/state'))!='offline' for n in ('pru0','pru1')):raise Blocked('PRU_BUSY')
        return self.p('/sys/pru0')
    def reserve(self):pass
    def unreserve(self):pass
    def pwm(self):return self.p('/sys/pwmchip4')
    def pwm_free(self,chip):
        if list(chip.glob('pwm*')):raise Blocked('PWM_BUSY')
    def check_i2c(self,profile):
        if self.p('/i2c-busy').exists():raise Blocked('I2C_BUSY')
    def pin_check(self,pin,mode):
        p=self.p('/pins/'+pin)
        if read(p)!='default':raise Blocked('PIN_BUSY')
        return {'pin':pin,'path':str(p),'old':'default','mode':mode}
    def pin_set(self,rec,mode):self.write(Path(rec['path']),mode)
    def write(self,path,value):
        path=Path(path);value=str(value)
        if self.fail==path.name and not self.failed:
            self.failed=True;raise IOError('INJECTED_WRITE_FAILURE')
        if path.name=='export':
            ch=path.parent/'pwm0';ch.mkdir()
            for n in ('period','duty_cycle','enable'):(ch/n).write_text('0')
        elif path.name=='unexport':
            ch=path.parent/'pwm0'
            for p in ch.iterdir():p.unlink()
            ch.rmdir()
        elif path.name=='state':path.write_text({'start':'running','stop':'offline'}[value])
        else:path.write_text(value)
        self.log.append({'write':str(path),'value':value})

class MockIO:
    def __init__(self,channel):self.channel=Path(channel);self.closed=False;self.registers={}
    def register(self,reg,value):self.registers[reg]=value
    def pwm_write(self,name,value):(self.channel/name).write_text(str(value))
    def close(self):self.closed=True
