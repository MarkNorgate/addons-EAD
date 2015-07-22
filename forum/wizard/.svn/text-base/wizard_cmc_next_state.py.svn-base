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


class wizard_next_state(wizard.interface):
    _detail = '''<?xml version="1.0"?>
    <form string="Assessment State">
                    <group colspan="2" col="2">
                        <field name="type" readonly="1" invisible="1"/>
                        <field name="type_name" readonly="1" /> 
                        <field name="state"  readonly="0" />
                    </group>
    </form>'''
    
    _fields = {
        'type': {'type':'char', 'string':'Type'},
        'type_name': {'type':'char', 'string':'Type'},
        'state':{'type':'many2one', 'relation':'cmc.assessment.state', 'string':'Next State','domain':"[('type','=',type)]",'required':True},
        'no_hours':{'type':'float','string':'Total Number of Hours for this Referral'},
    }
    
    def drving_name(self, type):
        t = {
            'full_driving_assessment': 'FULL DRIVING ASSESSMENT',
            'wheelchair_assessment':'WHEELCHAIR ASSESSMENT',
            'drive_from_wheelchair_assessment':'DRIVE FROM WHEELCHAIR ASSESSMENT',
            'passenger_adult':'Passenger Adult','passenger_child':'Passenger Child',
            'car_seat_harness_assessment':'CAR SEAT HARNESS ASSESSMENT',
            'driving_legal_assessment':'Driving Legal Assessment',
            'drive_safer_for_longer_assessment':'Drive Safer For Longer Assessment',
            'driving_adaptation_assessment':'Driving Adaptation Assessment',
            'mo_map_adapdation_assessment':'MO MAP Adaptation Assessment',
            'review_assessment':'Review Assessment',
            'wheel_walker':'Wheeled Walker',
            'chair_assessment':'Chair Assessment',
            'bathing_assessment':'Bathing Assessment',
            'other_ilme_equipment_assessment':'Other ILME Equipment Assessment',
            'buggy_assessment':'Buggy Assessment',
            'scooter_assessment':'Scooter Assessment',
            'pct_wheelchair_buggy':'PCT Wheelchair/Buggy',
            'hoist_demo':'Hoist Demo',
            'momap_access':'MO MAP Access',
            'pressure_mapping_assessment':'Pressure Mapping Assessment',
            }
        return t.get(type, '')
        return t.get(type, False)
    
    
    def _initial_details(self, cr, uid, data, context):
        data['form']['type']=data['form']['driving_assessment_type']
        data['form']['type_name']=data['form']['type']+"-new"
        return data['form']
    
    def _save(self, cr, uid, data, context):
        data['form']['assessment_date']=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        seq_id = pooler.get_pool(cr.dbname).get('ir.sequence').search(cr, uid, [('name', '=', 'CMC Assessment')])[0]
        new_id = pooler.get_pool(cr.dbname).get('ir.sequence').get_id(cr, uid, seq_id)
        ref_id = str(new_id)
        data['form']['ref_id']=ref_id
        data['form']['appointment_letters']='New appointment letter to Client:IPapptsr'
        data['form']['dummy_appointment']='New appointment letter to Client:IPapptsr'
        pooler.get_pool(cr.dbname).get('cmc.assessment').create(cr, uid, data['form'],context)
        return {}
    
    def _go_to_menu(self, cr, uid, data, context):
        return  {
                'domain': "[]",
                'name': 'Find a Person or Organisation',
                'view_type': 'form',
                'res_model': 'cmc.person',
                'view_mode': 'form,tree',
                'res_id': int(data['id']),
                'view_id': False,
                'type': 'ir.actions.act_window'
                }
    states = {
        'init': {
            'actions': [_initial_details],
            'result': {'type':'form',
                       'arch':_detail,
                       'fields':_fields,
                       'state':[('end', 'Cancel'),
                                ('save', 'Proceed'),
                                ]}
        },
        'save': {
            'actions': [_save],
            'result': {'type': 'action', 'action': _go_to_menu, 'state':'end'}

        },
        
    }
    
wizard_next_state('next_state_assessment')
