'use strict';
const P=require('./protocol.cjs');
const HZ=200000000n;
// Decodes the 36-byte ABI4 event exported by ARM. No Number conversion of an
// absolute uint64 timestamp; subtract the origin in BigInt first.
class StreamDecoder {
  constructor({period=1,crc='SMBUS',availableMask=7,sampleTolerance=0.00001,onFrame=()=>{},onFault=()=>{},onBlock=()=>{}}={}){
    if(period!==1)throw Error('Only 1 Hz enabled in runtime');
    this.period=period;this.crc=crc;this.tolerance=sampleTolerance;
    this.onFrame=onFrame;this.onFault=onFault;this.onBlock=onBlock;this.epoch=null;this.seq=null;
    this.origin=null;this.lastTick=null;this.rise=null;this.fall=null;
    this.receiver=new P.PhysicalReceiver(period,crc,availableMask);this.faulted=false;
  }
  fault(reason){this.faulted=true;this.onFault(reason);}
  ingest(e){
    for(const k of ['sequence','epoch','ticks_lo','ticks_hi','r31','normalized','flags'])
      if(!Number.isInteger(e[k])||e[k]<0||e[k]>0xffffffff)throw Error('invalid '+k);
    if(this.faulted)return;
    if(this.epoch===null)this.epoch=e.epoch;
    if(e.epoch!==this.epoch){this.fault('EPOCH_CHANGED');return;}
    if(this.seq!==null&&e.sequence!==((this.seq+1)>>>0)){this.fault('SEQUENCE_GAP');return;}
    this.seq=e.sequence;
    const tick=(BigInt(e.ticks_hi)<<32n)|BigInt(e.ticks_lo);
    if(this.lastTick!==null&&tick<this.lastTick){this.fault('TIME_REVERSED');return;}
    this.lastTick=tick;if(this.origin===null)this.origin=tick;
    const t=Number(tick-this.origin)/Number(HZ);
    if(e.flags===1){ // logical clock edge, after explicit polarity normalization
      if(e.normalized&8){if(this.rise!==null&&this.fall===null){this.fault('EXTRA_RISE');return;}this.rise=t;this.fall=null;}
      else {if(this.rise===null||this.fall!==null){this.fault('EXTRA_FALL');return;}this.fall=t;}
    }else if(e.flags===2){
      if(this.rise===null||this.fall===null||Math.abs(t-this.rise-0.8*this.period)>this.tolerance){this.fault('SAMPLE_DEADLINE');return;}
      const values=[0,1,2].map(j=>(e.normalized>>j)&1).join('');
      // Header control becomes available incrementally; select CRC before final
      // parse. Management is always SMBUS, ACK uses the negotiated application CRC.
      if(this.receiver.raw.length>=22){const c=parseInt(this.receiver.raw.slice(18,22),2);
        this.receiver.algorithm=(c>=8&&c<=11||c===14||c===15)?'SMBUS':this.crc;}
      const previousError=this.receiver.error;
      const previousBlocks=this.receiver.blocks.length;
      this.receiver.ingest({rise:this.rise,fall:this.fall,values});
      if(this.receiver.blocks.length>previousBlocks)this.onBlock({...this.receiver.blocks[this.receiver.blocks.length-1],sample_t:t});
      if(this.receiver.error&&this.receiver.error!==previousError){this.onFault(this.receiver.error);}
      if(this.receiver.result){const r=this.receiver.outcome();if(r.ok)this.onFrame(r.raw);else this.onFault(r.reason);}
    }else this.fault('EVENT_FLAGS');
  }
}
function decodeEvent(buf){
  if(buf.length!==36)throw Error('event length');
  return Object.fromEntries(['sequence','epoch','ticks_lo','ticks_hi','r31','normalized','flags','acoustic_active','acoustic_gap'].map((k,i)=>[k,buf.readUInt32LE(i*4)]));
}
module.exports={StreamDecoder,decodeEvent};
