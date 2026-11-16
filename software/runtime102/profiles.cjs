'use strict';
const fs=require('node:fs');
function validate(p,{hardware=false}={}){
  if(p.schema!==1||!['BBB-A','BBB-B'].includes(p.board)||p.abi!==3||p.period_s!==1)throw Error('PROFILE_IDENTITY');
  if(!Number.isInteger(p.rx_invert)||p.rx_invert<0||p.rx_invert>15)throw Error('PROFILE_POLARITY');
  if(!p.pins||p.pins.tx!=='P8_11'||p.pins.clock!=='P8_15'||p.pins.pwm!=='P9_14'||
    JSON.stringify(p.pins.data)!==JSON.stringify(['P9_27','P8_16','P9_24']))throw Error('PROFILE_PINMAP');
  if(hardware){
    const c=p.calibration;
    if(!c||c.board!==p.board||!c.evidence||!c.checked_at||c.status!=='MEASURED')throw Error('PROFILE_UNCALIBRATED');
    if(![c.servo_low_us,c.servo_high_us].every(v=>Number.isInteger(v)&&v>=1000&&v<=2000)||c.servo_low_us===c.servo_high_us)throw Error('PROFILE_SERVO');
    if(!Number.isFinite(c.settle_ms)||c.settle_ms<0||c.settle_ms>800)throw Error('PROFILE_SETTLING');
    if(p.hardware_revision!=='T51-P2-LOCAL')throw Error('PROFILE_HARDWARE_REVISION');
    if(!(p.rx_invert&8)||c.rx_invert!==p.rx_invert)throw Error('PROFILE_RX_POLARITY_UNVERIFIED');
    if(p.i2c_device!=='/dev/i2c-2'||c.i2c_device!==p.i2c_device)throw Error('PROFILE_I2C_UNVERIFIED');
  }
  return p;
}
function load(file,options){return validate(JSON.parse(fs.readFileSync(file,'utf8')),options);}
module.exports={load,validate};
