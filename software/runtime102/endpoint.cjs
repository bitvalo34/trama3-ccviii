'use strict';
const P = require('./protocol.cjs');
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
    this.queue.push({id:this.nextId++,frame:f,priority,token,notBefore:this.now+(priority===100?2.2*this.rxPeriod:0)});
  }
  request(f,expect,management=false){
    this.pending={frame:f,expect,management,attempts:0,deadline:null,token:this.nextId++};
    this.attempt();
  }
  attempt(){
    const p=this.pending;if(!p)return;
    if(p.attempts===4){this.fail('ATTEMPTS_EXHAUSTED_DELIVERY_UNCERTAIN');return;}
    if(p.attempts)this.stats.retries++;
    p.attempts++;p.deadline=null;
    this.enqueue(p.frame,p.management?50:0,p.token);
    this.event('ATTEMPT',{type:p.frame.type,seq:p.frame.seq,attempt:p.attempts});
  }
  start(t=0){
    this.time(t);if(!this.coordinator||this.state!=='IDLE')throw Error('start state');
    this.state='HELLO';this.request(P.frame('HELLO',this.config(),0,this.sid),'HELLO_ACK',true);
  }
  send(text,t=this.now){
    this.time(t);if(this.state!=='CONNECTED'||this.specs.length||this.pending)throw Error('not ready');
    const bytes=P.encode(text,this.encoding);if(bytes.length>1024)throw Error('message too long');
    this.specs=[['START',0],['LEN_LO',bytes.length&255],['LEN_HI',bytes.length>>>8],
      ...bytes.map(b=>['DATA',b]),['END',0]];this.index=0;this.next();
  }
  next(){
    if(this.index===this.specs.length){this.specs=[];this.event('MESSAGE_CONFIRMED');return;}
    const [type,data]=this.specs[this.index];this.request(P.frame(type,data,this.seq,this.sid,this.crc),'ACK');
  }
  take(t){
    this.time(t);this.poll(t);
    if(this.sending||this.state==='FAULT')return null;
    this.queue.sort((a,b)=>b.priority-a.priority||a.id-b.id);
    const at=this.queue.findIndex(j=>j.notBefore<=t);if(at<0)return null;
    const job=this.queue.splice(at,1)[0];
    this.sending=job;return {...job,period:this.txPeriod,rows:P.rows(job.frame.bits)};
  }
  txDone(id,t,bodyEnd=t){
    if(!Number.isFinite(bodyEnd)||bodyEnd>t||bodyEnd<0)throw Error('invalid body end');
    this.time(t);if(!this.sending||this.sending.id!==id)throw Error('unknown transmission');
    const job=this.sending;this.sending=null;
    this.event('TX_DONE',{type:job.frame.type,seq:job.frame.seq,sid:job.frame.sid,crc:job.frame.crc});
    if(this.pending&&job.token===this.pending.token)
      this.pending.deadline=bodyEnd+(this.pending.management?200:P.ackTimeout(this.rxPeriod));
  }
  poll(t){this.time(t);if(this.pending&&this.pending.deadline!==null&&t>=this.pending.deadline)this.attempt();}
  receive(bits,t){
    this.time(t);if(this.state==='FAULT')return;
    // Management always SMBUS, application negotiated CRC. Control is only used
    // to choose a parser; no action is taken before its CRC/SYN/SFD validation.
    const ctrl=typeof bits==='string'&&bits.length===54?parseInt(bits.slice(18,22),2):-1;
    const management=ctrl>=8&&ctrl<=11||ctrl===14||ctrl===15;
    const f=P.parse(bits,management?'SMBUS':this.crc);
    if(!f.ok){this.reject(f.reason,t);return;}
    this.event('RX_FRAME',{type:f.type,seq:f.seq,sid:f.sid,crc:f.crc,crc_valid:true});
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
      this.state='CONNECTED';this.enqueue(P.frame('READY',f.data,f.seq,f.sid),100);return;
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
        this.event('ACK_ACCEPTED',{seq:f.seq});
        this.pending=null;this.seq=(this.seq+1)&255;this.index++;this.next();
      }else if(f.type==='NACK'&&f.data===1&&p.deadline!==null){
        this.event('NACK_ACCEPTED',{seq:f.seq});this.attempt();
      }
      return;
    }
    const rx=this.rx,key=[f.ctrl,f.data,f.seq,f.sid].join('/');
    if(rx.last===key&&f.seq===((rx.expected+255)&255)){
      this.stats.duplicates++;this.enqueue(P.frame('ACK',f.ctrl,f.seq,f.sid,this.crc),100);return;
    }
    if(f.seq!==rx.expected)return;
    let valid=true;
    if(f.type==='START'&&rx.phase==='idle'){rx.phase='lo';rx.bytes=[];}
    else if(f.type==='LEN_LO'&&rx.phase==='lo'){rx.lo=f.data;rx.phase='hi';}
    else if(f.type==='LEN_HI'&&rx.phase==='hi'&&((f.data<<8)|rx.lo)<=1024){rx.length=(f.data<<8)|rx.lo;rx.phase='body';}
    else if(f.type==='DATA'&&rx.phase==='body'&&rx.bytes.length<rx.length)rx.bytes.push(f.data);
    else if(f.type==='END'&&rx.phase==='body'&&rx.bytes.length===rx.length){
      try{const text=P.decode(rx.bytes,this.encoding);this.deliveries.push(text);rx.phase='idle';this.event('DELIVERY',{text});}
      catch(_){valid=false;}
    }else valid=false;
    if(!valid){this.event('RX_REJECT',{reason:'CONTEXT'});return;}
    rx.last=key;rx.expected=(rx.expected+1)&255;
    this.enqueue(P.frame('ACK',f.ctrl,f.seq,f.sid,this.crc),100);
  }
  reject(reason,t=this.now){
    this.time(t);this.event('RX_REJECT',{reason});
    // Never derive response identity from corrupt header. Only established
    // message context supplies SID and expected sequence. Loss of clock is silent.
    if(this.state==='CONNECTED'&&this.rx.phase!=='idle'&&['CRC','MATRIX_SYNDROME','MATRIX_RANK'].includes(reason)){
      this.enqueue(P.frame('NACK',1,this.rx.expected,this.sid,this.crc),100);
      this.event('NACK_CONTEXT',{seq:this.rx.expected,sid:this.sid});
    }
  }
  fail(reason){this.state='FAULT';this.pending=null;this.queue=[];this.event('FAULT',{reason});}
}
module.exports={Endpoint};
