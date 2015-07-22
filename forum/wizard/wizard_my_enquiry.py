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
#    cr.execute('select id, name from ir_ui_view where model=%s and name=%s', ('cmc.enquiry', 'view_cmc_my_enquiry_tree'))
#    view_res = cr.fetchone()
    debug(data)
    debug(self)
    return  {
            'domain': "[('allocated_user_id','=',%d)]" % (uid),
            'name': 'Actions Allocated To Me',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.enquiry',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': {'user_id':uid}
            }


class wizard_cmc_my_enquiry_tree(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _my_enquiries, 'state':'end'}
            }
    }

wizard_cmc_my_enquiry_tree('wizard_cmc_my_enquiry_tree')

def _reception_enquiries(self, cr, uid, data, context):
    cr.execute("select id from cmc_enquiry where state in ('pending','awating') and (allocated_user_group_id in (select id from res_groups where name != 'Mobility ILME User') or allocated_user_group_id is null)")
    ids=cr.fetchall()
    debug(ids)
    return  {
            'domain': "[('id','in',%s)]" % str(ids),
            'name': 'Reception Enquiries - Pending Action',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.enquiry',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': {'user_id':uid}
            }


class wizard_cmc_reception_enquiry_tree(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _reception_enquiries, 'state':'end'}
            }
    }       

wizard_cmc_reception_enquiry_tree('wizard_cmc_reception_enquiry_tree')
