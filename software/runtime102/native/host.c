#define _POSIX_C_SOURCE 200809L
#include "abi.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/select.h>
#include <time.h>
#include <signal.h>
#include <string.h>
static volatile sig_atomic_t stopping;
static void stop_signal(int n){(void)n;stopping=1;}
static double clock_now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+t.tv_nsec/1e9;}
/* Internal bridge. Does NOT load firmware, select pins or authorize P2.
 * stdin: TX <id> <87 digits 0..7>, READY <id> <index>, STOP.
 * stdout JSONL: requests, events, done. Failure requires supervisor cleanup. */
int main(int argc,char **argv){
 int fd,rc=1,announced=0;volatile struct r102_shared *m;uint32_t id=0,index=~0u,done=0,body=0,epoch;
 char line[256],op[16],rows[88],input[256];unsigned a,b,i,used=0;int nread,k;double last,until,pru_seen;uint32_t pru_hb;
 if(argc!=3&&argc!=7){fprintf(stderr,"Internal use: host epoch invert_mask [window_start end min_active max_gap]\n");return 2;}
 epoch=(uint32_t)strtoul(argv[1],NULL,10);a=(unsigned)strtoul(argv[2],NULL,10);
 if(!epoch||a>15)return 2;
 fd=open("/dev/mem",O_RDWR|O_SYNC);if(fd<0){perror("/dev/mem");return 2;}
 m=mmap(NULL,12288,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0x4a310000);close(fd);
 if(m==MAP_FAILED)return 2;
 if(m->magic!=R102_MAGIC||m->abi!=R102_ABI||m->bytes!=sizeof(*m)||m->state!=R102_IDLE)goto finish;
 setvbuf(stdout,NULL,_IOLBF,0);signal(SIGINT,stop_signal);signal(SIGTERM,stop_signal);
 m->epoch=epoch;m->invert=a;m->arm_heartbeat=1;
 if(argc==7){m->acoustic_start=(uint32_t)strtoul(argv[3],NULL,10);m->acoustic_end=(uint32_t)strtoul(argv[4],NULL,10);
  m->acoustic_min=(uint32_t)strtoul(argv[5],NULL,10);m->acoustic_max_gap=(uint32_t)strtoul(argv[6],NULL,10);}
 __sync_synchronize();m->command=R102_START;
 last=clock_now();until=last+1;pru_seen=last;pru_hb=m->pru_heartbeat;
 while(!stopping){
  fd_set set;struct timeval wait={0,1000};double now=clock_now();
  if(now-last>0.5){fprintf(stderr,"Host deadline missed\n");break;}
  last=now;m->arm_heartbeat++;__sync_synchronize();
  if(m->pru_heartbeat!=pru_hb){pru_hb=m->pru_heartbeat;pru_seen=now;}
  if(now-pru_seen>0.5){fprintf(stderr,"PRU heartbeat expired\n");break;}
  if(m->state==R102_FAULT){fprintf(stderr,"PRU fault %u\n",m->error);break;}
  if(m->state==R102_IDLE&&now>until)break;
  if(m->state==R102_RUNNING&&!announced){announced=1;printf("{\"kind\":\"ready\",\"abi\":%u,\"epoch\":%u}\n",R102_ABI,epoch);}
  while(m->consumer!=m->producer){
   uint32_t c=m->consumer,p=m->producer;struct r102_slot e;
   if((uint32_t)(p-c)>R102_N){stopping=1;break;}
   __sync_synchronize();e=m->events[c&(R102_N-1)];__sync_synchronize();m->consumer=c+1;
   printf("{\"kind\":\"event\",\"sequence\":%u,\"epoch\":%u,\"ticks_lo\":%u,\"ticks_hi\":%u,\"r31\":%u,\"normalized\":%u,\"flags\":%u,\"acoustic_active\":%u,\"acoustic_gap\":%u}\n",e.sequence,e.epoch,e.ticks_lo,e.ticks_hi,e.r31,e.normalized,e.flags,e.acoustic_active,e.acoustic_gap);
  }
  if(m->request_id&&(id!=m->request_id||index!=m->request_index)){
   id=m->request_id;index=m->request_index;__sync_synchronize();
   if(index>=87){stopping=1;break;}
   printf("{\"kind\":\"prepare\",\"id\":%u,\"index\":%u,\"vector\":%u}\n",id,index,m->tx_rows[index]);
  }
  if(body!=m->tx_body_done){body=m->tx_body_done;printf("{\"kind\":\"body_done\",\"id\":%u}\n",body);}
  if(done!=m->tx_done){done=m->tx_done;printf("{\"kind\":\"done\",\"id\":%u}\n",done);}
  FD_ZERO(&set);FD_SET(STDIN_FILENO,&set);
  if(select(1,&set,NULL,NULL,&wait)>0){
   /* Drain the available bytes in one read; fragmented commands never block. */
   nread=(int)read(STDIN_FILENO,input,sizeof(input));
   if(nread<=0){stopping=1;break;}
   for(k=0;k<nread&&!stopping;k++){
   char byte=input[k];
   if(byte!='\n'){
    if(used>=sizeof(line)-1){stopping=1;break;}
    line[used++]=byte;continue;
   }
   line[used]=0;used=0;
   if(sscanf(line,"%15s",op)!=1)continue;
   if(strcmp(line,"STOP")==0){stopping=1;rc=0;break;}
   if(sscanf(line,"READY %u %u",&a,&b)==2){
    if(a!=m->request_id||b!=m->request_index){stopping=1;break;}
    m->ready_id=0;__sync_synchronize();m->ready_index=b;__sync_synchronize();m->ready_id=a;
   }else if(sscanf(line,"TX %u %87s",&a,rows)==2){
    if(!a||a==m->tx_done||m->tx_id!=m->tx_done){stopping=1;break;}
    b=(unsigned)strlen(rows);
    for(i=0;i<b;i++)if(rows[i]<'0'||rows[i]>'7')break;
    if(!b||i!=b){stopping=1;break;}
    for(i=0;i<b;i++)m->tx_rows[i]=(uint32_t)(rows[i]-'0');
    m->tx_count=b;
    __sync_synchronize();m->tx_id=a;
   }else {stopping=1;break;}
   }
  }
 }
 m->command=R102_STOP;__sync_synchronize();until=clock_now()+1;
 while(m->state!=R102_STOPPED&&clock_now()<until){struct timespec n={0,1000000};nanosleep(&n,NULL);}
 if(m->state!=R102_STOPPED)rc=1;
finish:munmap((void *)m,12288);return rc;
}
