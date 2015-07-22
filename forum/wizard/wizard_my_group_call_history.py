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


def _my_group_calls(self, cr, uid, data, context):
#    cr.execute('select id, name from ir_ui_view where model=%s and name=%s', ('cmc.call.history', 'view_cmc_my_call_tree'))
#    view_res = cr.fetchone()
    #fetch all ids with no 
    q = 'select id from cmc_call_history '\
        'where allocated_user_group_id in (select gid from res_groups_users_rel where uid = '+str(uid)+')'
    cr.execute(q)
    ids = cr.fetchall()
    return  {
            'domain': "[('id','in',%s), ('state', '=', 'allocated')]" % str(ids),
            'name': 'Calls Allocated to My Group',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.call.history',
            'view_id': False,
            'type': 'ir.actions.act_window'
            }


class wizard_cmc_my_group_call_tree(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _my_group_calls, 'state':'end'}
            }
    }       

wizard_cmc_my_group_call_tree('wizard_cmc_my_group_call_tree')
