import wizard
import time
from tools.misc import debug
import string
from string import Template
import pooler
import base64


class wizard_passenger_assessment(wizard.interface):
    
    def driving_name(self,driving_type):
         t = {
            'general':'GENERAL',
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
         return t.get(driving_type, False)
    
    def location(self,location):
        l={'cornwall':'Cornwall Mobility Centre, Truro',
        'mount_gould': 'Mount Gould Hospital, Plymouth',
        'holsworthy': 'Holsworthy Hospital, Holsworthy, Devon',
        'exeter': 'Exeter Mobility Centre, Exeter',
        'echo': 'Echo Centre, Liskeard'}
        return l.get(location,False)
    def title(self,title):
        t={
            'dr': 'Dr',
            'mr':'Mr',
            'ms':'Miss',
            'Ms':'Ms',
            'mrs':'Mrs',
            'other':'Other'
            }
        return t.get(title,False)
    def _details(self, cr, uid, data, context):
        debug('==== PASSENGER PAPERWORK ====')
        prev_record = pooler.get_pool(cr.dbname).get('cmc.assessment').browse(cr, uid, int(data['ids'][0]))
        if prev_record.person_id:
            person_id = prev_record.client_person_id
            
        address1 = person_id.address_line_1
        address2 = person_id.address_line_2
        add=False
        if address1 :
            add=address1
        elif address2 :
            add=address2
        elif address1 and address2 :
            add=address1+','+address2
        postcode = person_id.postcode
        telephone = person_id.telephone
        email = person_id.email_address
        agent_name=False
        if prev_record.paying == 'agent_paying':
            agent_name=prev_record.agent_person_id.display_name
        license_status=prev_record.type_lincense
        driver_number=prev_record.driver_number
        states = ['currently_driving', 'currently_driving_past', 'never_driven','driving_lessons_current']
        for st in states:
                if prev_record.driving_experience == st:
                    data['form'][st]='Yes'
                else:
                    data['form'][st]='No'
                    
        data['form']['id']=person_id.person_id
        data['form']['type']=self.driving_name(prev_record.driving_assessment_type)
        data['form']['location']=self.location(prev_record.where)
        data['form']['name']=person_id.display_name
        data['form']['date_birth']=person_id.birth_date
        data['form']['license_status']=license_status
        data['form']['driver_number']=driver_number 
        data['form']['ethnicity']=person_id.ethnicity if person_id.ethnicity else False
        data['form']['glass_required']='Yes' if prev_record.corrective_lense else 'No'
        data['form']['is_dvla_component']='Yes' if prev_record.b_dlva_informed else 'No'
        data['form']['diagnosis']=prev_record.diagnosis if prev_record.diagnosis else False
        data['form']['address'] = add
        data['form']['telephone']=telephone if telephone else False
        data['form']['assessment_date']=prev_record.assessment_date if prev_record.assessment_date else False 
        data['form']['owner']=prev_record.owner if prev_record.owner else False
        data['form']['agent_paying_name']=agent_name
        
        return data['form']
    
    states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print', 'report':'passenger.assessment', 'state':'end'}
            }
            
        
    }

wizard_passenger_assessment('passenger.assessment.wizard')
