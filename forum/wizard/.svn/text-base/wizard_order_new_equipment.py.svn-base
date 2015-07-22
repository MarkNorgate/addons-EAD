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

class wizard_order_new_equipment(wizard.interface):
    _action_detail = '''<?xml version="1.0"?>
    <form string="Action Entry">
                    <newline />
                    <group colspan="4" string="Tracking">
                            <field colspan="1" name="make"  />
                            <newline />
                            <field colspan="1" name="model" />
                            <newline />
                            <field colspan="1" name="size" />
                            <newline />
                            <field colspan="1" name="color" />
                            <newline />
                            <field colspan="1" name="price" />
                            <newline />
                            <field colspan="1" name="owner_id" />
                            
                    </group>
                </form>'''
    _action_fields = {
        'make': {'type':'char', 'string':'Make', 'size':100},
        'model': {'type':'char', 'string':'Model', 'size':100},
        'color': {'type':'char', 'string':'Colour', 'size':100},
        'size': {'type':'char','string':'Size','size':100},
        'price': {'type':'float','string':'Trade Price'},
        'owner_id':{'type':'many2one','relation':'cmc.person','string':'Owner'}
    }
    def _save(self, cr, uid, data, context):
        debug(data)
        debug(context)
        data['form']['equipment_supply_process_id']=data['id']
        data['form']['state']='Ordered'
        data['form']['date_ordered']=datetime.datetime.now().strftime("%Y-%m-%d")
        if not data['form']['owner_id']:
            data['form']['owner']=context.get('client_id',False)
        else:
            data['form']['owner']=data['form']['owner_id']
        enquiry_id = pooler.get_pool(cr.dbname).get('cmc.ordered.equipment.master').create(cr, uid, data['form'],context)
        return data['form']
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form',
                       'arch':_action_detail,
                       'fields':_action_fields,
                       'state':[('save','Save'),
                                ('end','Cancel')]}
            },
        'save': {
            'actions': [_save],
            'result': {'type': 'state','state':'end'}
        }
    }       

wizard_order_new_equipment('wizard_order_new_equipment')

