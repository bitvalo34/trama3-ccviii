#include "abi.h"
#include <string.h>
#ifndef R102_BARRIER
#define R102_BARRIER() __sync_synchronize()
#endif
static void fault(volatile struct r102_shared *m,struct r102_service *s,uint32_t e){
 s->output=0;s->pending=0;s->active=0;m->error=e;R102_BARRIER();m->state=R102_FAULT;
}
void r102_boot(volatile struct r102_shared *m,struct r102_service *s,uint32_t low){
 memset(s,0,sizeof(*s));s->previous=low;
 m->magic=0;m->abi=R102_ABI;m->bytes=sizeof(*m);m->command=0;m->state=R102_IDLE;
 m->producer=0;m->consumer=0;m->error=0;m->tx_id=0;m->tx_done=0;m->tx_body_done=0;
 m->request_id=0;m->ready_id=0;m->pru_heartbeat=0;
 m->tx_count=87;m->acoustic_start=0;m->acoustic_end=0;m->acoustic_min=0;m->acoustic_max_gap=0;
 R102_BARRIER();m->magic=R102_MAGIC;
}
static int publish(volatile struct r102_shared *m,struct r102_service *s,uint32_t raw,uint32_t v,uint32_t flags){
 uint32_t p=m->producer,c=m->consumer;volatile struct r102_slot *e;
 R102_BARRIER();
 if((uint32_t)(p-c)>=R102_N){fault(m,s,1);return 0;}
 e=&m->events[p&(R102_N-1)];e->sequence=s->sequence++;e->epoch=s->epoch;
 e->ticks_lo=(uint32_t)s->now;e->ticks_hi=(uint32_t)(s->now>>32);
 e->r31=raw;e->normalized=v;e->flags=flags;
 e->acoustic_active=flags==2&&s->acoustic_end?s->acoustic.active:0;
 e->acoustic_gap=flags==2&&s->acoustic_end?s->acoustic_gap:0;
 R102_BARRIER();m->producer=p+1;return 1;
}
void r102_poll(volatile struct r102_shared *m,struct r102_service *s,uint32_t low,uint32_t raw){
 uint32_t delta=low-s->previous,v,clk,i,command=m->command;
 s->previous=low;s->now+=delta;m->pru_heartbeat++;
 if(command==R102_STOP){s->output=0;s->active=0;s->pending=0;m->command=0;R102_BARRIER();m->state=R102_STOPPED;return;}
 if(command==R102_START){
  m->command=0;
  /* Reload firmware to recover faults; never silently reuse an old epoch. */
  if(m->state!=R102_IDLE||!m->epoch||m->invert>15){fault(m,s,2);return;}
  R102_BARRIER();s->epoch=m->epoch;s->invert=m->invert;
  s->acoustic_start=m->acoustic_start;s->acoustic_end=m->acoustic_end;
  s->acoustic_min=m->acoustic_min;s->acoustic_max_gap=m->acoustic_max_gap;
  if(s->acoustic_end&&r102_acoustic_init(&s->acoustic,s->acoustic_start,s->acoustic_end,
      s->acoustic_min?s->acoustic_min:1,s->acoustic_max_gap,0)<0){fault(m,s,11);return;}
  s->heartbeat=m->arm_heartbeat;s->host_at=s->now;s->initial_guard_until=s->now+2ULL*R102_T;m->state=R102_RUNNING;
 }
 if(m->state!=R102_RUNNING)return;
 if(delta>20000u){fault(m,s,3);return;} /* max poll gap 100 us, to characterize */
 if(m->epoch!=s->epoch||m->invert!=s->invert||m->acoustic_start!=s->acoustic_start||
    m->acoustic_end!=s->acoustic_end||m->acoustic_min!=s->acoustic_min||
    m->acoustic_max_gap!=s->acoustic_max_gap){fault(m,s,4);return;}
 if(m->arm_heartbeat!=s->heartbeat){s->heartbeat=m->arm_heartbeat;s->host_at=s->now;}
 if(s->now-s->host_at>100000000u){fault(m,s,5);return;}
 v=(((raw>>5)&1)|(((raw>>14)&1)<<1)|(((raw>>16)&1)<<2)|(((raw>>15)&1)<<3))^s->invert;
 clk=(v>>3)&1;
 if(clk!=s->clock){
  if(clk){
   if(s->pending){fault(m,s,6);return;}s->sample_at=s->now+160000000u;s->pending=1;
   s->acoustic_at=s->now;s->acoustic_gap=0;
   if(s->acoustic_end&&r102_acoustic_init(&s->acoustic,s->acoustic_start,s->acoustic_end,
       s->acoustic_min?s->acoustic_min:1,s->acoustic_max_gap,(v>>1)&1)<0){fault(m,s,11);return;}
  }
  s->clock=clk;if(!publish(m,s,raw,v,1))return;
 }
 if(s->pending&&s->acoustic_end&&!s->acoustic.closed){
  uint32_t relative=(uint32_t)(s->now-s->acoustic_at),gap=relative-s->acoustic.last;
  if(gap>s->acoustic_gap)s->acoustic_gap=gap;
  if(r102_acoustic_feed(&s->acoustic,relative,(v>>1)&1)<0){fault(m,s,12);return;}
 }
 if(s->pending&&s->now>=s->sample_at){
  if(s->now-s->sample_at>2000u){fault(m,s,7);return;}
  if(s->acoustic_end){
   int decision=r102_acoustic_result(&s->acoustic);
   if(decision<0){fault(m,s,12);return;}
   if(s->acoustic_min)v=(v&~2u)|((uint32_t)decision<<1);
  }
  s->pending=0;if(!publish(m,s,raw,v,2))return;
 }
 if(!s->active&&m->tx_id!=m->tx_done){
  R102_BARRIER();s->count=m->tx_count;
  if(!s->count||s->count>87){fault(m,s,8);return;}
  for(i=0;i<s->count;i++)if(m->tx_rows[i]>7){fault(m,s,8);return;}
  s->active=m->tx_id;s->index=0;s->tx_at=s->now+R102_LEAD;
  if(s->tx_at<s->initial_guard_until)s->tx_at=s->initial_guard_until;
  m->request_index=0;R102_BARRIER();m->request_id=s->active;
 }
 if(!s->active)return;
 if(m->tx_id!=s->active||m->tx_count!=s->count){fault(m,s,9);return;}
 if(s->output&&s->now>=s->tx_fall)s->output=0;
 if(s->index<s->count&&s->now>=s->tx_at){
  R102_BARRIER();
  if(m->ready_id!=s->active||m->ready_index!=s->index||s->now-s->tx_at>2000u){fault(m,s,10);return;}
  s->output=R102_TX_MASK;s->tx_fall=s->tx_at+(s->index?40000000u:120000000u);
  s->index++;s->tx_at+=R102_T;
  if(s->index==s->count)s->tx_end=s->tx_at+2ULL*R102_T;
 }
 if(s->index<s->count&&s->now+R102_LEAD>=s->tx_at){
  m->request_index=s->index;R102_BARRIER();m->request_id=s->active;
 }
 if(s->index==s->count&&s->now>=s->tx_at){R102_BARRIER();m->tx_body_done=s->active;}
 if(s->index==s->count&&s->now>=s->tx_end){
  s->output=0;R102_BARRIER();m->tx_done=s->active;s->active=0;m->request_id=0;
 }
}
