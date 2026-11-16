'use strict';
const {EventEmitter}=require('node:events');
// Persistent worker: no Python launch per symbol, no shell interpolation.
class P2Adapter extends EventEmitter {
  constructor(child,{timeoutMs=1000}={}){
    super();Object.assign(this,{child,timeoutMs});this.next=1;this.pending=new Map();this.buffer='';this.closed=false;
    child.stdout.setEncoding('utf8');
    child.stdout.on('data',text=>{
      try{
        this.buffer+=text;if(this.buffer.length>8192)throw Error('P2_BUFFER_LIMIT');
        let i;while((i=this.buffer.indexOf('\n'))>=0){
          const r=JSON.parse(this.buffer.slice(0,i));this.buffer=this.buffer.slice(i+1);
          const p=this.pending.get(r.id);if(!p||typeof r.ok!=='boolean')throw Error('P2_RESPONSE');
          this.pending.delete(r.id);clearTimeout(p.timer);
          if(r.ok)p.resolve(r.data);else p.reject(Error(r.error||'P2_IO'));
        }
      }catch(e){this.fail(e);}
    });
    child.on('error',e=>this.fail(e));child.stdin.on('error',e=>this.fail(e));
    child.on('exit',()=>{this.closed=true;this.fail(Error('P2_EXIT'));});
  }
  fail(e){for(const p of this.pending.values()){clearTimeout(p.timer);p.reject(e);}this.pending.clear();this.emit('failure',e);}
  request(op,extra={}){
    if(this.closed)return Promise.reject(Error('P2_CLOSED'));
    if(this.pending.size&&op!=='shutdown')return Promise.reject(Error('P2_BUSY'));
    return new Promise((resolve,reject)=>{
      const id=this.next++;const timer=setTimeout(()=>{this.pending.delete(id);reject(Error('P2_TIMEOUT'));},this.timeoutMs);
      this.pending.set(id,{resolve,reject,timer});
      this.child.stdin.write(JSON.stringify({id,op,...extra})+'\n');
    });
  }
  initialize(){return this.request('initialize');}
  prepare(vector){return this.request('prepare',{vector});}
  shutdown(){if(!this.stopping)this.stopping=this.request('shutdown');return this.stopping;}
}
module.exports={P2Adapter};
