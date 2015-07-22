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

def _my_dvla_pending_assessments(self, cr, uid, data, context):
    debug("=====Completed Assessments=====")
    debug(data)
    debug(uid)
    my_pending_payment_assessments=[]
    cr.execute('select id from cmc_assessment where payment_received=False')
    my_pending_payment_assessments = cr.fetchall()
    cr.execute("select view_id from ir_act_window where name='CMC Assessment'")
    view= cr.fetchall()
    debug(my_pending_payment_assessments)
    return  {
            'name': 'Pending Payment Assessments',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.assessment',
            'view_id': view[0],
            'type': 'ir.actions.act_window',
            'domain': "[('id','in',%s)]" % str(my_pending_payment_assessments),
            }
class wizard_dvla_pending_assessment(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _my_dvla_pending_assessments, 'state':'end'}
            }
    }
    
    
wizard_dvla_pending_assessment('wizard_dvla_pending_assessment')