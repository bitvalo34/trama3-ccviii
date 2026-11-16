"""P2-LOCAL: catalogo fisico. Ninguna casilla vacia significa cero."""
import csv
import datetime
import json
import math
from pathlib import Path

SCHEMA=2
REVISION="P2-LOCAL"
PINS=("P8_15","P8_16","P9_24","P9_27")
FIELDS=("schema","hardware_revision","board","point","value","uncertainty","unit","method",
        "instrument","measured_at","evidence","operator","origin","detail","notes")
CHECKS={
 "p2_conforme":"Montaje cotejado con netlist P2, fotos de ambas caras y revision T52/T53/T54",
 "fuentes_identificadas":"Modelo, polaridad, capacidad y salida aislada/flotante de adaptadores identificados",
 "fuentes_separadas":"Sin fuente comun entre actuadores y BBB",
 "sin_corto":"Sin corto persistente entre rieles, descargados",
 "polaridad_correcta":"Polaridad de entrada y condensadores comprobada",
 "retornos_correctos":"NT1 unica union GND_ACT-GND_LOGIC local",
 "neg_in_sin_bypass":"Sin bypass NEG_IN-GND_ACT por cable, aleta, instrumento o fuente",
 "sin_puente_nodos":"Sin cable GND entre nodos; rutas USB/instrumentos documentadas",
 "fusible_revisado":"F1 y cableado coordinados con carga; 1 A provisional no aumentado",
 "q6_verificado":"IRLZ44N, lote/fabricante, encapsulado, G/D/S y aleta verificados",
 "aleta_aislada":"Aleta Q6 NEG_IN sin contacto con GND ni chasis",
 "r30_verificada":"R30 100 kohm entre +5V_ACT y GND_ACT",
 "sw287_OFF":"Tabla de contactos OFF medida y rotulada",
 "sw287_CENTRO":"Tabla de contactos CENTRO medida",
 "sw287_ON":"Tabla de contactos ON medida y rotulada",
 "pinouts_revisados":"Pinouts reales U1, U2, transistores y modulos contrastados",
 "sin_anomalias":"Sin calentamiento, reinicios, olor, dano o fuente inestable",
 "servo_desconectado":"Servo desconectado durante diagnostico T06",
 "selectores_comprobados":"EN_C0/1/2 y JP4..7 diferenciados y verificados",
 "aislamiento_pc817":"U2.1/2 y J8 sin union al retorno receptor",
 "arranque_apagado":"Capturas de encendido/apagado sin tension indebida a GPIO",
 "conectores_revisados":"J1/J4/J10/J13 y borneras P2 contrastados",
 "carga_fuente_revisada":"Carga segura caracterizada; no usar servo bloqueado",
 "modulo_optico_3v3":"Modulo optico real identificado y funcional a 3.3 V",
 "modulo_acustico_3v3":"Modulo acustico real identificado y funcional a 3.3 V",
 "limites_lotes":"Hojas de lote, carga maxima y limites de componentes revisados",
}
METHODS={p:"inspection" for p in CHECKS}
for p in ("sin_corto","retornos_correctos","neg_in_sin_bypass","r30_verificada","sw287_OFF",
          "sw287_CENTRO","sw287_ON","aislamiento_pc817","selectores_comprobados"):
    METHODS[p]="continuity"
