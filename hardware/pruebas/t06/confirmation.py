"""Declaracion humana trazable; no constituye medicion automatica."""
import hashlib
import json
from pathlib import Path
from common import Blocked
def validate_confirmation(path,board,fixture,operator):
    if not path or not operator:raise Blocked("Faltan --operator y --checklist fisico de nivel 1")
    p=Path(path);raw=p.read_bytes();c=json.loads(raw.decode("utf-8"))
    if not isinstance(c,dict):raise Blocked("Checklist invalido")
    if (c.get("schema")!=1 or c.get("board")!=board or c.get("hardware_revision")!="BBB-BARE" or
        c.get("level")!=1 or c.get("fixture")!=fixture or c.get("operator")!=operator or
        not c.get("checked_at") or not c.get("evidence")):raise Blocked("Identidad/fecha/evidencia del checklist incompatible")
    for key in ("interface_disconnected","actuators_disconnected","wiring_done_unpowered","pins_identified","supply_checked"):
        if c.get(key) is not True:raise Blocked("Checklist pendiente: "+key)
    try:
        v=float(c["p9_3_V"]);u=float(c["uncertainty_V"])
        if not (u>=0 and 3.135<=v-u and v+u<=3.465):raise ValueError()
    except (KeyError,ValueError,TypeError):raise Blocked("Medicion P9_3 ausente/invalida")
    if not c.get("instrument"):raise Blocked("Falta instrumento de P9_3")
    c["sha256"]=hashlib.sha256(raw).hexdigest()
    c["note"]="Declaracion humana; no autenticacion automatica de medicion"
    return c
