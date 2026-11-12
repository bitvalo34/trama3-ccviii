/* Solo invocado por run.py tras validar identidad, exclusividad y firmware.
 * /dev/mem se limita a 12 KiB de SRAM compartida PRUSS del AM335x.
 * No cambia permisos de /dev/mem ni registros de arranque. */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#include <signal.h>
#include <time.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include "../firmware/abi.h"
static volatile sig_atomic_t interrupted;
static void sig(int n) { (void)n; interrupted=1; }
static double seconds(void) {
 struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t);
 return t.tv_sec+t.tv_nsec/1e9;
}
static void nap(void) { struct timespec t={0,10000000}; nanosleep(&t,NULL); }
static uint32_t number(const char *s) {
 char *end; unsigned long v; errno=0; v=strtoul(s,&end,10);
 if(errno || !*s || *end || *s=='-' || v>2000000000ul) { fprintf(stderr,"Numero invalido\n"); exit(2); }
 return (uint32_t)v;
}
int main(int argc,char **argv) {
 volatile struct mailbox *m; int fd, rc=0; uint32_t i, hb, mode;
 double deadline;
 if(argc!=2 && argc!=7) { fprintf(stderr,"Uso interno: host probe|stop|status; host run modo periodo_us alto_us ciclos timeout_ms\n"); return 2; }
 fd=open("/dev/mem",O_RDWR|O_SYNC);
 if(fd<0) { perror("/dev/mem"); return 4; }
 m=mmap(NULL,12288,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0x4a310000);
 close(fd); if(m==MAP_FAILED) {perror("mmap");return 4;}
 if(m->magic!=T06_MAGIC || m->abi!=T06_ABI) {fprintf(stderr,"ABI/firmware incompatible\n");rc=4;goto finish;}
 if(!strcmp(argv[1],"probe")) {
  hb=m->heartbeat; deadline=seconds()+1;
  while(m->heartbeat==hb && seconds()<deadline) nap();
  rc=(m->heartbeat==hb || m->state!=READY)?4:0;
  printf("{\"ready\":%s,\"abi\":%u}\n",rc?"false":"true",m->abi);
 } else if(!strcmp(argv[1],"stop")) {
  m->command=CMD_STOP; __sync_synchronize(); deadline=seconds()+1;
  while(m->state!=STOPPED && seconds()<deadline) nap();
  rc=m->state==STOPPED?0:5;
 } else if(!strcmp(argv[1],"status")) {
  printf("{\"state\":%u,\"count\":%u,\"generated\":%u}\n",m->state,m->count,m->generated);
 } else if(!strcmp(argv[1],"run") && argc==7) {
  uint32_t p=number(argv[3]),h=number(argv[4]),n=number(argv[5]),ms=number(argv[6]);
  mode=number(argv[2]);
  if(mode<1 || mode>4 || p<1000 || p>100000 || h<100 || h>=p ||
     n<2 || n>200 || ms<1 || ms>10000 ||
     ((mode==1 || mode==3) && (uint64_t)p*(n+1)>((uint64_t)ms*1000))) {rc=2;goto finish;}
  if(m->state!=READY) {rc=4;goto finish;}
  signal(SIGINT,sig); signal(SIGTERM,sig); signal(SIGHUP,sig);
  m->period=p*200; m->high=h*200; m->cycles=n; m->timeout=ms*200000;
  __sync_synchronize(); m->command=mode; __sync_synchronize();
  deadline=seconds()+ms/1000.0+2;
  while(seconds()<deadline) {
   uint32_t state=m->state;
   if(interrupted) {m->command=CMD_STOP;__sync_synchronize();}
   if(state==DONE || state==ERROR || state==STOPPED) break;
   nap();
  }
  __sync_synchronize();
  if(m->state!=DONE) rc=5;
  if(m->state!=DONE && m->state!=ERROR && m->state!=STOPPED) {
   m->command=CMD_STOP;__sync_synchronize();nap();
   fprintf(stderr,"Timeout host; detener remoteproc\n");rc=5;
  }
  printf("{\"state\":%u,\"mode\":%u,\"initial\":%u,\"generated\":%u,\"overflow\":%u,\"late\":%u,\"elapsed_ticks\":%u,\"max_gap_ticks\":%u,\"events\":[",
   m->state,m->mode,m->initial,m->generated,m->overflow,m->late,m->elapsed,m->max_gap);
  for(i=0;i<m->count && i<T06_EVENTS;i++)
   printf("%s[%u,%u]",i?",":"",m->events[i].tick,m->events[i].r31);
  puts("]}");
 } else rc=2;
finish: munmap((void *)m,12288);return rc;
}
