/* Experimental PRU0 adapter. Build-only until resource ownership and fixtures
 * are checked by the operator. Never run concurrently with T06 or IEP owners. */
#include "abi.h"
volatile register uint32_t __R30;
volatile register uint32_t __R31;
/* PRU shared SRAM volatile stores are ordered in the generated instruction
 * stream. Review TI assembly before deployment; this is NOT an ARM barrier. */
#define R102_BARRIER() __asm(" NOP")
#include "service.c"
#define REG(a) (*(volatile uint32_t *)(a))
#pragma DATA_SECTION(resource_table, ".resource_table")
#pragma RETAIN(resource_table)
const uint32_t resource_table[4]={1,0,0,0};
static struct r102_service service;
void main(void){
 volatile struct r102_shared *m=(volatile struct r102_shared *)0x10000;
 uint32_t low,raw;
 __R30&=~R102_TX_MASK;
 REG(0x26004)&=~(1u<<4);REG(0x26008)=0;REG(0x26030)|=1u;
 REG(0x2e000)=0;REG(0x2e008)=0;REG(0x2e040)=0;REG(0x2e00c)=0;REG(0x2e000)=0x11;
 r102_boot(m,&service,REG(0x2e00c));
 for(;;){
  low=REG(0x2e00c);raw=__R31; /* exactly one input register snapshot */
  r102_poll(m,&service,low,raw);
  __R30=(__R30&~R102_TX_MASK)|service.output;
 }
}
