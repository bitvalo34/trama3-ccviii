'use strict';
// Reference for the proposed C accumulator. Not used by ABI3 or the live decoder.
// All times are relative integer IEP ticks; no implicit/default calibration.
class AcousticWindow{
  constructor({start,end,minActive,maxGap},initial=0){
    if(![start,end,minActive,maxGap].every(Number.isSafeInteger)||start<0||end<=start||
       end>160000000||minActive<=0||minActive>end-start||maxGap<=0||maxGap>end-start||
       ![0,1].includes(initial))throw Error('WINDOW_CONFIG');
    Object.assign(this,{start,end,minActive,maxGap,last:0,level:initial,active:0,closed:false,fault:null});
  }
  feed(t,level){
    if(this.closed||this.fault)throw Error(this.fault||'WINDOW_CLOSED');
    if(!Number.isSafeInteger(t)||t<this.last||t>0xffffffff||![0,1].includes(level))
      {this.fault='WINDOW_INPUT';throw Error(this.fault);}
    if(t-this.last>this.maxGap){this.fault='WINDOW_GAP';throw Error(this.fault);}
    const lo=Math.max(this.last,this.start),hi=Math.min(t,this.end);
    if(hi>lo&&this.level)this.active+=hi-lo;
    this.last=t;this.level=level;
    if(t>=this.end)this.closed=true;
  }
  result(){
    if(this.fault||!this.closed)throw Error(this.fault||'WINDOW_INCOMPLETE');
    return {active_ticks:this.active,value:this.active>=this.minActive?1:0};
  }
}
module.exports={AcousticWindow};
