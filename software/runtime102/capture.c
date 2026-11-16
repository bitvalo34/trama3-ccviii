#include "capture.h"
#include <string.h>
void r102_init(struct r102_capture *c,uint32_t epoch,uint32_t invert,uint32_t gap){
 memset(c,0,sizeof(*c));c->epoch=epoch;c->invert=invert;c->max_gap=gap;
 if(invert>15||!gap||gap>200000u)c->fault=1;
}
static int push(struct r102_capture *c,uint32_t raw,uint32_t v,uint32_t flag){
 struct r102_event *e;
 if((uint32_t)(c->producer-c->consumer)>=R102_CAPACITY){c->fault=2;return 0;}
 e=&c->events[c->producer&(R102_CAPACITY-1)];
 e->sequence=c->sequence++;e->epoch=c->epoch;e->ticks_lo=(uint32_t)c->ticks;
 e->ticks_hi=(uint32_t)(c->ticks>>32);e->r31=raw;e->normalized=v;e->flags=flag;
 c->producer++;return 1;
}
int r102_step(struct r102_capture *c,uint32_t low,uint32_t raw,uint64_t elapsed_ns){
 uint32_t delta,v,clock;
 if(c->fault)return 0;
 /* elapsed_ns must come from independent watchdog supervision, not low-low. */
 if(elapsed_ns>=21474836480ULL){c->fault=3;return 0;}
 if(!c->initialized){c->ticks=low;c->previous=low;c->initialized=1;}
 delta=low-c->previous;
 if(delta>c->max_gap){c->fault=4;return 0;}
 c->previous=low;c->ticks+=delta;
 v=(((raw>>5)&1)|(((raw>>14)&1)<<1)|(((raw>>16)&1)<<2)|(((raw>>15)&1)<<3))^c->invert;
 clock=(v>>3)&1;
 if(clock!=c->old_clock){
  if(clock){
   if(c->pending){c->fault=5;return 0;}
   c->sample_at=c->ticks+160000000ULL;c->pending=1;
  }
  c->old_clock=clock;if(!push(c,raw,v,1))return 0;
 }
 if(c->pending&&c->ticks>=c->sample_at){
  if(c->ticks-c->sample_at>2000u){c->fault=6;return 0;}
  c->pending=0;if(!push(c,raw,v,2))return 0;
 }
 return 1;
}
int r102_pop(struct r102_capture *c,struct r102_event *e){
 if(c->consumer==c->producer)return 0;
 *e=c->events[c->consumer&(R102_CAPACITY-1)];c->consumer++;return 1;
}
void r102_stop(struct r102_capture *c){c->pending=0;c->fault=7;}
