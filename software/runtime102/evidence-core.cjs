'use strict';
function inspect(records,node,{simulation=false}={}){
  if(!Array.isArray(records)||!records.length||records.length>200000)throw Error('LOG_SIZE');
  const errors=[],origin=records[0].origin;
  if(!['hardware','simulation'].includes(origin))errors.push('ORIGIN');
  let last=-Infinity;
  records.forEach((r,i)=>{
    if(r.record!==i||r.node!==node||r.origin!==origin)errors.push('IDENTITY_OR_SEQUENCE');
    if(r.t!==undefined){if(!Number.isFinite(r.t)||r.t<last)errors.push('TIME');last=r.t;}
  });
  const simulated=simulation&&origin==='simulation';
  for(const kind of [...(simulated?[]:['LAUNCH']),'SESSION_START','SESSION_STOP','CLEANUP'])
    if(records.filter(r=>r.kind===kind).length!==1)errors.push('COUNT_'+kind);
  const pos=k=>records.findIndex(r=>r.kind===k),end=records[records.length-1];
  if(!(pos('LAUNCH')<pos('SESSION_START')&&pos('SESSION_START')<pos('SESSION_STOP')&&pos('SESSION_STOP')<pos('CLEANUP')))errors.push('LIFECYCLE');
  if(end.kind!=='CLEANUP'||!Array.isArray(end.errors)||end.errors.length)errors.push('CLEANUP');
  if(records.some(r=>['FAULT','START_FAILED'].includes(r.kind)))errors.push('SESSION_FAULT');
  const stops=['OPERATOR_STOP','CONSOLE_EOF','OPERATOR_SIGNAL','BENCH_COMPLETE'];
  if(simulated)stops.push('SIMULATION_END');
  if(records.some(r=>r.kind==='SESSION_STOP'&&!stops.includes(r.reason)))errors.push('STOP_REASON');
  const launch=records.find(r=>r.kind==='LAUNCH');
  if(!simulated&&(!launch||launch.profile?.board!=='BBB-'+node||!Number.isInteger(launch.epoch)||launch.epoch<1||
     !/^[0-9a-f]{64}$/.test(launch.firmware_sha256||'')))errors.push('PROVENANCE');
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
  if(manifest.origin==='hardware'&&[...a,...b].some(e=>e.run_id)&&
    [...a,...b].some(e=>e.run_id!==manifest.run_id))errors.push('RUN_ID');
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
function summarize(records){
  const count=(kind,test=()=>true)=>records.filter(e=>e.kind===kind&&test(e)).length;
  const ack=type=>({tx:count('TX_DONE',e=>e.type===type),rx:count('RX_FRAME',e=>e.type===type),
    accepted:count(type+'_ACCEPTED')});
  return {node:records[0]?.node,origin:records[0]?.origin,run_id:records[0]?.run_id,
    transmitted:count('TX_DONE'),received:count('RX_FRAME')+count('RX_REJECT',e=>e.reason==='CRC'),
    crc_ok:count('RX_FRAME',e=>e.crc_valid===true),crc_failed:count('RX_REJECT',e=>e.reason==='CRC'),
    ack:ack('ACK'),nack:ack('NACK'),retransmissions:count('ATTEMPT',e=>e.attempt>1),
    timeouts:count('TIMEOUT'),duplicates:count('DUPLICATE'),delivered:count('DELIVERY'),
    confirmed:count('MESSAGE_CONFIRMED'),
    failed_or_uncertain:Math.max(0,count('MESSAGE_STARTED')-count('MESSAGE_CONFIRMED')),
    errors:count('RX_REJECT')+count('FAULT')+count('CLOCK_GAP')+count('START_FAILED')};
}

function interference(manifest,a,b){
  const {schema,run_id,origin,text}=manifest;
  if(schema!==1||!/^[-a-zA-Z0-9_]{1,64}$/.test(run_id||'')||
    !['simulation','hardware'].includes(origin)||typeof text!=='string'||!text.length)throw Error('MANIFEST');
  const A=inspect(a,'A',{simulation:true}),B=inspect(b,'B',{simulation:true});
  const hardware=origin==='hardware';
  const errors=[...A.errors.map(e=>'A:'+e),...B.errors.map(e=>'B:'+e)];
  if(A.origin!==origin||B.origin!==origin)errors.push('ORIGIN_MISMATCH');
  if(hardware){
    const la=a[0],lb=b[0],hash=value=>/^[0-9a-f]{64}$/.test(value||'');
    if(la.commit!==lb.commit||!/^([0-9a-f]{40}|[0-9a-f]{64})$/.test(la.commit||'')||
      la.commit!==manifest.commit||la.mode!=='hardware'||lb.mode!=='hardware'||
      ![la,lb].every(e=>e.kind==='LAUNCH'&&hash(e.host_sha256)&&hash(e.profile_sha256)&&
        e.protocol_revision===102&&e.hardware_revision==='T51-P2-LOCAL'&&[3,7].includes(e.available_mask)))
      errors.push('HARDWARE_VERSION_OR_PROFILE');
    if([...a,...b].some(e=>e.run_id!==run_id||e.kind==='INJECTED_FAULT'))errors.push('RUN_ID_OR_INJECTION');
  }
  const chain={};
  function ordered(records,steps){
    let previous=-1;
    for(const [name,kind,test] of steps){
      const event=records.find(e=>e.record>previous&&e.kind===kind&&test(e));
      if(!event){errors.push('MISSING_'+name);return;}
      chain[name]=event.record;previous=event.record;
    }
  }
  const initial=a.find(e=>e.kind==='TX_DONE'&&e.type==='DATA');
  const same=e=>initial&&e.sid===initial.sid&&e.seq===initial.seq;
  const type=(name,extra=()=>true)=>e=>same(e)&&e.type===name&&extra(e);
  const sameData=e=>e.data===initial.data&&e.crc===initial.crc&&e.crc_algorithm===initial.crc_algorithm;
  const any=()=>true;
  ordered(a,[
    ['A_ATTEMPT_1','ATTEMPT',type('DATA',e=>e.attempt===1)],
    ['A_DATA_1','TX_DONE',type('DATA',e=>e.attempt===1&&sameData(e))],
    ['A_NACK','RX_FRAME',type('NACK',e=>e.crc_valid===true&&e.data===1)],
    ['A_NACK_ACCEPTED','NACK_ACCEPTED',e=>same(e)&&e.nack_for==='DATA'&&e.attempt===1],
    ['A_ATTEMPT_2','ATTEMPT',type('DATA',e=>e.attempt===2&&e.trigger==='nack')],
    ['A_DATA_2','TX_DONE',type('DATA',e=>e.attempt===2&&sameData(e))],
    ['A_ACK','RX_FRAME',type('ACK',e=>e.crc_valid===true&&e.data===initial.control)],
    ['A_ACK_ACCEPTED','ACK_ACCEPTED',e=>same(e)&&e.ack_for==='DATA'&&e.attempt===2],
    ['A_CONFIRMED','MESSAGE_CONFIRMED',e=>e.sid===initial.sid]
  ]);
  ordered(b,[
    ['B_CRC','RX_REJECT',type('DATA',e=>e.reason==='CRC'&&e.crc_valid===false&&e.data!==initial.data&&
      e.crc===initial.crc&&e.crc_algorithm===initial.crc_algorithm&&
      Number.isInteger(e.crc_calculated)&&e.crc_calculated!==e.crc)],
    ['B_NACK_CONTEXT','NACK_CONTEXT',same],
    ['B_NACK','TX_DONE',type('NACK',e=>e.data===1)],
    ['B_DATA_2','RX_FRAME',type('DATA',e=>e.crc_valid===true&&sameData(e))],
    ['B_ACK_START','TX_START',type('ACK',e=>e.data===initial.control)],
    // B may receive the next frame before the local ACK guard has finished.
    ['B_DELIVERY','DELIVERY',e=>e.sid===initial.sid&&e.text===text]
  ]);
  const ackSent=b.find(e=>e.kind==='TX_DONE'&&e.record>chain.B_ACK_START&&
    type('ACK',e=>e.data===initial.control)(e));
  if(ackSent)chain.B_ACK=ackSent.record;
  else errors.push('MISSING_B_ACK');
  if(a.filter(e=>e.kind==='TX_DONE'&&type('DATA')(e)).length!==2||
    a.some(e=>e.kind==='TIMEOUT'&&type('DATA')(e)))errors.push('AMBIGUOUS_DATA_ATTEMPTS');
  if(B.deliveries.length!==1||B.deliveries[0]!==text||A.confirmations!==1)errors.push('DELIVERY_OR_CONFIRMATION_COUNT');
  return {schema:1,scope:'crc-nack-retry',origin,run_id,status:errors.length?'FAIL':'PASS',
    physical_status:hardware?'EJECUTADO SIN CUMPLIR':'PREPARADO',errors,chain,
    sid:initial?.sid,seq:initial?.seq,A:summarize(a),B:summarize(b)};
}
module.exports={inspect,pair,summarize,interference};
