/* Ejecuta logica de firmware REAL con registros simulados; no prueba PRU ISA. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include <assert.h>
#include "../../hardware/pruebas/t06/firmware/abi.h"
uint32_t model_registers[0x30000/4];
volatile uint32_t __R30, __R31;
static jmp_buf done;
static unsigned scenario, steps, started, checks;
static volatile struct mailbox *box=(volatile struct mailbox *)&model_registers[0x10000/4];
void model_service(void) {
 if(started) {longjmp(done,1);}
 assert(box->magic==T06_MAGIC);
 box->period=4000000; box->high=300000;box->cycles=25;box->timeout=200000000;
 if(scenario==4) box->high=box->period; /* rechazar ancho invalido */
 box->command=scenario==1?CMD_RX:scenario==2?CMD_SNAPSHOT:CMD_LOOP;
 started=1;
}
void model_step(void) {
 uint32_t t;
 steps++;
 assert(steps<3000000);
 model_registers[0x2e00c/4]+=200; /* paso de modelo: 1 us */
 t=model_registers[0x2e00c/4];
 __R31=(scenario==1)?0:(__R30&T06_TX);
 if(scenario==2) __R31=(1u<<14)|(1u<<5);
 if(scenario==3 && steps==30000) box->command=CMD_STOP;
 if(scenario==5) __R31=(steps&1)?T06_RX:0; /* buffer overflow */
 if(scenario==6) model_registers[0x2e00c/4]+=4000; /* bucle demasiado lento */
 (void)t;
}
#define T06_MODEL
#define main firmware_main
#include "../../hardware/pruebas/t06/firmware/main.c"
#undef main
int main(void) {
 for(scenario=0;scenario<7;scenario++) {
  memset(model_registers,0,sizeof(model_registers));__R30=~0u;__R31=0;
  steps=0;started=0;
  if(setjmp(done)==0) firmware_main();
  assert((__R30&T06_TX)==0);checks++;
  if(scenario==0) {
   assert(box->state==DONE && box->generated==25 && box->count==50); checks++;
   assert(box->events[1].tick-box->events[0].tick==300000);checks++;
  }
  if(scenario==1){assert(box->state==DONE && box->count==0);checks++;}
  if(scenario==2){assert(box->state==DONE && box->count>0);assert(box->events[0].r31==((1u<<14)|(1u<<5)));checks++;}
  if(scenario==3){assert(box->state==STOPPED && box->generated<25);checks++;}
  if(scenario==4){assert(box->state==ERROR && box->generated==0);checks++;}
  if(scenario==5){assert(box->state==ERROR && box->overflow && box->count==T06_EVENTS);checks++;}
  if(scenario==6){assert(box->max_gap>2000);checks++;}
 }
 printf("PASS: %u comprobaciones, 7 escenarios de firmware SIMULADO. Sin evidencia fisica.\n",checks);
 return 0;
}
