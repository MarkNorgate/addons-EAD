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


def _my_appointments(self, cr, uid, data, context):
    debug("=====APPOINTMENT DIARY=====")
    debug(data)
    debug(uid)
    my_appointments=[]
    
    cr.execute('select id from cmc_appointments where type not in (\'reminder\') and state not in (\'cancelled\',\'cancelled_within_two_days\') and '\
               '((owner =%s)  or id in (select appointment_id from user_appointment_rel  where user_id=%s))', ( str(uid), str(uid) ))
    my_appointments = cr.fetchall()
    debug(my_appointments)
    return  {
            
            'name': 'My Appointment Diary',
            'view_type': 'form',
            'view_mode': 'calendar,form',
            'res_model': 'cmc.appointments',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': "[('id','in',%s)]" % str(my_appointments),
            'context':{'single_user':uid}
            }


class wizard_cmc_my_appointment_tree(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _my_appointments, 'state':'end'}
            }
    }       

wizard_cmc_my_appointment_tree('wizard_cmc_my_appointment_tree')
