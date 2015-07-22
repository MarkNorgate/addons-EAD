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


def _my_enquiries(self, cr, uid, data, context):
    query="select id from cmc_assessment where driving_assessment_type in ('full_driving_assessment','drive_from_wheelchair_assessment','passenger_assessment_map','review_assessment','Access Egress Assessment','Information  Advice Session','Information Enquiry','passenger_assessment')"
    cr.execute(query)
    ids = cr.fetchall()
    debug(ids)
    cr.execute("select view_id from ir_act_window where name='All ILME Assessment Records'")
    view= cr.fetchall()
    return  {
            
            'name': 'All Assessment Records',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.assessment',
            'view_id': view[0],
            'type': 'ir.actions.act_window',
            }


class wizard_adi_reception_filter_assessment(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _my_enquiries, 'state':'end'}
            }
    }       

wizard_adi_reception_filter_assessment('wizard_adi_reception_filter_assessment')