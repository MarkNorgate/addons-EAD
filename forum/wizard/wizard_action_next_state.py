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


class wizard_action_next_state(wizard.interface):
    
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
    }
    
    def drving_name(self, type):
        t = {
            'general':'GENERAL',
            'full_driving_assessment': 'Full Driving Assessment',
            'wheelchair_assessment':'Wheelchair Assessment',
            'drive_from_wheelchair_assessment':'Drive From Wheelchair Assessment',
            'passenger_assessment':'Passenger Assessment',
            'car_seat_harness_assessment':'Car Seat Harness Assessment',
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
    
    
    def _initial_details(self, cr, uid, data, context):
        debug(cr)
        debug(uid)
        debug(data)
        debug(context)
        debug(cr.dbname)
        debug(context.get('assessment_type'))
        if not context.get('assessment_type'):
            raise except_orm('Warning','Assessment Type Error')
        data['form']['type']=context.get('assessment_type')
        data['form']['type_name']=self.drving_name(data['form']['type'])
        return data['form']
    
    def _save(self, cr, uid, data, context):
        debug(self)
        pooler.get_pool(cr.dbname).get('cmc.enquiry').write(cr, uid, int(data['id']), {'state':'closed'}, context=context)
        seq_id = pooler.get_pool(cr.dbname).get('ir.sequence').search(cr, uid, [('name', '=', 'CMC Assessment')])[0]
        new_id = pooler.get_pool(cr.dbname).get('ir.sequence').get_id(cr, uid, seq_id)
        ref_id = str(new_id)
        enquiries = pooler.get_pool(cr.dbname).get('cmc.enquiry').browse(cr, uid, int(data['id']))
        enquiry=enquiries
        enquiry_id = enquiry.id
        driving = enquiry.enquiry_type
        state_id=data['form']['state']
        search_state=pooler.get_pool(cr.dbname).get('cmc.assessment.state').browse(cr,uid,state_id)
        if enquiry.is_dvla:
            referrer_type='dvla'
        elif enquiry.is_client:
            referrer_type='client_family'
        data['form']['total_cost']=0;
        price_id=pooler.get_pool(cr.dbname).get('cmc.assessment.price').search(cr, uid, [('type', '=',driving)])
        if len(price_id) >0:
            price_browse=pooler.get_pool(cr.dbname).get('cmc.assessment.price').browse(cr, uid, price_id[0])
            data['form']['total_cost']=price_browse.price
        id = pooler.get_pool(cr.dbname).get('cmc.assessment').create(cr, uid, {
                 'ref_id':ref_id,
                 'agent_person_id':enquiry.agent_id.id if enquiry.agent_id.id else None,
                 'client_person_id':enquiry.client_id.id if enquiry.client_id.id else None,
                 'person_id':enquiry.person_id.id,
                 'enquiry_id':enquiry.id,
                 'enquiry_details':enquiry.enquiry_details,
                 'paying':enquiry.paying,
                 'driving_assessment_type':driving,
                 'assessment_date': datetime.datetime.now(),
                 'state':state_id,
                 'is_agent':enquiry.is_agent,
                 'is_client':enquiry.is_client,
                 'is_dvla':enquiry.is_dvla,
                 'referrer_type':referrer_type,
                 'appointment_letters':'New appointment letter to Client post',
                 'total_cost':data['form']['total_cost']
                })
        person = False
        person=enquiry.person_id
        id = int(id)
        debug(person.id)
        pooler.get_pool(cr.dbname).get('cmc.assessment.communication').create(cr, uid, {
                 'comm_date':datetime.datetime.now(),
                 'assessment_id':id,
                 'type':self.drving_name(driving),
                 'client_name':enquiry.person_id.id,
                 'user_id':uid,
                 'subject':'Assessment Record Created with ' + ref_id,
                 'message':'State Changed to '+search_state.name
                })
        return {}
    
    
    def _go_to_menu(self, cr, uid, data, context):
        debug(uid)
        return  {
            'name': 'Action Records',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'cmc.enquiry',
            'view_id': False,
            'type': 'ir.actions.act_window',
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
    
wizard_action_next_state('action_next_state_assessment')
