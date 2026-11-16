#include "capture.h"
#include <assert.h>
#include <stdio.h>
static struct r102_capture c;
int main(void){
 uint64_t t;unsigned count=0;struct r102_event e;
 r102_init(&c,7,0,200000);
 /* 100 seconds, several IEP wraps, 1 Hz input. */
 for(t=0;t<20000000000ULL;t+=200000){
  uint32_t raw=(t%200000000ULL<40000000ULL)?(1u<<15):0;
  assert(r102_step(&c,(uint32_t)t,raw,1000000));
  while(r102_pop(&c,&e)){assert(e.epoch==7);assert(e.sequence==count++);}
 }
 assert(count==300);assert(c.ticks>4ULL*4294967296ULL);
 r102_stop(&c);assert(!r102_step(&c,0,0,0));
 r102_init(&c,8,0,200000);assert(r102_step(&c,0,0,0));
 assert(!r102_step(&c,0,0,21474836480ULL));assert(c.fault==3);
 r102_init(&c,9,0,200000);
 for(t=0;t<20000000000ULL&&!c.fault;t+=200000)
  r102_step(&c,(uint32_t)t,t%200000000ULL<40000000ULL?1u<<15:0,1000000);
 assert(c.fault==2);assert(c.producer==256); /* no overwrite */
 puts("PASS: continuous 100s, wraps, stop, watchdog and overflow");return 0;
}
