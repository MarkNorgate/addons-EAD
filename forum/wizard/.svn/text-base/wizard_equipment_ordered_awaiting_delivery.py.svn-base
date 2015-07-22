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


def _my_equipment(self, cr, uid, data, context):
    query="select id from cmc_ordered_equipment_master where state='Ordered'"
    cr.execute(query)
    ids = cr.fetchall()
    debug(ids)
    cr.execute("select view_id from ir_act_window where name='Equipment on order'")
    view= cr.fetchall()
    debug(view)
    return  {
            
            'name': 'Equipment on order',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.ordered.equipment.master',
            'view_id': view[0],
            'type': 'ir.actions.act_window',
            'domain': "[('id','in',%s)]" % str(ids),
            }


class wizard_cmc_ilme_group_equipment_ordered_awaiting_delivery(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _my_equipment, 'state':'end'}
            }
    }       

wizard_cmc_ilme_group_equipment_ordered_awaiting_delivery('wizard_cmc_ilme_group_equipment_ordered_awaiting_delivery')