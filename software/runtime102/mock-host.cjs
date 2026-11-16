'use strict';
// Process boundary fixture only. Does not synthesize a peer or successful TX.
const readline=require('node:readline');
if(process.argv.includes('--fail-start'))process.exit(7);
if(!process.argv.includes('--silent'))console.log(JSON.stringify({kind:'ready',abi:process.argv.includes('--wrong-abi')?2:3,epoch:Number(process.argv[2])}));
const input=readline.createInterface({input:process.stdin});
input.on('line',line=>{
  if(line==='STOP'){input.close();process.exit(0);}
  if(line.startsWith('TX ')){console.error('Mock launch fixture has no physical peer');process.exit(8);}
});
input.on('close',()=>process.exit(0));
