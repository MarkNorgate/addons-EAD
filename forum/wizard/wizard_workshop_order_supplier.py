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


class wizard_workshop_order_supplier(wizard.interface):
    _call_history_detail = '''<?xml version="1.0"?>
    <form string="Part Ordered List">
                    <group colspan="2" col="2">
                        <field name="workshop_id" invisible="1"/>
                        <field name="part_ordered" domain="[('workshop_id','=',workshop_id)]"/>
                    </group>
    </form>'''
    
    _call_history_fields = {
        'workshop_id':{'type':'many2one','relation':'cmc.workshop.process','string':'Workshop Id','readonly':True},
        'part_ordered': {'type':'many2many','relation':'cmc.workshop.part.ordered','string':'Part Ordered','readonly':False}
    }
    def _order_details(self, cr, uid, data, context):
        debug(context)
        data['form']['workshop_id']=data['id']
        pool = pooler.get_pool(cr.dbname)
        picking_obj = pool.get('cmc.workshop.part.ordered')
        ids=picking_obj.search(cr, uid, [('workshop_id', '=', data['id'])])
        if len(ids)==0:
            raise except_orm('Warning','This record has no part ordered')
        debug(data)
        return data['form']
    
    def _save(self, cr, uid, data, context):
        if len(data['form']['part_ordered'][0][2])>1 or len(data['form']['part_ordered'][0][2])<1:
            raise except_orm('Warning','Please Select One supplier')
        debug(data)
        return data['form']
    
    def _go_to_menu(self, cr, uid, data, context):
        return {
            'name': 'Ordered Form',
            'type': 'ir.actions.wizard',
            'wiz_name': "wizard_workshop_service_repair_order",
            }
    states = {
        'init': {
            'actions': [_order_details],
            'result': {'type':'form',
                       'arch':_call_history_detail,
                       'fields':_call_history_fields,
                       'state':[
                                ('end', 'Cancel'),
                                ('save', 'Proceed'),
                                ]}
        },
        'save': {
            'actions': [_save],
            'result': {'type': 'action', 'action': _go_to_menu, 'state':'end'}

        }
    }
    
wizard_workshop_order_supplier('wizard_workshop_order_supplier')
