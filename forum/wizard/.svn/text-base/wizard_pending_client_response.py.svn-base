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


def _pending_client_response_pack(self, cr, uid, data, context):
#    cr.execute('select id, name from ir_ui_view where model=%s and name=%s', ('cmc.enquiry', 'view_cmc_my_enquiry_tree'))
#    view_res = cr.fetchone()
#    #fetch all ids with no 
#    q = 'select id from cmc_enquiry '\
#        'where (allocated_user_group_id is NULL) and (allocated_user_id is null) '\
#        ' or allocated_user_group_id in (select gid from res_groups_users_rel where uid = '+str(uid)+')'
#    cr.execute(q)
#    ids = cr.fetchall()
    return  {
            'domain': """[('state', '=', 'awaiting'),
                        ('enquiry_type','not in',['general'])]""",
            'name': 'Pending Client Response',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.enquiry',
            'view_id': False,
            'type': 'ir.actions.act_window'
            }


class wizard_cmc_pending_client_response_tree(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _pending_client_response_pack, 'state':'end'}
            }
    }       

wizard_cmc_pending_client_response_tree('wizard_cmc_pending_client_response_tree')
