/* Propuesta ABI2 T13/T57, separada de ABI1 diagnostica. No firmware desplegado.
 * SPSC: PRU publica producer tras datos + barrera; ARM consumer tras copia.
 * Indices uint32 monotonic modulo; capacidad potencia de 2 <=1024.
 * Nunca sobreescribir muestra sin consumir. Overflow -> FAULT -> STOP.
 * Timestamp hi/lo estable bajo publicacion de slot; no lectura 64-bit atomica.
 */
#ifndef TRAMA3_STREAM102_H
#define TRAMA3_STREAM102_H
#include <stdint.h>
#define STREAM102_ABI 2u
#define STREAM102_CAPACITY 256u
struct stream102_event {
 uint32_t sequence, epoch, ticks_lo, ticks_hi, r31, normalized, flags;
};
struct stream102_control {
 uint32_t magic, abi, epoch, command, state, producer, consumer, overflow, late;
 struct stream102_event events[STREAM102_CAPACITY];
};
typedef char stream102_shared_fits[(sizeof(struct stream102_control)<=12288)?1:-1];
#endif
