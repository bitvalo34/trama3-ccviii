'use strict';
function inspect(records,node){
  if(!Array.isArray(records)||!records.length||records.length>200000)throw Error('LOG_SIZE');
  const errors=[],origin=records[0].origin;
  if(!['hardware','simulation'].includes(origin))errors.push('ORIGIN');
  let last=-Infinity;
  records.forEach((r,i)=>{
    if(r.record!==i||r.node!==node||r.origin!==origin)errors.push('IDENTITY_OR_SEQUENCE');
    if(r.t!==undefined){if(!Number.isFinite(r.t)||r.t<last)errors.push('TIME');last=r.t;}
  });
  for(const kind of ['LAUNCH','SESSION_START','SESSION_STOP','CLEANUP'])
    if(records.filter(r=>r.kind===kind).length!==1)errors.push('COUNT_'+kind);
  const pos=k=>records.findIndex(r=>r.kind===k),end=records[records.length-1];
  if(!(pos('LAUNCH')<pos('SESSION_START')&&pos('SESSION_START')<pos('SESSION_STOP')&&pos('SESSION_STOP')<pos('CLEANUP')))errors.push('LIFECYCLE');
  if(end.kind!=='CLEANUP'||!Array.isArray(end.errors)||end.errors.length)errors.push('CLEANUP');
  if(records.some(r=>['FAULT','START_FAILED'].includes(r.kind)))errors.push('SESSION_FAULT');
  if(records.some(r=>r.kind==='SESSION_STOP'&&!['OPERATOR_STOP','CONSOLE_EOF','OPERATOR_SIGNAL','BENCH_COMPLETE'].includes(r.reason)))errors.push('STOP_REASON');
  const launch=records.find(r=>r.kind==='LAUNCH');
  if(!launch||launch.profile?.board!=='BBB-'+node||!Number.isInteger(launch.epoch)||launch.epoch<1||
     !/^[0-9a-f]{64}$/.test(launch.firmware_sha256||''))errors.push('PROVENANCE');
  return {origin,errors:[...new Set(errors)],deliveries:records.filter(r=>r.kind==='DELIVERY').map(r=>r.text),
    confirmations:records.filter(r=>r.kind==='MESSAGE_CONFIRMED').length,
    retries:records.filter(r=>r.kind==='ATTEMPT'&&r.attempt>1).length,
    rejections:records.filter(r=>r.kind==='RX_REJECT').map(r=>r.reason),
    nack_contexts:records.filter(r=>r.kind==='NACK_CONTEXT').length,
    nack_accepted:records.filter(r=>r.kind==='NACK_ACCEPTED').length};
}
function pair(manifest,a,b){
  if(manifest.schema!==1||!/^[-a-zA-Z0-9_]{1,64}$/.test(manifest.run_id||'')||
    !['hardware','simulation'].includes(manifest.origin)||
    !Array.isArray(manifest.A_to_B)||!Array.isArray(manifest.B_to_A)||
    !manifest.A_to_B.length||!manifest.B_to_A.length||
    [...manifest.A_to_B,...manifest.B_to_A].some(x=>typeof x!=='string'))throw Error('MANIFEST');
  const A=inspect(a,'A'),B=inspect(b,'B'),errors=[...A.errors.map(e=>'A:'+e),...B.errors.map(e=>'B:'+e)];
  if(A.origin!==manifest.origin||B.origin!==manifest.origin)errors.push('ORIGIN_MISMATCH');
  if(JSON.stringify(A.deliveries)!==JSON.stringify(manifest.B_to_A))errors.push('A_DELIVERIES');
  if(JSON.stringify(B.deliveries)!==JSON.stringify(manifest.A_to_B))errors.push('B_DELIVERIES');
  if(A.confirmations!==manifest.A_to_B.length||B.confirmations!==manifest.B_to_A.length)errors.push('CONFIRMATIONS');
  return {schema:1,scope:'bidirectional-delivery-and-cleanup',run_id:manifest.run_id,origin:manifest.origin,
    status:errors.length?'FAIL':'PASS',physical_status:'NOT_TESTED',errors,A,B,
    limitations:['Log analysis is not authentication of physical observations.',
      'No cross-board comparison of absolute clocks.',
      'Does not certify CRC/NACK causal chain, electrical acceptance, or all protocol requirements.',
      'Manifest association of these two files is supplied by operator; no shared session identifier in ABI3 logs.']};
}
module.exports={inspect,pair};
