#ifndef TRAMA3_ABI_H
#define TRAMA3_ABI_H
#include <stdint.h>
#define T06_MAGIC 0x54303632u
#define T06_ABI 1u
#define T06_EVENTS 1024u
#define T06_HZ 200000000u
#define T06_TX (1u << 15)
#define T06_RX (1u << 15)
#define T06_INPUTS ((1u<<15)|(1u<<14)|(1u<<16)|(1u<<5))
enum { READY=1, RUNNING=2, DONE=3, ERROR=4, STOPPED=5 };
enum { CMD_NONE=0, CMD_TX=1, CMD_RX=2, CMD_LOOP=3, CMD_SNAPSHOT=4, CMD_STOP=9 };
struct event { uint32_t tick, r31; };
/* ARM publica command al final; PRU publica state al final del resultado.
 * Datos solo se leen tras DONE/ERROR/STOPPED; no hay consumidor concurrente. */
struct mailbox {
    uint32_t magic, abi, state, command, heartbeat, mode;
    uint32_t period, high, cycles, timeout, count, generated;
    uint32_t overflow, late, initial, elapsed, max_gap, reserved;
    struct event events[T06_EVENTS];
};
#endif
