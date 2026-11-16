'use strict';
const assert=require('node:assert/strict');
const {validate}=require('./profiles.cjs');
const p=structuredClone(require('./profiles/BBB-A.json'));
// Synthetic evidence tests validation only; never written to a usable profile.
p.calibration={board:'BBB-A',status:'MEASURED',evidence:'TEST FIXTURE',checked_at:'fixture',
  servo_low_us:1000,servo_high_us:2000,settle_ms:100,rx_invert:8,i2c_device:'/dev/i2c-2'};
assert.throws(()=>validate(p,{hardware:true}),/POLARITY/);
p.rx_invert=8;validate(p,{hardware:true});
p.calibration.rx_invert=9;assert.throws(()=>validate(p,{hardware:true}),/POLARITY/);
p.calibration.rx_invert=8;p.calibration.i2c_device='/dev/i2c-1';
assert.throws(()=>validate(p,{hardware:true}),/I2C/);
p.calibration.i2c_device='/dev/i2c-2';p.hardware_revision='T51-P1';
assert.throws(()=>validate(p,{hardware:true}),/HARDWARE_REVISION/);
console.log('PASS physical profile rejects direct clock, inconsistent polarity, unverified I2C and P1');
