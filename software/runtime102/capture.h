/* Portable continuous capture core. Hardware adapter must call at bounded
 * intervals and enforce an independent watchdog; this is not deployed firmware. */
#ifndef R102_CAPTURE_H
#define R102_CAPTURE_H
#include <stdint.h>
#define R102_CAPACITY 256u
struct r102_event { uint32_t sequence,epoch,ticks_lo,ticks_hi,r31,normalized,flags; };
struct r102_capture {
 uint32_t producer,consumer,epoch,previous,sequence,old_clock,initialized;
 uint32_t fault,pending,invert,max_gap;
 uint64_t ticks,sample_at;
 struct r102_event events[R102_CAPACITY];
};
/* Single-thread model API. Shared-memory integration needs release/acquire
 * publication and ownership; these structs must NOT be mmap'ed as an ABI. */
void r102_init(struct r102_capture *,uint32_t,uint32_t,uint32_t);
int r102_step(struct r102_capture *,uint32_t,uint32_t,uint64_t);
int r102_pop(struct r102_capture *,struct r102_event *);
void r102_stop(struct r102_capture *);
#endif
