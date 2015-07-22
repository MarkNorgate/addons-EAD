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


def _print_send_information_pack(self, cr, uid, data, context):
    debug("I AM IN PRINT IFORMATION PACK")
    debug(context)
    return  {
            'domain': """[('state', '=', 'pending'),
                        ('enquiry_type','!=','general')]""",
            'name': 'Print and Send Information Pack',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.enquiry',
            'view_id': False,
            'type': 'ir.actions.act_window'
            }


class wizard_cmc_print_information_pack_tree(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _print_send_information_pack, 'state':'end'}
            }
    }       

wizard_cmc_print_information_pack_tree('wizard_cmc_print_information_pack_tree')
