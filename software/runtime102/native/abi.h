#ifndef R102_ABI_H
#define R102_ABI_H
#include <stdint.h>
#define R102_MAGIC 0x52313032u
#define R102_ABI 3u
#define R102_N 256u
#define R102_T 200000000u
#define R102_LEAD 4000000u
#define R102_TX_MASK (1u<<15)
enum { R102_IDLE=1, R102_RUNNING=2, R102_STOPPED=3, R102_FAULT=4 };
enum { R102_NONE=0, R102_START=1, R102_STOP=2 };
struct r102_slot { uint32_t sequence,epoch,ticks_lo,ticks_hi,r31,normalized,flags; };
/* Fixed uint32 fields, no pointer/enum/bool ABI. All timestamps in 200 MHz ticks.
 * ARM owns command, epoch, invert, arm_heartbeat, consumer, tx_id/rows, ready_id/index.
 * PRU owns other fields. tx_rows frozen until tx_done==tx_id or terminal fault.
 * Publication: data, release barrier, producer/tx_id/ready_id. Consumer acquire.
 * Different magic from the earlier proposal in hardware/pruebas/interfaces. */
struct r102_shared {
 uint32_t magic,abi,bytes,state,command,epoch,invert,arm_heartbeat;
 uint32_t pru_heartbeat,producer,consumer,error;
 uint32_t tx_id,tx_done,request_id,request_index,ready_id,ready_index,tx_body_done;
 uint32_t tx_rows[87];
 struct r102_slot events[R102_N];
};
typedef char r102_slot_size[(sizeof(struct r102_slot)==28)?1:-1];
typedef char r102_shm_size[(sizeof(struct r102_shared)==7592)?1:-1];
struct r102_service {
 uint64_t now,sample_at,host_at,tx_at,tx_fall,tx_end;
 uint32_t previous,sequence,clock,pending,heartbeat,active,index,output;
 uint32_t epoch,invert;
};
void r102_boot(volatile struct r102_shared *,struct r102_service *,uint32_t);
void r102_poll(volatile struct r102_shared *,struct r102_service *,uint32_t,uint32_t);
#endif
