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
    query="select id from cmc_equipment where state='booked' and is_external=False"
    cr.execute(query)
    ids = cr.fetchall()
    debug(ids)
    cr.execute("select view_id from ir_act_window where name='All ILME Assessment Records'")
    view= cr.fetchall()
    cr.execute("select view_id from ir_act_window where name='Equipments'")
    view_v= cr.fetchall()
    return  {
            
            'name': 'Equipments in Stock-To Be Delivered',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.equipment',
            'view_id': view_v[0],
            'type': 'ir.actions.act_window',
            'domain': "[('id','in',%s)]" % str(ids),
            }


class wizard_cmc_ilme_group_equipment_in_stock_delivered(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _my_equipment, 'state':'end'}
            }
    }       

wizard_cmc_ilme_group_equipment_in_stock_delivered('wizard_cmc_ilme_group_equipment_in_stock_delivered')