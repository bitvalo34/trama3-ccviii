'use strict';
const {Supervisor}=require('./supervisor.cjs');
const {plan}=require('./bench-core.cjs');
// Diagnostic session only: no Endpoint handshake, decoding, ACK or retry.
// RX never receives expected vectors. Compare independent logs offline.
class Bench extends Supervisor {
  constructor(options,{role,pattern,runId,timeout=180}){
    super({...options,coordinator:false});
    if(!['tx','rx'].includes(role)||!Number.isInteger(timeout)||timeout<100||timeout>600||
       !/^[-a-zA-Z0-9_]{1,64}$/.test(runId))throw Error('BENCH_CONFIGURATION');
    this.role=role;this.runId=runId;this.timeout=timeout;
    this.plan=role==='tx'?plan(pattern,runId,options.node):null;
    this.captureCount=0;this.sampleCount=0;
  }
  start(){
    if(this.state!=='NEW')throw Error('BENCH_STATE');
    this.state='RUNNING';this.deadline=this.clock()+this.timeout;
    try{
      this.journal.write({kind:'SESSION_START',t:this.clock()});
      this.journal.write({kind:'BENCH_START',role:this.role,run_id:this.runId,plan:this.plan,t:this.clock()});
      if(this.role==='tx'){
        this.active={id:1,vectors:this.plan.vectors,index:0,bodyEnd:null};
        this.bridge.write('TX 1 '+this.plan.vectors.join('')+'\n');
      }
    }catch(e){void this.stop(e.message);}
  }
  send(){throw Error('BENCH_NOT_CHAT');}
  pump(){
    if(this.state!=='RUNNING')return;
    if(this.preparing&&this.clock()>this.prepareDeadline){void this.stop('OUTPUT_PREPARE_TIMEOUT');return;}
    if(this.clock()>=this.deadline)void this.stop('BENCH_TIMEOUT');
  }
  record(r){
    if(this.state!=='RUNNING')return;
    if(r.kind==='event'){
      if(++this.captureCount>1024)throw Error('BENCH_CAPTURE_LIMIT');
      this.journal.write({...r,kind:'CAPTURE',t:this.clock()});
      if(this.role==='rx'&&r.flags===2&&++this.sampleCount===87){
        this.journal.write({kind:'BENCH_RECEIVED',samples:87,t:this.clock()});
        void this.stop('BENCH_COMPLETE');
      }
      return;
    }
    if(r.kind==='done'){
      if(this.role!=='tx'||!this.active||r.id!==1||this.active.index!==87||this.active.bodyEnd===null)
        throw Error('BENCH_DONE_ORDER');
      this.journal.write({kind:'BENCH_SENT',vectors:87,t:this.clock()});
      this.active=null;void this.stop('BENCH_COMPLETE');return;
    }
    super.record(r); // reuse READY only after IO completion and bounded prepare
  }
}
module.exports={Bench};
