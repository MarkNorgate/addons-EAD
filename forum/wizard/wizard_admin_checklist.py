import wizard
import time
from tools.misc import debug
import string
from string import Template
import pooler
import base64
import datetime

class wizard_admin_checklist(wizard.interface):
     def driving_name(self, type):
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
        return t.get(type, False)
    
     def _details(self, cr, uid, data, context):
        debug('==== DATA ADMIN CHEKLIST ====')
        debug(data)
        
        prev_record = pooler.get_pool(cr.dbname).get('cmc.assessment').browse(cr, uid, int(data['ids'][0]))
        
        if prev_record.client_person_id.display_name:
            person_id = prev_record.client_person_id
        else:
            person_id = prev_record.agent_person_id
        pooler.get_pool(cr.dbname).get('cmc.assessment.communication').create(cr, uid, {
                 'comm_date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 'assessment_id':prev_record.id,
                 'type':self.driving_name(prev_record.driving_assessment_type),
                 'client_name':prev_record.person_id.id,
                 'user_id':uid,
                 'subject':'Admin Checklist Printed',
                 'message':'Admin Checklist Printed'
                })
        diagnosis = prev_record.diagnosis if prev_record.diagnosis else False
        not_days = prev_record.days_not_available if prev_record.days_not_available else False
        names = person_id.display_name
#        if prev_record.enquiry_id.user_id.name:
#             names += ',' + prev_record.enquiry_id.user_id.name
        data['form']['type'] = self.driving_name(prev_record.driving_assessment_type)
        data['form']['name'] = person_id.display_name
        data['form']['diagnosis'] = diagnosis if diagnosis else "" 
        data['form']['not_days'] = not_days if not_days else "" 
        data['form']['location'] = prev_record.where if prev_record.where else "" 
        data['form']['names'] = ""
        data['form']['date'] = ""
        data['form']['time'] = ""
        if prev_record.payment_date != False:
            data['form']['payment_received'] = datetime.datetime.strptime(prev_record.payment_date, '%Y-%m-%d').strftime('%d-%m-%Y') if prev_record.payment_received else 'No'
        else:
            data['form']['payment_received'] = ""
        data['form']['nearest_location']=prev_record.where if prev_record.where else ""
        data['form']['ot']='Y' if prev_record.cognitive_referral else 'N'
        data['form']['agent_name']=prev_record.agent_person_id.display_name if prev_record.agent_person_id.display_name else "" 
        return data['form']
    
     states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print', 'report':'admin.checklist', 'state':'end'}
            }
            
        
    }

wizard_admin_checklist('admin.checklist.wizard')
