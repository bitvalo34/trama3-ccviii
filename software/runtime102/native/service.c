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
 R102_BARRIER();m->magic=R102_MAGIC;
}
static int publish(volatile struct r102_shared *m,struct r102_service *s,uint32_t raw,uint32_t v,uint32_t flags){
 uint32_t p=m->producer,c=m->consumer;volatile struct r102_slot *e;
 R102_BARRIER();
 if((uint32_t)(p-c)>=R102_N){fault(m,s,1);return 0;}
 e=&m->events[p&(R102_N-1)];e->sequence=s->sequence++;e->epoch=s->epoch;
 e->ticks_lo=(uint32_t)s->now;e->ticks_hi=(uint32_t)(s->now>>32);
 e->r31=raw;e->normalized=v;e->flags=flags;R102_BARRIER();m->producer=p+1;return 1;
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
  s->heartbeat=m->arm_heartbeat;s->host_at=s->now;m->state=R102_RUNNING;
 }
 if(m->state!=R102_RUNNING)return;
 if(delta>20000u){fault(m,s,3);return;} /* max poll gap 100 us, to characterize */
 if(m->epoch!=s->epoch||m->invert!=s->invert){fault(m,s,4);return;}
 if(m->arm_heartbeat!=s->heartbeat){s->heartbeat=m->arm_heartbeat;s->host_at=s->now;}
 if(s->now-s->host_at>100000000u){fault(m,s,5);return;}
 v=(((raw>>5)&1)|(((raw>>14)&1)<<1)|(((raw>>16)&1)<<2)|(((raw>>15)&1)<<3))^s->invert;
 clk=(v>>3)&1;
 if(clk!=s->clock){
  if(clk){if(s->pending){fault(m,s,6);return;}s->sample_at=s->now+160000000u;s->pending=1;}
  s->clock=clk;if(!publish(m,s,raw,v,1))return;
 }
 if(s->pending&&s->now>=s->sample_at){
  if(s->now-s->sample_at>2000u){fault(m,s,7);return;}
  s->pending=0;if(!publish(m,s,raw,v,2))return;
 }
 if(!s->active&&m->tx_id!=m->tx_done){
  R102_BARRIER();for(i=0;i<87;i++)if(m->tx_rows[i]>7){fault(m,s,8);return;}
  s->active=m->tx_id;s->index=0;s->tx_at=s->now+R102_LEAD;
  m->request_index=0;R102_BARRIER();m->request_id=s->active;
 }
 if(!s->active)return;
 if(m->tx_id!=s->active){fault(m,s,9);return;}
 if(s->output&&s->now>=s->tx_fall)s->output=0;
 if(s->index<87&&s->now>=s->tx_at){
  R102_BARRIER();
  if(m->ready_id!=s->active||m->ready_index!=s->index||s->now-s->tx_at>2000u){fault(m,s,10);return;}
  s->output=R102_TX_MASK;s->tx_fall=s->tx_at+(s->index?40000000u:120000000u);
  s->index++;s->tx_at+=R102_T;
  if(s->index==87)s->tx_end=s->tx_at+2ULL*R102_T;
 }
 if(s->index<87&&s->now+R102_LEAD>=s->tx_at){
  m->request_index=s->index;R102_BARRIER();m->request_id=s->active;
 }
 if(s->index==87&&s->now>=s->tx_at){R102_BARRIER();m->tx_body_done=s->active;}
 if(s->index==87&&s->now>=s->tx_end){
  s->output=0;R102_BARRIER();m->tx_done=s->active;s->active=0;m->request_id=0;
 }
}
