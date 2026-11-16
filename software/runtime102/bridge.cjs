'use strict';
const {EventEmitter}=require('node:events');
// Wrap an already spawned, exclusively owned host process. No shell command,
// privilege escalation, firmware loading or pin changes are performed here.
class ProcessBridge extends EventEmitter {
  constructor(child){
    super();this.child=child;this.buffer='';this.closed=false;
    child.stdout.setEncoding('utf8');
    child.stdout.on('data',chunk=>{
      try{
        this.buffer+=chunk;
        if(this.buffer.length>65536)throw Error('BRIDGE_BUFFER_LIMIT');
        let end;while((end=this.buffer.indexOf('\n'))>=0){
          const line=this.buffer.slice(0,end);this.buffer=this.buffer.slice(end+1);
          if(line.length>4096)throw Error('BRIDGE_LINE_LIMIT');
          const record=JSON.parse(line);
          if(!record||typeof record!=='object'||Array.isArray(record))throw Error('BRIDGE_JSON');
          if(record.kind==='ready'){this.readyInfo=record;this.emit('ready',record);}
          else this.emit('record',record);
        }
      }catch(e){this.emit('failure',e);}
    });
    child.stderr.on('data',chunk=>this.emit('diagnostic',String(chunk).slice(0,4096)));
    child.on('error',e=>this.emit('failure',e));
    child.stdin.on('error',e=>this.emit('failure',e));
    child.on('exit',(code,signal)=>{this.closed=true;this.emit('exit',{code,signal});});
  }
  write(command){
    if(this.closed||this.child.stdin.destroyed)throw Error('BRIDGE_CLOSED');
    if(this.child.stdin.writableLength>8192)throw Error('BRIDGE_BACKPRESSURE');
    this.child.stdin.write(command);
  }
}
module.exports={ProcessBridge};
