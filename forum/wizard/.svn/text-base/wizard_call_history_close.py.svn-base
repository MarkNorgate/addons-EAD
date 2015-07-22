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


def _close_call(self, cr, uid, data, context):
    debug(data)
    user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid)
    call = pooler.get_pool(cr.dbname).get('cmc.call.history').browse(cr, uid, int(data['id']))
    pooler.get_pool(cr.dbname).get('cmc.call.history').write(cr, uid, int(data['id']),{'state':'closed', 'allocated_user_id': None, 'allocated_user_group_id': None})
    pooler.get_pool(cr.dbname).get('cmc.call.comments').create(cr, uid, {
             'date_time':datetime.datetime.now(),
             'user_id': uid,
             'comments': 'Call closed by ' + user.name,
             'call_id':int(data['id']),
    })
    pooler.get_pool(cr.dbname).get('cmc.user.activity').create(cr, uid, {
                     'date':datetime.datetime.now(),
                     'user_id': uid,
                     'activity':'Call closed by ' + user.name,
                     'type':'closed call',
                     'client_id':call.client_id.id,
                     'agent_id':call.agent_id.id,
                     'call_id':int(data['id']),
                     })
    
    cr.execute('select id, name from ir_ui_view where model=%s and name=%s', ('cmc.call.history', 'view_cmc_my_call_tree'))
    view_res = cr.fetchone()
    debug(uid)
    if context.get('_terp_view_name',False):
        return {
                'type': 'ir.actions.act_url',
                'url':'/menu',
                'target': '_top'
                }
    else:
        return  {
            'domain': "[('allocated_user_id','=',%d)]" % (uid),
            'name': 'Calls Allocated to Me',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.call.history',
            'view_id': view_res,
            'type': 'ir.actions.act_window',
            'context': {'user_id':uid,'call_completed_close':'close'}
            }
    #===========================================================================
    # return  {
    #            'domain': "[]",
    #            'name': 'Find a Person or Organisation',
    #            'view_type': 'form',
    #            'res_model': 'cmc.person',
    #            'view_mode': 'form,tree',
    #            'res_id': int(call.client_id.id if call.client_id.id else call.agent_id.id),
    #            'view_id': False,
    #            'type': 'ir.actions.act_window'
    #            }
    #===========================================================================
    #===========================================================================
    # return  {
    #        'domain': "[('allocated_user_id','=',%d)]" % (uid),
    #        'name': 'Calls Allocated to Me',
    #        'view_type': 'form',
    #        'view_mode': 'tree,form',
    #        'res_model': 'cmc.call.history',
    #        'view_id': view_res,
    #        'type': 'ir.actions.act_window',
    #        'context': {'user_id':uid,'call_completed_close':'close'}
    #        }
    #===========================================================================


class wizard_call_history_close(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _close_call, 'state':'end'}
            }
    }       

wizard_call_history_close('wizard_call_history_close')
