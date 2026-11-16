#include "acoustic_window.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 struct r102_acoustic w;unsigned t;
 assert(r102_acoustic_init(&w,20,80,15,10,0)==0);
 for(t=10;t<=80;t+=10)assert(r102_acoustic_feed(&w,t,t>=30&&t<50?1:0)>=0);
 assert(w.active==20&&r102_acoustic_result(&w)==1);
 assert(r102_acoustic_init(&w,20,80,15,10,0)==0);
 for(t=10;t<=80;t+=10)assert(r102_acoustic_feed(&w,t,t==30?1:0)>=0);
 assert(w.active==10&&r102_acoustic_result(&w)==0);
 assert(r102_acoustic_init(&w,20,80,15,10,1)==0);
 assert(r102_acoustic_result(&w)==-1);
 assert(r102_acoustic_feed(&w,11,1)==-1);
 assert(r102_acoustic_result(&w)==-1);
 assert(r102_acoustic_init(&w,20,80,0,10,0)==-1);
 puts("PASS candidate acoustic helper (synthetic ticks; not physical)");
 return 0;
}
