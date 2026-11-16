#ifndef R102_ACOUSTIC_WINDOW_H
#define R102_ACOUSTIC_WINDOW_H
#include <stdint.h>
/* Candidate helper, NOT linked into ABI3 service.c.
 * Relative IEP ticks from a logical clock rise. Caller supplies polarity-normalized
 * C1 on every poll. Integrate previous level on [last,t); clip to [start,end).
 * No defaults: calibration determines start/end/min_active/max_gap.
 * return -1 error, 0 collecting, 1 finished. Fault is sticky until init. */
struct r102_acoustic {
 uint32_t start,end,min_active,max_gap,last,level,active,closed,fault;
};
static int r102_acoustic_init(struct r102_acoustic *w,uint32_t start,
 uint32_t end,uint32_t min_active,uint32_t max_gap,uint32_t initial){
 w->fault=1;
 if(start>=end||end>160000000u||!min_active||min_active>end-start||
    !max_gap||max_gap>end-start||initial>1)return -1;
 w->start=start;w->end=end;w->min_active=min_active;w->max_gap=max_gap;
 w->last=0;w->level=initial;w->active=0;w->closed=0;w->fault=0;return 0;
}
static int r102_acoustic_feed(struct r102_acoustic *w,uint32_t t,uint32_t level){
 uint32_t lo,hi;
 if(w->fault||w->closed)return -1;
 if(t<w->last||t-w->last>w->max_gap||level>1){w->fault=1;return -1;}
 lo=w->last>w->start?w->last:w->start;hi=t<w->end?t:w->end;
 if(hi>lo&&w->level)w->active+=hi-lo;
 w->last=t;w->level=level;if(t>=w->end)w->closed=1;return w->closed?1:0;
}
static int r102_acoustic_result(const struct r102_acoustic *w){
 if(w->fault||!w->closed)return -1;
 return w->active>=w->min_active?1:0;
}
#endif
