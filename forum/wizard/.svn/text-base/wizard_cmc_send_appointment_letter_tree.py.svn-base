

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


def _my_pending_appointment_letter(self, cr, uid, data, context):
#    cr.execute('select id, name from ir_ui_view where model=%s and name=%s', ('cmc.enquiry', 'view_cmc_my_enquiry_tree'))
#    view_res = cr.fetchone()
    debug(data)
    debug(self)
    return  {
            'domain': "[('driving_assessment_type','in',['full_driving_assessment','drive_from_wheelchair_assessment']),('state', 'in', ['pending_send_appointment_letter'])]" ,
            'name': 'Send Appointment Letter',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.assessment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': {'user_id':uid}
            }


class wizard_cmc_send_appointment_letter_tree(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _my_pending_appointment_letter, 'state':'end'}
            }
    }       

wizard_cmc_send_appointment_letter_tree('wizard_cmc_send_appointment_letter_tree')
