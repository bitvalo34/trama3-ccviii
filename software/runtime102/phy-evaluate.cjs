#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),crypto=require('node:crypto');
const {inspect}=require('./phy.cjs'),P=require('./protocol.cjs'),{StreamDecoder}=require('./stream.cjs');
function evaluate(tx,rx){
  const errors=[],one=(records,kind)=>records.find(e=>e.kind===kind);
  const t=one(tx,'PHY_START'),r=one(rx,'PHY_START');
  if(!t||!r||t.role!=='tx'||r.role!=='rx'||t.run_id!==r.run_id||t.node===r.node||t.trial!==r.trial)throw Error('INDEPENDENT_RUN_IDENTITY');
  for(const records of [tx,rx]){
    const launch=one(records,'LAUNCH'),stop=one(records,'SESSION_STOP'),cleanup=one(records,'CLEANUP'),ready=one(records,'BRIDGE_READY');
    if(!launch||launch.mode!=='hardware'||records.some(e=>e.origin!=='hardware'))errors.push('NOT_HARDWARE_ORIGIN');
    if(!launch||launch.profile.available_mask!==3||launch.profile.experiment!=='optical-acoustic')errors.push('PROFILE');
    if(!ready||ready.abi!==4)errors.push('ABI');
    if(!stop||stop.reason!=='PHY_COMPLETE')errors.push('INCOMPLETE_OR_TIMEOUT');
    if(!cleanup||cleanup.errors.length)errors.push('CLEANUP');
  }
  if(r.plan!==null)errors.push('RX_EXPECTED_DATA_PRESENT');
  const captures=rx.filter(e=>e.kind==='CAPTURE'),samples=captures.filter(e=>e.flags===2);
  const rp=one(rx,'LAUNCH').profile;
  for(const e of captures){
    const raw=(((e.r31>>5)&1)|(((e.r31>>14)&1)<<1)|(((e.r31>>15)&1)<<3))^(rp.rx_invert&11);
    if((raw&9)!==(e.normalized&9))errors.push('RAW_POLARITY_MISMATCH');
    if(e.flags===2&&rp.acoustic){
      const a=rp.acoustic;
      if(!Number.isInteger(e.acoustic_active)||e.acoustic_active<0||e.acoustic_active>a.end-a.start||
         !Number.isInteger(e.acoustic_gap)||e.acoustic_gap<=0||e.acoustic_gap>a.max_gap)errors.push('ACOUSTIC_WINDOW_EVIDENCE');
      const bit=a.min_active?Number(e.acoustic_active>=a.min_active):(raw>>1)&1;
      if(bit!==((e.normalized>>1)&1))errors.push('ACOUSTIC_DECISION_MISMATCH');
    }
  }
  const timing=inspect(captures,t.ticks);if(timing.status!=='PASS')errors.push(...timing.errors);
  const sent=tx.filter(e=>e.kind==='PHY_TX_DONE'&&e.id===1).length===1;
  if(!sent)errors.push('TX_NOT_COMPLETED');
  if(tx.filter(e=>e.kind==='OUTPUT_PREPARED'&&e.id===1&&e.readback&&e.readback.readback_verified).length!==t.ticks)errors.push('MCP_READBACK_MISSING');
  let reconstructed=false,crc=false,confirmed=false,frame=null,blocks=[],calibration=null;
  if(t.trial==='frame'){
    const decoder=new StreamDecoder({availableMask:3,crc:t.plan.frame.algorithm,onFrame:bits=>{frame=P.parse(bits,t.plan.frame.algorithm);reconstructed=true;crc=frame.ok;
      if(bits!==t.plan.frame.bits)errors.push('PAYLOAD_MISMATCH');},onFault:reason=>errors.push(reason)});
    for(const e of captures)decoder.ingest(e);
    blocks=decoder.receiver.blocks;
    if(!reconstructed||!crc||blocks.length!==27)errors.push('FRAME_NOT_VALIDATED');
    if(!decoder.receiver.meta||decoder.receiver.meta.seen!==3)errors.push('BOTH_PILOTS_REQUIRED_FOR_THIS_TRIAL');
    if(t.ack){
      let ackFrame=null;
      const back=tx.filter(e=>e.kind==='CAPTURE');
      const d=new StreamDecoder({availableMask:3,crc:t.plan.frame.algorithm,onFrame:bits=>{ackFrame=P.parse(bits,t.plan.frame.algorithm);},onFault:reason=>errors.push('ACK_'+reason)});
      for(const e of back)d.ingest(e);
      const f=t.plan.frame;
      confirmed=!!(ackFrame&&ackFrame.ok&&ackFrame.type==='ACK'&&ackFrame.sid===f.sid&&ackFrame.seq===f.seq&&ackFrame.data===f.ctrl&&
        inspect(back,87).status==='PASS'&&one(tx,'PHY_ACK_RECEIVED')&&rx.some(e=>e.kind==='PHY_TX_DONE'&&e.id===2));
      if(!confirmed)errors.push('NO_PHYSICAL_ACK');
    }
  }else if(t.trial==='c1'){
    const groups=[0,1].map(bit=>samples.filter((e,i)=>((t.plan.vectors[i]>>1)&1)===bit).map(e=>e.acoustic_active));
    if(!groups.every(g=>g.length&&g.every(Number.isInteger)))errors.push('ACOUSTIC_STATISTICS_MISSING');
    else{
      const offMax=Math.max(...groups[0]),onMin=Math.min(...groups[1]);
      calibration={off_max_ticks:offMax,on_min_ticks:onMin,separation_ticks:onMin-offMax,
        suggested_min_active:onMin>offMax?Math.floor((offMax+onMin)/2)+1:null,
        note:'Derived offline from this 010101 run; repeat separately on each board and with both channels active.'};
      if(onMin<=offMax)errors.push('ACOUSTIC_NO_SEPARATION');
    }
  }else if(t.trial!=='clock'){
    const mask=t.trial==='c0'?1:3;
    if(samples.some((e,i)=>(e.normalized&mask)!==(t.plan.vectors[i]&mask)))errors.push('VECTOR_MISMATCH');
    if(t.trial==='pair')for(let i=0;i<samples.length;i+=3){
      const y=samples.slice(i,i+3).flatMap(e=>[e.normalized&1,e.normalized>>1&1,null]);
      if(y.length===9)blocks.push({received:y,...P.matrix.decode(y,{diagnostics:true})});
    }
  }
  const first=captures.length?((BigInt(captures[0].ticks_hi)<<32n)|BigInt(captures[0].ticks_lo)):0n;
  const observations=samples.map((e,i)=>({tick:i,tx_vector:t.plan.vectors[i],
    tx_gpio:{GPA0:t.plan.vectors[i]&1,GPA1:t.plan.vectors[i]>>1&1},
    raw_r31:e.r31,normalized_c0_c1:[e.normalized&1,e.normalized>>1&1],c2:null,rx_invert:rp.rx_invert,
    relative_iep_ticks:String(((BigInt(e.ticks_hi)<<32n)|BigInt(e.ticks_lo))-first),
    acoustic_active:e.acoustic_active,acoustic_gap:e.acoustic_gap,
    point_vector_matches:(e.normalized&3)===(t.plan.vectors[i]&3)}));
  return {schema:1,run_id:t.run_id,trial:t.trial,tx_node:t.node,rx_node:r.node,status:errors.length?'FAIL':'PASS',errors:[...new Set(errors)],
    evidence_scope:'Independent local hardware logs, not independent instrument certification',
    levels:{tx_completed:sent,physical_capture_complete:timing.status==='PASS',frame_reconstructed:reconstructed,crc_valid:crc,physical_ack:confirmed},
    available_mask:3,c2:'known absence declared in profile; not sampled for decoding',three_media_academic_requirement:'NOT_TESTED',
    rx_configuration:{rx_invert:rp.rx_invert,i2c_device:rp.i2c_device,acoustic:rp.acoustic},
    timing,frame,blocks,calibration,observations};
}
module.exports={evaluate};
if(require.main===module){
  try{
    const [a,b,out]=process.argv.slice(2);if(!a||!b||!out)throw Error('phy-evaluate.cjs TX.jsonl RX.jsonl NEW_REPORT.json');
    const read=f=>{const data=fs.readFileSync(f);if(data.length>16*1024*1024)throw Error('LOG_LIMIT');return data.toString().trim().split('\n').map(JSON.parse);};
    const result=evaluate(read(a),read(b));result.sources=[a,b].map(file=>({file,sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')}));
    fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result,null,2));process.exitCode=result.status==='PASS'?0:1;
  }catch(e){console.error(e.stack);process.exitCode=1;}
}
