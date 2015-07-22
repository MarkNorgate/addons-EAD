from osv import fields, osv
from osv.orm import except_orm
from string import Template
from tools.misc import debug
from tools.translate import _
import tools
import datetime
import string
import pooler
import base64
import wizard


def _my_appointments_reminder(self, cr, uid, data, context):
    debug("=====APPOINTMENT DIARY=====")
    debug(data)
    debug(uid)
    my_appointments=[]
    query="select id from cmc_appointments where owner="+str(uid)+" and type='reminder' and state not in (\'cancelled\',\'cancelled_within_two_days\')"
    cr.execute(query)
    my_appointments = cr.fetchall()
    debug(my_appointments)
    return  {
            
            'name': 'Reminder Calendar',
            'view_type': 'form',
            'view_mode': 'calendar,form',
            'res_model': 'cmc.appointments',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': "[('id','in',%s)]" % str(my_appointments),
            }


class wizard_cmc_my_appointment_reminder_tree(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _my_appointments_reminder, 'state':'end'}
            }
    }       

wizard_cmc_my_appointment_reminder_tree('wizard_cmc_my_appointment_reminder_tree')
