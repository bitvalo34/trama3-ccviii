#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path');
const {launch}=require('./launcher.cjs');
const {load,validateLab}=require('./profiles.cjs');
const {makePlan,PhysicalTrial}=require('./phy.cjs');
async function main(args=process.argv.slice(2)){
  const command=args.shift(),o={};
  const accepted=['profile','kind','pair','data-hex','seq','sid','crc','run','directory','timeout','ticks','firmware','host'];
  while(args.length){const k=args.shift();if(k==='--ack'){o.ack=true;continue;}
    if(!k.startsWith('--')||!accepted.includes(k.slice(2))||!args.length)throw Error('Unknown/missing option '+k);
    o[k.slice(2)]=args.shift();}
  if(!['send','receive','check'].includes(command)||!o.profile)throw Error('phy-cli.cjs check|send|receive --profile FILE --kind c0|c1|clock|pair|frame|i2c --run ID --directory NEW_DIR [--pair 00|01|10|11|all] [--ticks N] [--ack]');
  const profile=load(o.profile,{hardware:true});
  validateLab(profile,{frames:['pair','frame'].includes(o.kind)});
  if(command==='check'){console.log(JSON.stringify({status:'PROFILE_VALID',physical_status:'NOT_TESTED',profile},null,2));return;}
  const kind=o.kind||'frame',role=command==='send'?'tx':'rx',crc=o.crc||'SMBUS';
  if(o['data-hex']&&!/^[0-9a-f]{2}$/i.test(o['data-hex']))throw Error('DATA_HEX');
  if(role==='rx'&&['data-hex','pair','seq','sid'].some(k=>k in o))throw Error('RX_MUST_NOT_RECEIVE_EXPECTED_DATA');
  const plan=role==='tx'?makePlan({kind,pair:o.pair||'00',data:parseInt(o['data-hex']||'41',16),seq:Number(o.seq||0),sid:Number(o.sid||1),crc}):null;
  const ticks=plan?plan.ticks:Number(o.ticks||(kind==='frame'?87:kind==='pair'?3:kind==='i2c'?20:6));
  if(kind==='frame'&&ticks!==87)throw Error('FRAME_REQUIRES_87_TICKS');
  const config={role,kind,runId:o.run,ticks,plan,ack:!!o.ack,crc,timeout:Number(o.timeout||(o.ack?260:ticks+60))};
  if(!o.directory||!o.run)throw Error('RUN_AND_NEW_DIRECTORY_REQUIRED');
  const session=await launch({mode:'hardware',profileFile:o.profile,directory:o.directory,electricalChecked:true,crc,labDiagnostics:!['pair','frame'].includes(kind),
    firmware:o.firmware||path.join(__dirname,'native/build/runtime102-pru0.out'),host:o.host||path.join(__dirname,'native/build/runtime102-host'),
    python:process.env.TRAMA3_PYTHON||'python3',supervisorFactory:options=>new PhysicalTrial(options,config)});
  console.log('PHY '+role+' '+kind+' 1 Hz, C0/C1, C2 disconnected. Logs: '+o.directory);
  const stop=()=>session.stop();process.once('SIGINT',stop);process.once('SIGTERM',stop);
  let last=-1;
  const watch=setInterval(()=>{
    const s=session.supervisor,n=s.active?s.active.index:s.events.filter(e=>e.flags===2).length;
    if(n!==last){console.log('ticks='+n+' state='+s.state);last=n;}
    if(['STOPPED','CLEANUP_FAILED'].includes(s.state)){
      clearInterval(watch);process.removeListener('SIGINT',stop);process.removeListener('SIGTERM',stop);
      const lines=fs.readFileSync(path.join(o.directory,profile.board.slice(-1)+'.jsonl'),'utf8').trim().split('\n').map(JSON.parse);
      const end=lines.find(e=>e.kind==='SESSION_STOP');
      console.log(JSON.stringify({state:s.state,reason:end&&end.reason,errors:s.errors}));
      process.exitCode=s.state==='STOPPED'&&end&&end.reason==='PHY_COMPLETE'?0:1;
    }
  },250);
}
module.exports={main};
if(require.main===module)main().catch(e=>{console.error(e.stack);process.exitCode=1;});
