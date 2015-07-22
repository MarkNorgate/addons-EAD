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

def _my_pending_payment_assessments(self, cr, uid, data, context):
    debug("=====Completed Assessments=====")
    my_pending_payment_assessments=[]
    query="select cmc_assessment.id from cmc_assessment \
    left join cmc_appointments on cmc_assessment.id=cmc_appointments.assessment_id \
    where cmc_assessment.total_balance > 0.00 \
    and cmc_assessment.driving_assessment_type not in ('Driving Tution','Drive From Wheelchair Tution','MoMap Familiarisation') \
    and cmc_appointments.state='completed' and \
cmc_appointments.apmnt_start_date >= '2011-07-01'"
    cr.execute(query)
    my_pending_payment_assessments = cr.fetchall()
    cr.execute("select view_id from ir_act_window where name='EAD Assessment'")
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
class wizard_cmc_pending_payment_assessment(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _my_pending_payment_assessments, 'state':'end'}
            }
    }
    
    
wizard_cmc_pending_payment_assessment('wizard_cmc_pending_payment_assessment')