METHODS["arranque_apagado"]="oscilloscope"
NUMERIC={
 "fuente_bbb_5v":(4.75,5.25,"V","multimeter"),
 "fuente_act_5v_vacio":(4.75,5.25,"V","multimeter"),
 "fuente_act_5v_carga":(4.75,5.25,"V","multimeter"),
 "P9_3":(3.135,3.465,"V","multimeter"),
 "J1_ENTRADA":(4.75,5.25,"V","multimeter"),
 "TP1_5V_ACT":(4.75,5.25,"V","multimeter"),
 "Q6_VGS":(4.0,5.25,"V","multimeter"),
 "Q6_CAIDA":(0,0.15,"V","multimeter"),
 "TP3_3V3":(3.135,3.465,"V","multimeter"),
 "U1_VDD":(3.135,3.465,"V","multimeter"),
 "J5_VDD":(3.135,3.465,"V","multimeter"),
 "J6_VDD":(3.135,3.465,"V","multimeter"),
 "J4_servo_OFF":(0,0.1,"V","multimeter"),
 "TP9_servo_OFF":(0,0.1,"V","multimeter"),
 "J4_servo_CENTRO":(0,0.1,"V","multimeter"),
 "TP9_servo_CENTRO":(0,0.1,"V","multimeter"),
 "J4_servo_ON":(4.8,5.25,"V","multimeter"),
 "TP9_servo_CENTRO_PICO":(0,0.1,"V","oscilloscope"),
 "riel_logico_mA":(0,75,"mA","current_probe"),
 "buzzer_mA":(0,20,"mA","current_probe"),
 "carga_act_A":(0,1,"A","current_probe"),
 "J7_ABIERTO":(2.0,3.3,"V","multimeter"),
 "J7_CERRADO":(0,0.8,"V","multimeter"),
}
for pin in PINS:
    NUMERIC[pin+"_LOW"]=(0,0.8,"V","multimeter")
    NUMERIC[pin+"_HIGH"]=(2.0,3.3,"V","multimeter")
    NUMERIC[pin+"_PEAK"]=(0,3.3,"V","oscilloscope")
    NUMERIC[pin+"_MIN"]=(0,0.8,"V","oscilloscope")
ALL_POINTS=tuple(sorted(CHECKS))+tuple(sorted(NUMERIC))
CONTACTS={"sw287_OFF":["2-3","5-6"],"sw287_CENTRO":[],"sw287_ON":["1-2","4-5"]}

def template(board):
    if board not in ("BBB-A","BBB-B"):raise ValueError("Placa invalida")
    return [dict(schema=str(SCHEMA),hardware_revision=REVISION,board=board,point=p,value="",
                 uncertainty="",unit=NUMERIC[p][2] if p in NUMERIC else "bool",
                 method=NUMERIC[p][3] if p in NUMERIC else METHODS[p],instrument="",
                 measured_at="",evidence="",operator="",origin="physical",detail="",notes=CHECKS.get(p,""))
            for p in ALL_POINTS]

def write_csv(path,rows):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)

def read_csv(path):
    with Path(path).open(newline="",encoding="utf-8-sig") as f:
        r=csv.DictReader(f)
        if tuple(r.fieldnames or ())!=FIELDS:raise ValueError("CSV P1/incompatible: no migrar evidencia a P2")
        return list(r)

def valid_date(value):
    try:
        # Fecha real obligatoria; admite YYYY-MM-DD o timestamp ISO.
        datetime.datetime.strptime(value[:10],"%Y-%m-%d")
        return len(value)==10 or (len(value)>10 and value[10]=="T")
    except (ValueError,TypeError):return False

def detail_error(key,r):
    if key not in CONTACTS and key not in ("q6_verificado","p2_conforme"):return None
    try:d=json.loads(r.get("detail",""))
    except (ValueError,TypeError):return "Falta detalle estructurado verificable"
    if not isinstance(d,dict):return "Detalle debe ser objeto"
    if key in CONTACTS:
        if (d.get("closed")!=CONTACTS[key] or d.get("all_other_pairs_open") is not True or
            not d.get("terminal_map_evidence")):
            return "Contactos SW287 incompatibles o mapa fisico ausente"
    elif key=="q6_verificado":
        if (d.get("part") not in ("IRLZ44N","IRLZ44NPbF") or
            d.get("package")!="TO-220" or not d.get("manufacturer") or not d.get("datasheet") or
            d.get("pins")!={"1":"G","2":"D","3":"S","tab":"D"} or
            d.get("nets")!={"G":"+5V_ACT","D":"NEG_IN","S":"GND_ACT"}):
            return "Identidad/pinout/topologia Q6 no confirmados"
    elif not all(d.get(k) for k in ("netlist_sha256","front_photo","back_photo","reviewer","board_serial")):
        return "Falta identidad, fotos, netlist o revisor P2"
    return None

