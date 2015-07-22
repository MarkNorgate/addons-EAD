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

def _my_completed_assessments(self, cr, uid, data, context):
    debug("=====Completed Assessments=====")
    completed_assessments=[]
    query="select id from cmc_assessment where (state in (select id from cmc_assessment_state where name like '%-Complete' or name like '%-All Hours Completed'))"
    cr.execute(query)
    completed_assessments = cr.fetchall()
    cr.execute("select view_id from ir_act_window where name='EAD Assessment'")
    view= cr.fetchall()
    return  {
            
            'name': 'Completed Assessments',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.assessment',
            'view_id': view[0],
            'type': 'ir.actions.act_window',
            'domain': "[('id','in',%s)]" % str(completed_assessments),
            }
class wizard_cmc_my_completed_assessment(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _my_completed_assessments, 'state':'end'}
            }
    }
    
    
wizard_cmc_my_completed_assessment('wizard_cmc_my_completed_assessment')