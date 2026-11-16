"""Modelo de contrato T13/T57, NO motor PRU desplegable ni prueba fisica."""
from collections import deque
HZ=200000000
WRAP=1<<32
class TickExtender:
    def __init__(self):
        self.previous=None
        self.total=0
    def advance(self,low,elapsed_ns):
        if type(low) is not int or not 0<=low<WRAP:raise ValueError("Timestamp invalido")
        # elapsed_ns is an independent watchdog bound, not inferred from low.
        if type(elapsed_ns) is not int or elapsed_ns<0 or elapsed_ns*HZ>=WRAP*1000000000:
            raise ValueError("Intervalo ambiguo: reiniciar epoch y resincronizar")
        if self.previous is None:self.total=low
        else:self.total+=(low-self.previous)&(WRAP-1)
        self.previous=low
        return self.total
class CaptureRing:
    def __init__(self,capacity=256,epoch=0):
        if type(capacity) is not int or not 3<=capacity<=1024:raise ValueError("Capacidad invalida")
        self.capacity=capacity;self.epoch=epoch;self.sequence=0;self.queue=deque();self.overflow=False;self.stopped=False
    def push(self,tick64,r31,invert_mask=0,kind="sample",late=False):
        if self.stopped:raise ValueError("STOPPED: iniciar nueva captura explicitamente")
        if kind not in ("sample","edge"):raise ValueError("Tipo invalido")
        if not 0<=invert_mask<=7:raise ValueError("Polaridad invalida")
        if len(self.queue)>=self.capacity:
            self.overflow=True;self.stopped=True;return False
        raw=((r31>>5)&1)|(((r31>>14)&1)<<1)|(((r31>>16)&1)<<2)
        self.queue.append(dict(epoch=self.epoch,sequence=self.sequence,tick64=tick64,r31=r31,
                               raw_vector=raw,vector=raw^invert_mask,kind=kind,late=bool(late)))
        self.sequence+=1
        return True
    def consume(self,limit=3):
        if type(limit) is not int or limit<1:raise ValueError("Limite invalido")
        return [self.queue.popleft() for _ in range(min(limit,len(self.queue)))]
    def stop(self):self.stopped=True