def evaluate(rows,board,origin="physical"):
    if board not in ("BBB-A","BBB-B"):raise ValueError("Placa invalida")
    report={"schema":SCHEMA,"hardware_revision":REVISION,"board":board,"test":"t08",
            "origin":origin,"points":{},"status":"NOT_TESTED","integration_allowed":False}
    if origin!="physical":
        report["errors"]=["Simulacion no acredita hardware"];return report
    seen={}
    for r in rows:
        if r.get("board")!=board:raise ValueError("CSV mezcla placas")
        if r.get("schema")!=str(SCHEMA) or r.get("hardware_revision")!=REVISION:
            raise ValueError("Evidencia P1/revision incorrecta; conservar sin convertir")
        key=r.get("point")
        if key not in ALL_POINTS or key in seen:raise ValueError("Punto retirado/desconocido/duplicado: "+str(key))
        seen[key]=r
    points=report["points"]
    for key in ALL_POINTS:
        r=seen.get(key,{})
        val=r.get("value","").strip()
        state="NOT_TESTED";why="Sin medicion"
        if val:
            state="BLOCKED";why="Falta fecha real, operador, instrumento o evidencia fisica"
            metadata=all(r.get(x,"").strip() for x in ("method","instrument","measured_at","evidence","operator"))
            physical=r.get("origin")=="physical" and not any("simulad" in r.get(k,"").lower() for k in ("instrument","evidence"))
            if metadata and physical and valid_date(r["measured_at"]):
                if key in CHECKS:
                    if r["unit"]!="bool" or r["method"]!=METHODS[key]:why="Unidad/metodo incompatible"
                    elif val not in ("yes","no"):why="Usar yes/no"
                    elif val=="no":state="FAIL";why=CHECKS[key]
                    else:
                        error=detail_error(key,r)
                        state="BLOCKED" if error else "PASS";why=error or CHECKS[key]
                else:
                    lo,hi,unit,method=NUMERIC[key]
                    try:
                        v=float(val);u=float(r.get("uncertainty",""))
                        if not math.isfinite(v) or not math.isfinite(u) or u<0:raise ValueError()
                        if r["unit"]!=unit or r["method"]!=method:why="Unidad/metodo incompatible"
                        else:
                            state="PASS" if lo<=v-u and v+u<=hi else "FAIL"
                            why="Intervalo valor +/- incertidumbre dentro de [{}, {}] {}".format(lo,hi,unit)
                    except (ValueError,TypeError):why="Numero/incertidumbre invalida"
        points[key]={"status":state,"reason":why,"measurement":r or None}
    if points["P9_3"]["status"]=="PASS":
        rail=seen["P9_3"];railmin=float(rail["value"])-float(rail["uncertainty"])
        for pin in PINS:
            for suffix in ("_HIGH","_PEAK"):
                key=pin+suffix;r=seen.get(key,{})
                if points[key]["status"]=="PASS" and float(r["value"])+float(r["uncertainty"])>railmin:
                    points[key].update(status="FAIL",reason="Entrada excede riel local conservador")
    states=[v["status"] for v in points.values()]
    report["status"]=next((s for s in ("FAIL","BLOCKED","NOT_TESTED") if s in states),"PASS")
    report["integration_allowed"]=report["status"]=="PASS"
    report["limits_source"]="T08_Auditoria_P2.md: limites por punto; lotes pendientes requieren verificacion"
    report["note"]="Valida registros, no autentica fotos ni sustituye revision humana"
    return report
