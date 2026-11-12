"""Esquema y evaluacion electrica. Ausencia nunca equivale a cero."""
import csv
import datetime
import math
from pathlib import Path
PINS=("P8_15","P8_16","P9_24","P9_27")
FIELDS=("board","point","value","uncertainty","unit","method","instrument","measured_at","evidence","notes")
CHECKS={
 "fuentes_identificadas":"Etiquetas, conectores, polaridad y corriente nominal registradas",
 "fuentes_separadas":"BBB por fuente propia, actuadores externos; no 5 V inyectado en BBB",
 "sin_corto":"Sin corto persistente entre rieles; sin alimentacion",
 "polaridad_correcta":"Conectores y electroliticos correctos",
 "retornos_correctos":"NT1 unica union local; retorno servo no por BBB",
 "sin_puente_nodos":"No union indebida entre nodos; USB comun documentado/retirado",
 "fusible_revisado":"F1 curva/corriente coordinadas con cables, Q6 y carga real",
 "pinouts_revisados":"Q1..Q6/U1/U2, adaptador y modulos contrastados con lote",
 "placa_revisada":"T07/T52 y placa construida revisada antes de energizar",
 "sin_anomalias":"Sin calentamiento, daño, reinicios, polaridad inversa ni fuente inestable",
 "servo_desconectado":"Servo sin alimentar durante T06; SW1 OFF",
 "selectores_comprobados":"EN_C0/1/2 y JP4..7 comprobados antes de GPIO",
 "aislamiento_pc817":"Isla J8/U2/D2 sin union al retorno receptor",
 "arranque_apagado":"Sin señales a GPIO con BBB apagada; transitorios revisados",
 "conectores_revisados":"J1/J11 excluyentes; SW1, J4 y arneses con capacidad/polaridad correctas",
 "carga_fuente_revisada":"Prueba bajo carga segura/equipo electronico documentada sin servo bloqueado",
}
# Tolerancias del ensayo de 5 V son conservadoras; no califican el SG90.
NUMERIC={
 "fuente_bbb_5v":(4.75,5.25,"V","multimeter"),
 "fuente_act_5v_vacio":(4.75,5.25,"V","multimeter"),
 "fuente_act_5v_carga":(4.75,5.25,"V","multimeter"),
 "P9_3":(3.135,3.465,"V","multimeter"),
 "TP1_5V_ACT":(4.75,5.25,"V","multimeter"),
 "TP3_3V3":(3.135,3.465,"V","multimeter"),
 "U1_VDD":(3.135,3.465,"V","multimeter"),
 "J5_VDD":(3.135,3.465,"V","multimeter"),
 "J6_VDD":(3.135,3.465,"V","multimeter"),
 "J4_servo_OFF":(0,0.1,"V","multimeter"),
 "TP9_servo_OFF":(0,0.1,"V","multimeter"),
 "riel_logico_mA":(0,75,"mA","current_probe"),
 "buzzer_mA":(0,20,"mA","current_probe"),
}
for pin in PINS:
    NUMERIC[pin+"_LOW"]=(0,0.8,"V","multimeter")
    NUMERIC[pin+"_HIGH"]=(2.0,3.3,"V","multimeter")
    NUMERIC[pin+"_PEAK"]=(0,3.3,"V","oscilloscope")
    NUMERIC[pin+"_MIN"]=(0,0.8,"V","oscilloscope")
ALL_POINTS=tuple(sorted(CHECKS))+tuple(sorted(NUMERIC))

def template(board):
    return [{"board":board,"point":p,"value":"","uncertainty":"","unit":NUMERIC[p][2] if p in NUMERIC else "bool",
             "method":NUMERIC[p][3] if p in NUMERIC else "inspection","instrument":"",
             "measured_at":"","evidence":"","notes":CHECKS.get(p,"")} for p in ALL_POINTS]

def write_csv(path, rows):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)

def read_csv(path):
    with Path(path).open(newline="",encoding="utf-8-sig") as f:
        r=csv.DictReader(f)
        if tuple(r.fieldnames or ())!=FIELDS:
            raise ValueError("Columnas CSV incompatibles")
        return list(r)

def evaluate(rows, board, origin="physical"):
    if origin!="physical":
        return {"schema":1,"board":board,"test":"t08","status":"NOT_TESTED","origin":origin,
                "errors":["Datos simulados no acreditan electricidad"],"points":{}}
    points={};seen={}
    for r in rows:
        if r.get("board")!=board: raise ValueError("CSV mezcla placas")
        key=r.get("point")
        if key not in ALL_POINTS or key in seen:
            raise ValueError("Punto desconocido/duplicado: "+str(key))
        seen[key]=r
    for key in ALL_POINTS:
        r=seen.get(key,{})
        val=r.get("value","").strip()
        state="NOT_TESTED";why="Sin medicion"
        if val:
            state="BLOCKED";why="Falta metodo, instrumento, fecha o evidencia"
            metadata=all(r.get(x,"").strip() for x in ("method","instrument","measured_at","evidence"))
            if metadata:
                if key in CHECKS:
                    if val not in ("yes","no"): why="Usar yes/no, no interpretar texto ambiguo"
                    elif r["method"]!="inspection": why="Metodo debe ser inspection"
                    else: state="PASS" if val=="yes" else "FAIL";why=CHECKS[key]
                else:
                    lo,hi,unit,method=NUMERIC[key]
                    try:
                        v=float(val);u=float(r.get("uncertainty",""))
                        if not math.isfinite(v) or not math.isfinite(u) or u<0: raise ValueError()
                        if r["unit"]!=unit or r["method"]!=method:
                            why="Unidad/metodo incompatible"
                        else:
                            # Intervalo completo debe quedar dentro de los limites.
                            state="PASS" if lo<=v-u and v+u<=hi else "FAIL"
                            why="{} <= valor ± incertidumbre <= {} {}".format(lo,hi,unit)
                    except ValueError: why="Numero/incertidumbre invalida o no finita"
        points[key]={"status":state,"reason":why,"measurement":r or None}
    # Nunca aprobar entrada por encima del riel local aun si <=3.3 nominal.
    rail=seen.get("P9_3",{})
    if points["P9_3"]["status"]=="PASS":
        railmin=float(rail["value"])-float(rail["uncertainty"])
        for pin in PINS:
            key=pin+"_PEAK";r=seen.get(key,{})
            if points[key]["status"]=="PASS" and float(r["value"])+float(r["uncertainty"])>railmin:
                points[key].update(status="FAIL",reason="Pico excede riel local conservador")
    states=[v["status"] for v in points.values()]
    status="FAIL" if "FAIL" in states else "BLOCKED" if "BLOCKED" in states else "NOT_TESTED" if "NOT_TESTED" in states else "PASS"
    return {"schema":1,"board":board,"test":"t08","status":status,"origin":"physical",
            "points":points,"limits_source":"SPRS717L §§5.1,5.3,5.7; criterios conservadores T51/T08",
            "note":"PASS acredita registros aportados; no certifica diseño ni sustituye revision humana"}
