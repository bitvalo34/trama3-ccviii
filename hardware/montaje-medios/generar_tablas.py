from pathlib import Path
import csv,json,hashlib,math,sys,importlib.util
R=Path(__file__).resolve().parent
P=json.loads((R/'cad/parametros.json').read_text(encoding='utf8'))
D=json.loads((R/'fuentes/T51-P2-LOCAL/diseno.json').read_text(encoding='utf8'))
def write(name,fields,rows):
    with (R/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(fields);w.writerows(rows)

inventory=[
['MDF300x200','2 piezas',1,1,0,0,0,'base','ambos nodos','espesor pendiente'],
['PVC1pulgada','1000mm',0,0,'2x480mm','34mm con kerf3','0 si largo real>=966','C0 bidireccional','X30/75','OD/ID y corte por confirmar'],
['Manguera1/2pulgada','1000mm',0,0,'2x480mm','40mm','0 si largo real>=960','C1 bidireccional','X120/160','manga externa no consume conducto'],
['Abrazaderas1pulgada','4',2,2,0,0,'si OD no compatible','PVC','Y181','cincho en cuna firme como alternativa a cotejar'],
['TuercasM3','24',14,14,0,0,4,'28 uniones pasantes','8 placas +6 soportes por nodo','si separadores roscados:12 necesarias y12 sobrantes'],
['M3x16','mas de24',6,6,0,'>=13 si hay25','medir conteo','servo/SW2/SW287','2 por soporte','no bastan para placa+separador pasante'],
['Tornillos largos placas','no declarados','8','8',0,'pendiente','hasta16 condicionales','4 M3x25 PCB +4 M3x20/22/25 BBB por nodo','placas','usar separadores roscados y tornillos independientes si disponibles'],
['ArandelasM3 metal','25',14,14,0,0,3,'bajo MDF en 28 fijaciones','cara inferior MDF','con separadores de otro tipo recalcular'],
['Arandelas aislantes','no declaradas',8,8,0,'pendiente','hasta16 condicionales','proteger PCB','cara superior soportes','cabezas/soportes plasticos compatibles'],
['Tornillos abrazaderas','disponibles sin conteo',4,4,0,'pendiente','segun conteo/paso','dos por abrazadera propuestos','Y181','transferir patron real'],
['Cinchos','100',12,12,4,72,0,'mangueras/tapas/arneses','frontal y corredores','no comprimir ni cubrir sensor'],
['Nylon0.5mm','disponible sin longitud',0,0,'2x750mm','Ldisponible-1500','si L<1500','C2','X215/275','conservar colas y reserva'],
['Armellas cerradas','24',3,3,0,18,'soporte alto si vastago corto','guiaTX/guiaRX/retorno','ver perforaciones','no desenroscar para ganar altura'],
['Escuadras1pulgada','4',2,2,0,0,'si repisa SW287 incompatible','SW2 ySW287','frontal/rear lateral','adaptador rigido reciclado si hace falta'],
['Resortes','1 caja',1,1,2,'conteo-4','si no hay4 adecuados','2 retorno+2 serie','C2','k/F0/longitud por medir'],
['Espuma','disponible sin medida','2 apoyos+2 mangas','2 apoyos+2 mangas','apoyo medio manguera opcional','pendiente','segun tamaño','aislamiento acustico','C1','no usar espuma blanda para alinear PVC'],
['Bases servo','2',1,1,0,0,'0 si huella encaja','SG90','segun tabla','presentar antes de taladro'],
['Separadores plasticos','disponibles sin conteo',8,8,0,'conteo-16','si conteo<16','PCB/BBB','12/8mm iniciales','tipo roscado o clip cambia tornilleria'],
['Calces firmes PVC','no declarados',2,2,0,'pendiente','4 si no hay sobrantes','altura eje40','bajo abrazaderas','retazos madera/plastico rigido'],
['Tapas opacas PVC','no declaradas',2,2,0,'pendiente','4 si no hay retazos','sellar luz ambiente','bocasC0','carton opaco rigido o plastico reciclado'],
['Soportes/acoples auxiliares','no declarados','segun piezas reales','segun piezas reales',0,'pendiente','condicional','sensores y ancla alta','frontal','retazos y cinchos; no requiere impresora3D'],
['Pares reloj26AWG','longitud no declarada',0,0,'2x1100mm de par','pendiente','si par disponible<2200mm','dos relojes','bordesglobal5/295','no tercerGND'],
['BBB','2 declaradas',1,1,0,0,0,'procesamiento','trasera','conservar existentes'],
['Perfboard90x150','2 previstas;1 soldada',1,1,0,0,'terminar segunda','interfazP2','trasera','no reconstruir primera'],
['LED/LDR/buzzer/MIC/SG90/SW2','2 de cada declarados','1 de cada','1 de cada',0,0,'verificar variantes','tres medios','frontal','pinoutMIC independiente'],
['SW287/IRLZ44N','P2 previstos;conteo real pendiente','1 de cada','1 de cada',0,'pendiente','segun kitP2','mantenimiento/proteccion','SW287 lateral/Q6 placa','no sustitucionP1 directa'],
['Fuentesactuadores5V2.5A','2 previstas sin identificar',1,1,0,'pendiente','si no aisladas/flotantes','alimentacion','fueraMDF','verificar disponibles antes de comprar'],
['Instrumentacion','multimetro;sin osciloscopio confirmado',0,0,'prestamo para pruebas','no aplica','prestamo osciloscopio/captura','amplitud/tiempos','banco','no instalar otra appCAD']]
write('materiales/distribucion.csv',['material','disponible','nodo_A','nodo_B','entre_nodos','sobrante','faltante_condicional','funcion','posicion','alternativa_nota'],inventory)

measures=[
['M01','MDF espesor',6,'PROVISIONAL','calibre3puntos','corte/fijaciones'],['M02','MDF ancho/fondo','300x200','DECLARADO','regla yescuadra','huella'],
['M03','Perfboard','90x150x1.6','NOMINAL','medir contorno y cuatro agujeros','taladrar'],['M04','BBB','86.36x53.34','FABRICANTE; variante pendiente','cotejar contorno y transferir agujeros','taladrar'],
['M05','Agujeros BBB','candidatos en CSV','NO VERIFICADOS','transferir desde placa; no perforar PCB','taladrar'],
['M06','Saliente inferior soldaduras','','PENDIENTE','regla puente y calibre sin tocar soldaduras','alturaPCB'],
['M07','Separadores','12PCB/8BBB','PROVISIONAL','medir altura rosca/clip y cantidad','fijaciones'],
['M08','PVC OD/ID','34/28','PROVISIONAL','calibre dos ejes','abrazaderas/tapas'],['M09','Manguera OD/ID','18/12.7','PROVISIONAL','calibre sin comprimir','mangas'],
['M10','Longitud PVC/manguera','1000/1000','DECLARADO','medir sin estirar; medir kerf','corte'],
['M11','SG90','23x12.2x29','FABRICANTE referencia','medir lote y base/orejas','envolvente'],
['M12','Radio brazo/angulo','8/20','PROPUESTO','medir agujero existente y excursion real','nylon'],
['M13','Switch SW2','28x16x15','RESERVA P2','medir agujeros; fuerza/recorrido/retorno','mecanismo'],
['M14','SW287','30x25x55; agujero12','RESERVA P2','medir cuerpo/casquillo; continuidad6terminales','soporte/arnes'],
['M15','LDR-A/LDR-B','32x14x12','RESERVA P2','medir individual y mapa de pines','acoples'],
['M16','MIC-A/MIC-B','45x17x16','RESERVA P2','medir cada variante y pines','acoples/arneses'],
['M17','Buzzer','12x12x10','RESERVA P2','diametro/apertura/polaridad/consumo','acople/driver'],
['M18','Resortes k/F0/L0','','PENDIENTE','ensayo fuerzas conocidas y elongaciones','tension'],
['M19','Espuma espesor/densidad','','PENDIENTE','medir espesor; ficha si existe; no inferir densidad','acoples'],
['M20','Armellas vastago/rosca/ojo','','PENDIENTE','calibre y profundidad segura','guia elevacion'],
['M21','Fuentes modelos/polaridad','','PENDIENTE','etiqueta/ficha y mediciones T08','energia'],
['M22','Nylon longitud/elongacion','1500min reserva','PROPUESTO','medir longitud y elongacion carga elegida','C2'],
['M23','Cable reloj longitud','2x1100par','PROPUESTO','medir ruta y existencias','CLK'],
['M24','Calce/escuadra altura','','PENDIENTE','presentar soporte real con carga','alineacion'],
['M25','Pila tornillo y arandelas','','PENDIENTE','sumar espesores reales y rosca util','fijaciones'],
['M26','Gap360 y eje40/32/36','360/40/32/36','PROPUESTA','regla desde origen comun','presentacion'],
['M27','Revision fisica PCB-A/B','P2 candidata','NO CONFIRMADA','continuidad y marcado contra snapshot','cableado/energia']]
write('materiales/medidas-criticas.csv',['id','magnitud','referencia_mm_salvo_indicado','estado','metodo','bloquea','valor_A','valor_B','instrumento','fecha','evidencia'],[r+['']*5 for r in measures])

fix=[['PCB',4,12,1.6,25,'M3x16 insuficiente','separadorroscado'],['BBB',4,8,1.6,20,'M3x20 justo nominal; revisar tolerancia','M3x22/25 o separadorroscado'],['Servo',2,0,5,16,'medir base','tornillo disponible'],['SW2',2,0,2,16,'medir soporte','M3x16'],['SW287',2,0,2,16,'medir soporte','M3x16']]
write('materiales/fijaciones.csv',['componente','cantidad_por_nodo','separador_mm','pieza_mm','largo_candidato_mm','nota','alternativa','Lmin_con_MDF6_arandela1_tuerca2p4_salida1'],[r+[round(6+r[2]+r[3]+1+2.4+1,1)] for r in fix])

rows=[]
with (R/'fuentes/T51-P2-LOCAL/arneses-externos.csv').open(encoding='utf-8-sig') as f:source=list(csv.DictReader(f))
for s in source:
    nodes=['A','B'] if s['aplica']=='A y B' else [s['aplica']]
    for n in nodes:
        long=1100 if '->' in n else 350 if s['id'] in ['H01','H02'] else 250 if int(s['id'][1:])<=7 else 300
        net=s['red'];color='rojo' if '5V' in net else 'negro' if 'GND' in net else 'naranja' if '3V3' in net else 'violeta' if 'opto' in net else 'azul'
        path='bordesglobalX5AB/X295BA' if '->' in n else 'potenciaY8/X285' if int(s['id'][1:])<=7 else 'frontal porY115'
        rows.append([n+'-'+s['id'],n,s['origen'],s['destino'],net,long,s['conductor'],color,'bornera/terminal aislado segun pieza',path,'RESERVA; medir en seco; P2 por confirmar'])
pins=['P9_3','P9_1','P9_19','P9_20','P9_14','P8_11','P9_27','P8_16','P9_24','P8_15'];j=next(x for x in D['components'] if x['ref']=='J10')
for n in ['A','B']:
    for p,bbb in zip(j['pins'],pins):rows.append([n+'-J10-'+p['number'],n,'J10.'+p['number'],bbb,p['net'],300,'26AWG flexible','segun guia J10','hembra2.54 desmontable','J10-Y112-X177-BBB','verificar continuidad individual'])
    rows.append([n+'-PWR-IN',n,'fuente aislada + y -','J1.1/J1.2','+5V_RAW / NEG_IN',400,'22AWG flexible o fuente validada','rojo/negro con etiquetaNEG_IN','conector REAL fuente +bornera','traseroY0','no unir NEG_IN aGND_ACT'])
write('materiales/arneses.csv',['etiqueta','nodo_sentido','origen','destino','funcion_red','longitud_reserva_mm','calibre_propuesto','color','terminal','ruta','estado'],rows)
write('materiales/J10.csv',['pin_J10','pin_BBB','red','estado'],[[p['number'],bbb,p['net'],'REFERENCIA P2; continuidad fisica pendiente'] for p,bbb in zip(j['pins'],pins)])

write('calibracion/registros.csv',['procedimiento','medio','sentido','estado','reposo','activacion','liberacion','patron_010101','retardo_subida_ms','retardo_bajada_ms','rebote_ms','falsos_positivos','falsos_negativos','ensayos','Vlow','Vhigh','polaridad','ajuste','evidencia','revision_fw','operador','revisor','fecha'],[[f'P{i+1:02}',m,d,'NO_PROBADO']+['']*19 for i,(m,d) in enumerate([(m,d) for m in ['C0','C1','C2','CLK'] for d in ['AB','BA']])])
fields=['ensayo','medio','sentido','tick','esperado','observado','t_orden_s','t_estable_s','flancos','v_bajo','v_alto','polaridad','resolucion_s','evidencia','operador','fecha','revision_fw']
write('calibracion/muestras.csv',fields,[[m+'-'+d+'-01',m,d,i,b]+['']*12 for m in ['C0','C1','C2'] for d in ['AB','BA'] for i,b in enumerate('010101')])
write('calibracion/diafonia.csv',['receptor','sentido','agresor','patron_propio','ventanas','FP','FN','flancos_extra','evidencia','estado'],[[m,d,a,p,'','','','','','NO_PROBADO'] for m in ['C0','C1','C2'] for d in ['AB','BA'] for a in ['otro sentido mismo medio','otros medios','servo local','ambos servos','todos'] for p in ['reposo','010101']])
write('calibracion/resortes.csv',['id','funcion','L0_mm','F1_N','L1_mm','F2_N','L2_mm','k_N_mm','F0_N','elongacion_servicio_mm','retorno_L0','instrumento','incertidumbre','evidencia'],[[k,f]+['']*12 for k,f in [('S1','serieAB'),('S2','serieBA'),('S3','retornoA'),('S4','retornoB')]])
write('calibracion/reloj.csv',['sentido','pulso','T_s','ancho_TX_s','ancho_RX_activo_s','retardo_s','perdidos','extras','concurrente','polaridad','evidencia','estado'],[[d,p]+['']*9+['NO_PROBADO'] for d in ['AB','BA'] for p in ['marcador','ordinario','guarda','doble reloj']])
write('calibracion/desviaciones-P2.csv',['nodo','ref','esperado','observado','correccion','evidencia','revision_Adrian','estado'],[[n,r,v,'','','','','PENDIENTE'] for n in ['A','B'] for r,v in [('Q6','IRLZ44N G=5V D=NEG_IN S=GND_ACT'),('SW1','SW287 contactos comprobados'),('J11_MOD3_J12','sin conexiones P1'),('NT1','unica union GND_ACT-LOGIC'),('J10','10pines segun tabla'),('J5_J6','3V3 DO individual'),('J8_J9','opto par sin GND remoto'),('AletaQ6','sin contacto conductor'),('Fuente','aislada flotante identificada')]])

manifest={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'fuentes/T51-P2-LOCAL').iterdir() if p.is_file()}
(R/'evidencias/fuentes-sha256.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print('Tablas generadas; registros vacios, no evidencia fisica.')
