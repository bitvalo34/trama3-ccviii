#include "abi.h"
#include <assert.h>
#include <stdio.h>
static struct r102_shared m;static struct r102_service s;
int main(void){
 uint64_t t;unsigned count=0;uint32_t p;
 r102_boot(&m,&s,0);assert(m.bytes==9660);m.epoch=17;m.command=R102_START;
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
 for(t=2000;t<405000000&&m.state==R102_RUNNING;t+=1000){m.arm_heartbeat=(uint32_t)(t/10000000);r102_poll(&m,&s,(uint32_t)t,0);}
 assert(m.error==10&&!s.output); /* missing READY never emits CLK */
 r102_boot(&m,&s,0);m.epoch=19;m.command=R102_START;m.tx_id=2;count=0;p=0;
 for(t=0;t<18500000000ULL;t+=1000){
  m.arm_heartbeat=(uint32_t)(t/10000000);
  if(m.request_id){m.ready_index=m.request_index;m.ready_id=m.request_id;}
  r102_poll(&m,&s,(uint32_t)t,0);assert(m.state==R102_RUNNING);
  if(t<400000000ULL)assert(!s.output);
  if(t>=17800000000ULL&&t<18200000000ULL){assert(m.tx_body_done==2);assert(m.tx_done==0);}
  if(s.output&&!p)count++;
  p=s.output;
 }
 assert(count==87);assert(m.tx_done==2);assert(m.tx_body_done==2);assert(!s.output);
 /* A train of comparator pulses ends LOW at the nominal sample. */
 for(unsigned observe=0;observe<2;observe++){
  r102_boot(&m,&s,0);m.epoch=20;m.command=R102_START;
  m.acoustic_start=40000000;m.acoustic_end=160000000;m.acoustic_min=observe?0:30000000;m.acoustic_max_gap=20000;
  for(t=0;t<=160000000;t+=1000){
   uint32_t raw=t<40000000?1u<<15:0;
   if(t%200000<100000&&t<160000000)raw|=1u<<14;
   m.arm_heartbeat=(uint32_t)(t/10000000);r102_poll(&m,&s,(uint32_t)t,raw);
   assert(m.state==R102_RUNNING);
  }
  assert(m.producer==3);assert(m.events[2].acoustic_active==60000000);
  assert(m.events[2].acoustic_gap==1000);assert(!(m.events[2].r31&(1u<<14)));
  assert(((m.events[2].normalized>>1)&1)==!observe);
 }
 r102_boot(&m,&s,0);m.epoch=21;m.command=R102_START;m.tx_count=3;m.tx_id=1;count=0;p=0;
 for(t=0;t<1500000000;t+=1000){
  m.arm_heartbeat=(uint32_t)(t/10000000);
  if(m.request_id){m.ready_id=m.request_id;m.ready_index=m.request_index;}
  r102_poll(&m,&s,(uint32_t)t,0);assert(m.state==R102_RUNNING);
  if(s.output&&!p)count++;
  p=s.output;
 }
 assert(count==3&&m.tx_done==1);
 r102_boot(&m,&s,0);m.epoch=22;m.command=R102_START;r102_poll(&m,&s,0,0);
 m.producer=R102_N;r102_poll(&m,&s,1000,1u<<15);assert(m.error==1&&!s.output);
 r102_boot(&m,&s,0);m.epoch=23;m.command=R102_START;m.acoustic_start=0;m.acoustic_end=160000000;
 m.acoustic_max_gap=500;r102_poll(&m,&s,0,1u<<15);r102_poll(&m,&s,1000,1u<<15);assert(m.error==12);
 r102_boot(&m,&s,0);m.epoch=24;m.command=R102_START;r102_poll(&m,&s,0,0);
 r102_poll(&m,&s,20001,0);assert(m.error==3);
 r102_boot(&m,&s,0);m.epoch=25;m.command=R102_START;
 for(t=0;t<=100001000;t+=1000)r102_poll(&m,&s,(uint32_t)t,0);
 assert(m.error==5);
 puts("PASS ABI4, 90s RX/wraps, STOP, READY, 87/3 ticks and guard, pulsed acoustic/observe, overflow, poll gap, heartbeat");return 0;
}
