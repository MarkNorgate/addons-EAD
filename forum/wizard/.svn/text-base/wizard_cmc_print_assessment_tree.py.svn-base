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


def _my_print_assessment(self, cr, uid, data, context):
    return  {
            'domain': "[('driving_assessment_type','in',['full_driving_assessment','drive_from_wheelchair_assessment']),('state', '=', 'print_assessment_paperwork')]",
            'name': 'Print Assessment Paperwork',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.assessment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': {'user_id':uid}
            }
    
class wizard_cmc_print_assessment_tree(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _my_print_assessment, 'state':'end'}
            }
    }       

wizard_cmc_print_assessment_tree('wizard_cmc_print_assessment_tree')
