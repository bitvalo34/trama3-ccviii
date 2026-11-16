"""Additional gates for the explicitly authorized two-medium experiment."""
import re

CHECKS = ('power_3v3', 'actuator_supply_p2', 'no_known_short', 'harness_p2',
          'inputs_3v3', 'clock_pc817_isolated', 'servo_power_disconnected')

def validate_lab(p, frames=False):
    if p.get('experiment') != 'optical-acoustic' or p.get('available_mask') != 3:
        raise ValueError('LAB_AVAILABILITY')
    if p.get('hardware_revision') != 'T51-P2-LOCAL' or p.get('abi') != 4:
        raise ValueError('LAB_REVISION')
    c=p.get('calibration', {})
    if c.get('board') != p.get('board') or not c.get('evidence') or not c.get('checked_at'):
        raise ValueError('LAB_EVIDENCE_REQUIRED')
    if c.get('status') not in ('COMMISSIONING', 'MEASURED'):
        raise ValueError('LAB_STATUS')
    if not all(c.get('checks', {}).get(k) is True for k in CHECKS):
        raise ValueError('LAB_ELECTRICAL_CHECKS')
    if not p.get('mcp_reset_confirmed') or not (p.get('rx_invert', 0)&8) or c.get('rx_invert') != p.get('rx_invert'):
        raise ValueError('LAB_RESET_OR_POLARITY')
    if not re.match(r'^/dev/i2c-[0-9]+$', p.get('i2c_device','')) or c.get('i2c_device') != p['i2c_device'] or not c.get('i2c_adapter_evidence'):
        raise ValueError('LAB_I2C_EVIDENCE')
    a=p.get('acoustic', {})
    vals=[a.get(k) for k in ('start', 'end', 'min_active', 'max_gap')]
    if not all(type(v) is int for v in vals): raise ValueError('LAB_WINDOW')
    start,end,minimum,gap=vals
    if not (0<=start<end<=160000000 and 0<=minimum<=end-start and 0<gap<=20000):
        raise ValueError('LAB_WINDOW')
    if frames and (c['status']!='MEASURED' or minimum==0 or not a.get('evidence') or not c.get('clock_evidence')):
        raise ValueError('LAB_FRAME_CALIBRATION')
    return p
