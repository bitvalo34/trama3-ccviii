'use strict';
const matrix=require('../matrices102/core.js');
const N=87,HZ=200000000n;
const patterns=['clock','c0','c1','c2','vectors','matrix-00','matrix-01','matrix-10','matrix-11'];
function plan(pattern,runId,tx){
  if(!patterns.includes(pattern)||!['A','B'].includes(tx)||!/^[-a-zA-Z0-9_]{1,64}$/.test(runId))throw Error('BENCH_PLAN');
  let cycle;
  if(pattern==='clock')cycle=[0];
  else if(/^c[012]$/.test(pattern))cycle=[0,1<<Number(pattern[1])];
  else if(pattern==='vectors')cycle=[0,1,2,4,7,6,5,3];
  else {const bits=pattern.slice(-2).split('').map(Number),word=matrix.encode(bits);
    cycle=[0,1,2].map(i=>word[i*3]|word[i*3+1]<<1|word[i*3+2]<<2);}
  return {schema:1,kind:'BENCH_PLAN',run_id:runId,tx,rx:tx==='A'?'B':'A',pattern,
    period_ticks:String(HZ),sample_ticks:'160000000',vectors:Array.from({length:N},(_,i)=>cycle[i%cycle.length]),
    note:'Diagnostic vectors, not protocol frames. No automatic physical certification.'};
}
function validatePlan(p){
  const expected=plan(p.pattern,p.run_id,p.tx);
  if(JSON.stringify(p.vectors)!==JSON.stringify(expected.vectors)||p.rx!==expected.rx||
    p.schema!==1||p.kind!=='BENCH_PLAN'||p.period_ticks!==expected.period_ticks||p.sample_ticks!==expected.sample_ticks)throw Error('ALTERED_PLAN');
  return p;
}
function capture(p,events,{count=N,availableMask=7,compare=true}={}){
  validatePlan(p);
  if(!Array.isArray(events)||events.length>1024)throw Error('CAPTURE_LIMIT');
  const errors=[],samples=[],periods=[],widths=[],offsets=[];
  let epoch=null,seq=null,last=null,rise=null,fall=null,previousRise=null,phase='rise',index=0;
  function bad(x){errors.push(x);}
  for(const e of events){
    for(const k of ['sequence','epoch','ticks_lo','ticks_hi','r31','normalized','flags'])
      if(!Number.isInteger(e[k])||e[k]<0||e[k]>0xffffffff)throw Error('CAPTURE_FIELD '+k);
    if(e.normalized>15||![1,2].includes(e.flags))throw Error('CAPTURE_VALUE');
    if(epoch===null)epoch=e.epoch;
    if(!epoch||epoch!==e.epoch)bad('EPOCH');
    if(seq!==null&&e.sequence!==((seq+1)>>>0))bad('SEQUENCE_GAP');
    seq=e.sequence;
    const tick=BigInt(e.ticks_hi)*4294967296n+BigInt(e.ticks_lo);
    if(last!==null&&tick<last)bad('TIME_REVERSED');
    last=tick;
    if(e.flags===1&&(e.normalized&8)){
      if(phase!=='rise')bad('RISE_ORDER');
      if(previousRise!==null){const dt=tick-previousRise;periods.push(Number(dt));
        if(dt<190000000n||dt>210000000n)bad('PERIOD');}
      previousRise=tick;rise=tick;fall=null;phase='fall';
    }else if(e.flags===1){
      if(phase!=='fall'||rise===null){bad('FALL_ORDER');continue;}
      fall=tick;const dt=fall-rise,target=index===0?120000000n:40000000n;
      widths.push(Number(dt));if(dt<target-10000000n||dt>target+10000000n)bad('PULSE_WIDTH');
      phase='sample';
    }else{
      if(phase!=='sample'||rise===null||fall===null){bad('SAMPLE_ORDER');continue;}
      const dt=tick-rise;offsets.push(Number(dt));
      if(dt<159998000n||dt>160002000n)bad('SAMPLE_DEADLINE');
      samples.push(e.normalized&7);index++;phase='rise';
    }
  }
  if(events.length!==count*3||samples.length!==count||phase!=='rise')bad('INCOMPLETE_CAPTURE');
  const mismatches=compare?samples.map((v,i)=>({index:i,expected:p.vectors[i]&availableMask,observed:v&availableMask}))
    .filter(x=>x.expected!==x.observed):[];
  if(mismatches.length)bad('VECTOR_MISMATCH');
  const summary=a=>a.length?{min:Math.min(...a),max:Math.max(...a)}:null;
  return {schema:1,scope:'bench-capture-analysis',run_id:p.run_id,status:errors.length?'FAIL':'PASS',
    physical_status:'NOT_TESTED',errors:[...new Set(errors)],samples:samples.length,mismatches,
    per_channel:compare?[0,1,2].filter(c=>availableMask&(1<<c)).map(c=>({channel:c,errors:samples.filter((v,i)=>((v^p.vectors[i])>>c)&1).length})):null,
    period_ticks:summary(periods),width_ticks:summary(widths),sample_offset_ticks:summary(offsets),
    timebase:'IEP nominal 200 MHz; no independent calibration',
    limits:'Revision102 period +/-5%, high pulse +/-0.05T; runtime sample +/-10 us. No independent clock calibration.'};
}
module.exports={plan,validatePlan,capture,patterns};
