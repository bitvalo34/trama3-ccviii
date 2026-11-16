'use strict';
// One reference for the wire format; importing it never runs a simulation.
const reference = require('../matrices102/engine.js');
const matrix = require('../matrices102/core.js');
module.exports = Object.freeze({
  VERSION: 6, TYPES: reference.TYPES, RATE: reference.RATE,
  frame: reference.frame, parse: reference.parse, encode: reference.encode,
  decode: reference.decode, crc8: reference.crc8, CRCS: reference.CRCS,
  rows: bits => reference.layout(bits, 7), PhysicalReceiver: reference.PhysicalReceiver,
  matrix,
  ackTimeout: returnPeriod => {
    if (!Number.isFinite(returnPeriod) || returnPeriod <= 0) throw Error('period');
    return 178 * returnPeriod + 2;
  }
});
