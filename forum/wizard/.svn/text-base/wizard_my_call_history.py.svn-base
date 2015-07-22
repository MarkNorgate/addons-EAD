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


def _my_calls(self, cr, uid, data, context):
    debug(data)
    cr.execute('select id from ir_ui_view where model=%s and name=%s', ('cmc.call.history', 'view_cmc_call_history_tree'))
    view_res = cr.fetchone()
    return  {
            'domain': "[('allocated_user_id','=',%d), ('state', '=', 'allocated')]" % (uid),
            'name': 'Calls Allocated to Me',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.call.history',
            'view_id': view_res,
            'type': 'ir.actions.act_window',
            'context': {'user_id':uid}
            }


class wizard_cmc_my_call_tree(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _my_calls, 'state':'end'}
            }
    }       

wizard_cmc_my_call_tree('wizard_cmc_my_call_tree')

def _my_calls_calendar(self, cr, uid, data, context):
    return  {
            'domain': "[('allocated_user_id','=',%d)]" % (uid),
            'name': 'Calendar: Calls Allocated to Me',
            'view_type': 'form',
            'view_mode': 'calendar,form',
            'res_model': 'cmc.call.history',
            'view_id': False,
            'type': 'ir.actions.act_window',
            }


class wizard_cmc_my_call_calendar(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _my_calls_calendar, 'state':'end'}
            }
    }       

wizard_cmc_my_call_calendar('wizard_cmc_my_call_calendar')
