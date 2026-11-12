"""Convierte capturas R31/IEP en tiempos. Ningun dato sintetico se acredita."""
def analyze(raw, period_us, high_us, mode, cycles):
    errors=[]
    if not isinstance(raw, dict):
        raise ValueError("Captura debe ser un objeto")
    required=("state","initial","generated","overflow","late","max_gap_ticks","events")
    if any(k not in raw for k in required):
        raise ValueError("Captura incompleta")
    for key in required[:-1]:
        if type(raw[key]) is not int or not 0<=raw[key]<=0xffffffff:
            raise ValueError("Campo de captura invalido: "+key)
    if not isinstance(raw["events"],list) or len(raw["events"])>1024:
        raise ValueError("Buffer de eventos invalido")
    for event in raw["events"]:
        if not isinstance(event,(list,tuple)) or len(event)!=2 or any(type(v) is not int or not 0<=v<=0xffffffff for v in event):
            raise ValueError("Evento invalido")
    if mode=="inputs" and not raw["events"]:
        errors.append("Sin instantaneas R31")
    if raw.get("state")!=3: errors.append("Firmware no finalizo DONE")
    if raw.get("overflow"): errors.append("Buffer desbordado")
    if raw.get("late"): errors.append("Generacion con retrasos >10 us")
    # 10 us es limite de sondeo del ensayo, no precision prometida de 5 ns.
    if raw.get("max_gap_ticks",0)>2000: errors.append("Intervalo de muestreo >10 us")
    if mode in ("pru-tx","loopback") and raw.get("generated")!=cycles:
        errors.append("Cantidad generada incorrecta")
    previous=raw.get("initial",0)
    rise=None; fall=None; last_rise=None
    highs=[]; lows=[]; periods=[]; rising=0; falling=0; snaps=[]
    last_tick=-1
    for tick,value in raw.get("events",[]):
        if tick<=last_tick: errors.append("Timestamps desordenados")
        last_tick=tick
        snaps.append({"tick":tick,"clock":(value>>15)&1,"C0":(value>>5)&1,
                      "C1":(value>>14)&1,"C2":(value>>16)&1})
        if (value^previous)&(1<<15):
            if value&(1<<15):
                rising+=1
                if last_rise is not None: periods.append((tick-last_rise)/200.0)
                if fall is not None: lows.append((tick-fall)/200.0)
                rise=tick; last_rise=tick
            else:
                falling+=1
                if rise is not None: highs.append((tick-rise)/200.0)
                fall=tick
        previous=value
    if mode in ("loopback","pru-rx","pwm-capture"):
        if not highs or not periods or not lows: errors.append("Timeout/sin pulsos completos")
        for label,vals,target in (("alto",highs,high_us),("periodo",periods,period_us),
                                   ("bajo",lows,period_us-high_us)):
            if any(abs(v-target)>max(20,target*.02) for v in vals):
                errors.append("Tiempo "+label+" fuera de tolerancia de ensayo (2% o 20 us)")
        if mode=="loopback" and (rising!=cycles or falling!=cycles):
            errors.append("Pulsos ausentes/inesperados en loopback")
        if mode!="loopback" and len(periods)<10:
            errors.append("Menos de 10 periodos completos")
    return {"status":"FAIL" if errors else "PASS","errors":errors,"rising":rising,"falling":falling,
            "high_us":highs,"low_us":lows,"period_us":periods,"snapshots":snaps,
            "frequency_hz":1000000/(sum(periods)/len(periods)) if periods else None,
            "observed_input":mode in ("loopback","pru-rx","pwm-capture") and bool(periods),
            "timebase":"IEP nominal 200 MHz, reloj compartido; no calibracion independiente"}
