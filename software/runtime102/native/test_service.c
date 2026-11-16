#include "abi.h"
#include <assert.h>
#include <stdio.h>
static struct r102_shared m;static struct r102_service s;
int main(void){
 uint64_t t;unsigned count=0;uint32_t p;
 r102_boot(&m,&s,0);assert(m.bytes==7592);m.epoch=17;m.command=R102_START;
 for(t=0;t<18000000000ULL;t+=1000){
  m.arm_heartbeat=(uint32_t)(t/10000000);p=m.producer;
  r102_poll(&m,&s,(uint32_t)t,t%200000000<40000000?1u<<15:0);
  assert(m.state==R102_RUNNING);
  count+=(uint32_t)(m.producer-p);m.consumer=m.producer;
 }
 assert(count==270);assert(s.now>4ULL*4294967296ULL);
 m.command=R102_STOP;r102_poll(&m,&s,(uint32_t)t,0);assert(m.state==R102_STOPPED&&!s.output);
 r102_boot(&m,&s,0);m.epoch=18;m.command=R102_START;r102_poll(&m,&s,0,0);
 m.tx_id=1;r102_poll(&m,&s,1000,0);
 for(t=2000;t<5000000&&m.state==R102_RUNNING;t+=1000)r102_poll(&m,&s,(uint32_t)t,0);
 assert(m.error==10&&!s.output); /* missing READY never emits CLK */
 r102_boot(&m,&s,0);m.epoch=19;m.command=R102_START;m.tx_id=2;count=0;p=0;
 for(t=0;t<18000000000ULL;t+=1000){
  m.arm_heartbeat=(uint32_t)(t/10000000);
  if(m.request_id){m.ready_index=m.request_index;m.ready_id=m.request_id;}
  r102_poll(&m,&s,(uint32_t)t,0);assert(m.state==R102_RUNNING);
  if(t>=17404000000ULL&&t<17804000000ULL){assert(m.tx_body_done==2);assert(m.tx_done==0);}
  if(s.output&&!p)count++;
  p=s.output;
 }
 assert(count==87);assert(m.tx_done==2);assert(m.tx_body_done==2);assert(!s.output);
 puts("PASS ABI, 90s RX/multiple wraps, STOP, missing READY, 87 TX ticks/guard");return 0;
}
