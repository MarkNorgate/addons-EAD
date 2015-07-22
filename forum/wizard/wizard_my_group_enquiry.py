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


def _my_group_enquiries(self, cr, uid, data, context):
    name='Administrator'
#    This to keep in mind these id are harcoded
    cr.execute("select name from ir_ui_menu where id='%s'" % (data['id']))
    view_res = cr.fetchone()
    group_name=view_res[0]
    if group_name=='Reception Actions':
        name='Mobility Reception User'
    elif group_name=='ADI Actions':
        name='Mobility ADI User'
    elif group_name=='ILME Actions':
        name='Mobility ILME User'
    elif group_name=='Workshop Actions':
        name='Mobility Workshop User'
    elif group_name=='Adaptations Actions':
        name='Mobility Adaptations User'
    #fetch all ids with no 
    q = "select id from cmc_enquiry \
        where allocated_user_group_id in (select id from res_groups where name='%s') \
        and (state=\'pending\' or state=\'awaiting\')"
    cr.execute(q %(name))
    ids = cr.fetchall()
    return  {
            'domain': "[('id','in',%s)]" % str(ids),
            'name': 'Actions Allocated to My Group',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.enquiry',
            'view_id': False,
            'type': 'ir.actions.act_window'
            }


class wizard_cmc_my_group_enquiry_tree(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _my_group_enquiries, 'state':'end'}
            }
    }       

wizard_cmc_my_group_enquiry_tree('wizard_cmc_my_group_enquiry_tree')
