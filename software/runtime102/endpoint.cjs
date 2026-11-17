'use strict';
const P = require('./protocol.cjs');
function fields(frame, bits) {
  return {
    type:frame.type, sid:frame.sid, seq:frame.seq, control:frame.ctrl, data:frame.data,
    crc:frame.crc, crc_calculated:frame.calculated, crc_algorithm:frame.algorithm,
    syn:bits.slice(0,12), sfd:bits.slice(12,18), length_bits:bits.length
  };
}
// One instance owns ONLY one node. No reference to the peer's expected sequence,
// original payload or fault mask. Times are monotonic seconds supplied by caller.
class Endpoint {
  constructor({id, coordinator=false, sid=1, crc='SMBUS', encoding='utf-8', log=()=>{}}) {
    if (!['A','B'].includes(id) || !Number.isInteger(sid) || sid<1 || sid>255 ||
        !P.CRCS[crc] || !['utf-8','windows-1252'].includes(encoding)) throw Error('configuration');
    Object.assign(this,{id,coordinator,sid,crc,encoding,log});
    this.state='IDLE'; this.now=0; this.nextId=1; this.pending=null;
    this.queue=[]; this.sending=null; this.deliveries=[]; this.rx=this.newRx();
    this.seq=0; this.specs=[]; this.index=0; this.txPeriod=1; this.rxPeriod=1;
    this.managementSeen=null; this.stats={retries:0,duplicates:0};
  }
  newRx(){return {expected:0,last:null,phase:'idle',bytes:[],lo:0,length:0};}
  time(t){if(!Number.isFinite(t)||t<this.now)throw Error('nonmonotonic time');this.now=t;}
  event(kind,extra={}){this.log({node:this.id,t:this.now,kind,...extra});}
  config(){return (Object.keys(P.CRCS).indexOf(this.crc)<<6)|(this.encoding==='windows-1252'?32:0)|6;}
  enqueue(f,priority=0,token=null){
    if(this.queue.length>=16){this.fail('QUEUE_OVERFLOW');return;}
    this.queue.push({id:this.nextId++,frame:f,priority,token,attempt:token===null?null:this.pending.attempts,
      notBefore:this.now+(priority===100?2.2*this.rxPeriod:0)});
  }
  request(f,expect,management=false){
    this.pending={frame:f,expect,management,attempts:0,deadline:null,token:this.nextId++};
    this.attempt();
  }
  attempt(trigger='initial'){
    const p=this.pending;if(!p)return;
    if(p.attempts===4){this.fail('ATTEMPTS_EXHAUSTED_DELIVERY_UNCERTAIN');return;}
    if(p.attempts)this.stats.retries++;
    p.attempts++;p.deadline=null;
    this.enqueue(p.frame,p.management?50:0,p.token);
    this.event('ATTEMPT',{direction:'tx',type:p.frame.type,sid:p.frame.sid,seq:p.frame.seq,
      attempt:p.attempts,trigger});
  }
  start(t=0){
    this.time(t);if(!this.coordinator||this.state!=='IDLE')throw Error('start state');
    this.state='HELLO';this.request(P.frame('HELLO',this.config(),0,this.sid),'HELLO_ACK',true);
  }
  send(text,t=this.now){
    this.time(t);if(this.state!=='CONNECTED'||this.specs.length||this.pending)throw Error('not ready');
    const bytes=P.encode(text,this.encoding);if(bytes.length>1024)throw Error('message too long');
    this.event('MESSAGE_STARTED',{direction:'tx',sid:this.sid,seq:this.seq,length_bytes:bytes.length});
    this.specs=[['START',0],['LEN_LO',bytes.length&255],['LEN_HI',bytes.length>>>8],
      ...bytes.map(b=>['DATA',b]),['END',0]];this.index=0;this.next();
  }
  next(){
    if(this.index===this.specs.length){this.specs=[];this.event('MESSAGE_CONFIRMED',
      {direction:'tx',sid:this.sid,seq:(this.seq+255)&255});return;}
    const [type,data]=this.specs[this.index];this.request(P.frame(type,data,this.seq,this.sid,this.crc),'ACK');
  }
  take(t){
    this.time(t);this.poll(t);
    if(this.sending||this.state==='FAULT')return null;
    this.queue.sort((a,b)=>b.priority-a.priority||a.id-b.id);
    const at=this.queue.findIndex(j=>j.notBefore<=t);if(at<0)return null;
    const job=this.queue.splice(at,1)[0];
    this.sending=job;
    job.started=t;
    this.event('TX_START',{direction:'tx',...fields(job.frame,job.frame.bits),id:job.id,attempt:job.attempt});
    return {...job,period:this.txPeriod,rows:P.rows(job.frame.bits)};
  }
  txDone(id,t,bodyEnd=t){
    if(!Number.isFinite(bodyEnd)||bodyEnd>t||bodyEnd<0)throw Error('invalid body end');
    this.time(t);if(!this.sending||this.sending.id!==id)throw Error('unknown transmission');
    const job=this.sending;this.sending=null;
    this.event('TX_DONE',{direction:'tx',...fields(job.frame,job.frame.bits),id,attempt:job.attempt,
      dispatch_t:job.started,body_end_t:bodyEnd,confirmation:job.token===null?'not_required':'waiting'});
    if(this.pending&&job.token===this.pending.token)
      this.pending.deadline=bodyEnd+(this.pending.management?200:P.ackTimeout(this.rxPeriod));
  }
  poll(t){
    this.time(t);
    const p=this.pending;
    if(p&&p.deadline!==null&&t>=p.deadline){
      this.event('TIMEOUT',{direction:'rx',type:p.frame.type,sid:p.frame.sid,seq:p.frame.seq,attempt:p.attempts});
      this.attempt('timeout');
    }
  }
  receive(bits,t){
    this.time(t);if(this.state==='FAULT')return;
    // Management always SMBUS, application negotiated CRC. Control is only used
    // to choose a parser; no action is taken before its CRC/SYN/SFD validation.
    const ctrl=typeof bits==='string'&&bits.length===54?parseInt(bits.slice(18,22),2):-1;
    const management=ctrl>=8&&ctrl<=11||ctrl===14||ctrl===15;
    const f=P.parse(bits,management?'SMBUS':this.crc);
    if(!f.ok){this.reject(f.reason,t,f.reason==='CRC'?{...fields(f,bits),crc_valid:false}:{});return;}
    this.event('RX_FRAME',{direction:'rx',...fields(f,bits),crc_valid:true,result:'OK'});
    if(f.type==='HELLO'&&!this.coordinator){
      if((f.data&7)!==6 || (f.data&24)!==0){this.enqueue(P.frame('ERROR',1,f.seq,f.sid),100);return;}
      if(this.managementSeen && this.managementSeen.sid===f.sid && this.managementSeen.config!==f.data)return;
      if(this.state!=='IDLE'&&f.sid!==this.sid){this.fail('PEER_RESET_DELIVERY_UNCERTAIN');return;}
      this.sid=f.sid;this.crc=Object.keys(P.CRCS)[f.data>>>6];
      this.encoding=f.data&32?'windows-1252':'utf-8';
      this.managementSeen={sid:f.sid,config:f.data};
      this.enqueue(P.frame('HELLO_ACK',f.data,f.seq,f.sid),100);return;
    }
    if(f.sid!==this.sid)return;
    if(f.type==='COMMIT'&&!this.coordinator&&this.managementSeen&&f.data===this.managementSeen.config){
      if(this.state!=='CONNECTED'){this.state='CONNECTED';this.event('CONNECTED');}
      this.enqueue(P.frame('READY',f.data,f.seq,f.sid),100);return;
    }
    const p=this.pending;
    if(p&&p.management&&f.type===p.expect&&f.seq===p.frame.seq&&f.data===p.frame.data){
      this.pending=null;
      if(this.state==='HELLO'){
        this.state='COMMIT';this.request(P.frame('COMMIT',this.config(),0,this.sid),'READY',true);
      }else if(this.state==='COMMIT'){this.state='CONNECTED';this.event('CONNECTED');}
      return;
    }
    if(this.state!=='CONNECTED')return;
    // Candidate rates need physical evidence. The first runtime explicitly rejects
    // rate negotiation; never silently acknowledge a profile it cannot execute.
    if(f.type==='RATE_CTRL'||f.type==='PERIOD_PART'){
      this.enqueue(P.frame('RATE_CTRL',P.RATE.REJECT,f.seq,f.sid),100);return;
    }
    if(f.type==='ACK'||f.type==='NACK'){
      if(!p||p.management||f.seq!==p.frame.seq)return;
      if(f.type==='ACK'&&f.data===p.frame.ctrl){
        this.event('ACK_ACCEPTED',{direction:'rx',type:'ACK',sid:f.sid,seq:f.seq,ack_for:p.frame.type,attempt:p.attempts});
        this.pending=null;this.seq=(this.seq+1)&255;this.index++;this.next();
      }else if(f.type==='NACK'&&f.data===1&&p.deadline!==null){
        this.event('NACK_ACCEPTED',{direction:'rx',type:'NACK',sid:f.sid,seq:f.seq,nack_for:p.frame.type,attempt:p.attempts});
        this.attempt('nack');
      }
      return;
    }
    const rx=this.rx,key=[f.ctrl,f.data,f.seq,f.sid].join('/');
    if(rx.last===key&&f.seq===((rx.expected+255)&255)){
      this.stats.duplicates++;this.event('DUPLICATE',{direction:'rx',type:f.type,sid:f.sid,seq:f.seq});
      this.enqueue(P.frame('ACK',f.ctrl,f.seq,f.sid,this.crc),100);return;
    }
    if(f.seq!==rx.expected)return;
    let valid=true;
    if(f.type==='START'&&rx.phase==='idle'){rx.phase='lo';rx.bytes=[];}
    else if(f.type==='LEN_LO'&&rx.phase==='lo'){rx.lo=f.data;rx.phase='hi';}
    else if(f.type==='LEN_HI'&&rx.phase==='hi'&&((f.data<<8)|rx.lo)<=1024){rx.length=(f.data<<8)|rx.lo;rx.phase='body';}
    else if(f.type==='DATA'&&rx.phase==='body'&&rx.bytes.length<rx.length)rx.bytes.push(f.data);
    else if(f.type==='END'&&rx.phase==='body'&&rx.bytes.length===rx.length){
      try{const text=P.decode(rx.bytes,this.encoding);this.deliveries.push(text);rx.phase='idle';
        this.event('DELIVERY',{direction:'rx',type:'END',text,sid:f.sid,seq:f.seq,length_bytes:rx.length});}
      catch(_){valid=false;}
    }else valid=false;
    if(!valid){this.event('RX_REJECT',{direction:'rx',type:f.type,sid:f.sid,seq:f.seq,reason:'CONTEXT'});return;}
    rx.last=key;rx.expected=(rx.expected+1)&255;
    this.enqueue(P.frame('ACK',f.ctrl,f.seq,f.sid,this.crc),100);
  }
  reject(reason,t=this.now,observation={}){
    this.time(t);this.event('RX_REJECT',{direction:'rx',...observation,reason});
    // Never derive response identity from corrupt header. Only established
    // message context supplies SID and expected sequence. Loss of clock is silent.
    if(this.state==='CONNECTED'&&this.rx.phase!=='idle'&&['CRC','MATRIX_SYNDROME','MATRIX_RANK'].includes(reason)){
      this.enqueue(P.frame('NACK',1,this.rx.expected,this.sid,this.crc),100);
      this.event('NACK_CONTEXT',{direction:'tx',type:'NACK',seq:this.rx.expected,sid:this.sid});
    }
  }
  fail(reason){this.state='FAULT';this.pending=null;this.queue=[];this.event('FAULT',{reason});}
}
module.exports={Endpoint};
