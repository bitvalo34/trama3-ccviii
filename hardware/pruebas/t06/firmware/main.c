/* T06: prueba finita, sin protocolo 102 ni drivers de actuadores.
 * TI clpru, AM335x PRU0. IEP a 200 MHz; ambos PRU deben ser exclusivos.
 * R31 se lee UNA vez por iteracion y todas las entradas comparten muestra.
 * Resolucion del contador NO equivale a precision de captura del bucle. */
#include "abi.h"
#ifndef T06_MODEL
volatile register uint32_t __R30;
volatile register uint32_t __R31;
#endif
#define REG(a) (*(volatile uint32_t *)(a))
#define IEP_CFG REG(0x2e000)
#define IEP_COUNT REG(0x2e00c)
#define IEP_COMPEN REG(0x2e008)
#define IEP_CMP_CFG REG(0x2e040)
#define PRU_CFG_SYSCFG REG(0x26004)
#define PRU_CFG_GPCFG0 REG(0x26008)
#define PRU_CFG_IEPCLK REG(0x26030)
#define M ((volatile struct mailbox *)0x10000)
#ifdef T06_MODEL
#include "model.h"
#endif
#pragma DATA_SECTION(resource_table, ".resource_table")
#pragma RETAIN(resource_table)
const uint32_t resource_table[4] = {1,0,0,0};

void main(void) {
    uint32_t mode, p, h, n, limit, start, now, prev, r, old;
    uint32_t next, rising, sent, delta, count, last_sample, outcome;
    __R30 &= ~T06_TX;
    PRU_CFG_SYSCFG &= ~(1u<<4); /* STANDBY_INIT=0: acceso OCP */
    PRU_CFG_GPCFG0 = 0; /* GPI/GPO directos */
    PRU_CFG_IEPCLK |= 1u; /* reloj IEP OCP, 200 MHz en AM335x */
    IEP_CFG=0; IEP_COMPEN=0; IEP_CMP_CFG=0; IEP_COUNT=0;
    IEP_CFG=0x11; /* DEFAULT_INC=1, CNT_ENABLE=1; sin compensacion */
    M->magic=0; M->abi=T06_ABI; M->command=0; M->heartbeat=0;
    M->count=0; M->state=READY; M->magic=T06_MAGIC;
    for (;;) {
        M->heartbeat++;
#ifdef T06_MODEL
        model_service();
#endif
        mode=M->command;
        if (mode==CMD_STOP) {
            __R30 &= ~T06_TX; M->command=0; M->state=STOPPED; continue;
        }
        if (mode==CMD_NONE) continue;
        M->command=0; M->mode=mode;
        p=M->period; h=M->high; n=M->cycles; limit=M->timeout;
        M->count=0; M->generated=0; M->overflow=0; M->late=0;
        M->elapsed=0; M->max_gap=0;
        if (mode>CMD_SNAPSHOT || p<200000u || p>20000000u ||
            h<20000u || h>=p || n<2 || n>200 ||
            limit< p || limit>2000000000u ||
            ((mode==CMD_TX || mode==CMD_LOOP) && n>(limit-p)/p)) {
            __R30 &= ~T06_TX; M->state=ERROR; continue;
        }
        __R30 &= ~T06_TX;
        old=__R31 & T06_INPUTS; M->initial=old;
        start=IEP_COUNT; prev=start; last_sample=0; next=p; outcome=DONE;
        rising=1; sent=0; count=0; M->state=RUNNING;
        for (;;) {
            #ifdef T06_MODEL
            model_step();
#endif
            now=IEP_COUNT; r=__R31 & T06_INPUTS;
            delta=now-prev; prev=now;
            if (delta>M->max_gap) M->max_gap=delta;
            if (M->command==CMD_STOP) { outcome=STOPPED; break; }
            if ((uint32_t)(now-start)>=limit) {
                outcome=(mode==CMD_RX || mode==CMD_SNAPSHOT) ? DONE : ERROR;
                break;
            }
            if ((mode==CMD_TX || mode==CMD_LOOP) && sent<n &&
                (int32_t)((now-start)-next)>=0) {
                if ((now-start)-next>2000u) M->late++; /* >10 us */
                if (rising) {
                    __R30 |= T06_TX; next+=h; rising=0;
                } else {
                    __R30 &= ~T06_TX; next+=p-h; rising=1; sent++;
                    M->generated=sent;
                }
            }
            if (mode!=CMD_TX && ((mode!=CMD_SNAPSHOT && ((r^old)&T06_RX)) ||
                (mode==CMD_SNAPSHOT && (now-start)-last_sample>=p))) {
                if (count>=T06_EVENTS) { M->overflow=1; outcome=ERROR; break; }
                M->events[count].tick=now-start;
                M->events[count].r31=r; count++; M->count=count;
                last_sample=now-start; old=r;
            }
            /* Deja un periodo adicional bajo para observar el ultimo flanco. */
            if ((mode==CMD_TX || mode==CMD_LOOP) && sent>=n) {
                __R30 &= ~T06_TX;
                /* Evita una subida n+1 durante la guarda final. */
                if ((now-start)>=p*(n+1)) { outcome=DONE; break; }
            }
        }
        __R30 &= ~T06_TX; M->elapsed=IEP_COUNT-start; M->command=0;
        /* Publicar el estado final DESPUES de todos los datos. */
        M->state=outcome;
    }
}
