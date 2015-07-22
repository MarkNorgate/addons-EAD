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

class wizard_recieved_equipment(wizard.interface):
    _action_detail = '''<?xml version="1.0"?>
    <form string="Action Entry">
                    <newline />
                    <group colspan="4" string="Tracking">
                            <field colspan="1" name="asset_type"  />
                            <newline />
                            <field colspan="1" name="serial_no"  />
                            <newline />
                            <field colspan="1" name="onwer_asset_no" />
                            <newline />
                            
                    </group>
                </form>'''
    _action_fields = {
        'serial_no': {'type':'char', 'string':'Serial No', 'size':100},
        'onwer_asset_no': {'type':'char', 'string':'Asset Number', 'size':100},
        'size': {'type':'char', 'string':'Size', 'size':100},
        'color': {'type':'char', 'string':'Color', 'size':100},
        'asset_type': {'type':'selection',
                         'selection':[('Wheelchair Manual SP-Basic Manual','Wheelchair Manual SP-Basic Manual'),
                                       ('Wheelchair Manual SP-Manual with seating system','Wheelchair Manual SP-Manual with seating system'),
                                       ('Wheelchair Manual TR-Basic Manual','Wheelchair Manual TR-Basic Manual'),
                                       ('Wheelchair Manual TR-Manual with seating system','Wheelchair Manual TR-Manual with seating system'),
                                       ('Powerhubs','Powerhubs'),
                                       ('Wheelchair powered-Basic', 'Wheelchair powered-Basic'),
                                       ('Powerpack-User controllable','Powerpack-User controllable'),
                                       ('Powerpack-Attendant controllable','Powerpack-Attendant controllable'), 
                                        ('Wheelchair Powered - With electric seating', 'Wheelchair Powered - With electric seating'),
                                        ('Wheelchair Powered - Stand up', 'Wheelchair Powered - Stand up'),
                                       ('Walking Aid', 'Walking Aid'),
                                       ('Scooter-Boot', 'Scooter-Boot'),
                                       ('Scooter-Mid Size', 'Scooter-Mid Size'),
                                       ('Scooter-Large Size', 'Scooter-Large Size'),
                                       ('Powerhubs', 'Powerhubs'),
                                       ('Bath Lift-Portable', 'Bath Lift-Portable'),
                                       ('Bath Lift-Fixed', 'Bath Lift-Fixed'),
                                       ('Riser Recliner', 'Riser Recliner'),
                                       ('Wheeled Walker', 'Wheeled Walker'),
                                       ('Hoist-Portable', 'Hoist-Portable'),
                                       ('Hoist-Fixed', 'Hoist-Fixed'),
                                       ('Hoist-Overhead', 'Hoist-Overhead'),
                                       ('Bed-Manual', 'Bed-Manual'),
                                       ('Bed-Electric', 'Bed-Electric'),
                                       ('Other','Other')
                          ],'string':'Asset Type'},
    }
    def _save(self, cr, uid, data, context):
        debug(data)
        debug(context)
        id=data['id']
        table_name=data['model']
        ss=pooler.get_pool(cr.dbname).get(table_name).browse(cr,uid,id)
        data['form']['make']=ss.make
        data['form']['model']=ss.model
        data['form']['state']='in_stock'
        data['form']['manufacture_date']=datetime.datetime.now().strftime("%Y-%m-%d")
        data['form']['order_no']=ss.order_no
        data['form']['price']=ss.price
        data['form']['owner']=ss.owner.id
        data['form']['current_user_id']=ss.owner.id
        data['form']['size']=ss.size
        data['form']['color']=ss.color
        
        equipment_id=pooler.get_pool(cr.dbname).get('cmc.equipment').create(cr, uid, data['form'])
        debug(equipment_id)
        if equipment_id:
            query="insert into equipment_equipment_rel values("+str(ss.equipment_supply_process_id.id)+','+str(equipment_id)+")"
            debug(query)
            cr.execute(query)
            update_query="update cmc_equipment set state='booked' where id="+str(equipment_id)
            cr.execute(update_query)
            pooler.get_pool(cr.dbname).get(table_name).write(cr,uid,[id],{'color':data['form']['color'],'serial_no':data['form']['serial_no'],'state':'Recieved'})
            debug(equipment_id)
        debug(ss)
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

wizard_recieved_equipment('wizard_recieved_equipment')

