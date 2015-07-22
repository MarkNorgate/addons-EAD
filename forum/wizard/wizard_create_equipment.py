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


def _create_equipment(self, cr, uid, data, context):
    if context.get('from',False) == 'call history':
        call_browse=pooler.get_pool(cr.dbname).get('cmc.call.history').browse(cr, uid, int(data['id']))
        details=False
        if call_browse.call_details:
            details=call_browse.call_details
        debug(details)
        if call_browse.client_id:
            person_id=call_browse.client_id.id
        else:
            raise except_orm('Warning','Following Record has no client')
    else:
        details=False
        person_id=int(data['id'])
    debug(person_id)
    return  {
            'domain': "[]",
            'name': 'Create New Equipment Enquiry',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'cmc.equipement.supply.process',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': {'person_id':person_id,
                        'details':details}
            }


class wizard_create_equipment(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _create_equipment, 'state':'end'}
            }
    }       

wizard_create_equipment('wizard_create_equipment')

