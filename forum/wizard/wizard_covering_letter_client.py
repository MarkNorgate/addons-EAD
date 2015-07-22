import wizard
import time
from tools.misc import debug
import string
from string import Template
import pooler
import base64
from osv import fields, osv
from osv.orm import except_orm
import datetime


class wizard_covering_letter_client(wizard.interface):
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
    def title(self,title):
        t = {
            'dr': 'Dr',
            'mr':'Mr',
            'ms':'Miss',
            'Ms':'Ms',
            'mrs':'Mrs',
            'other':'Other'
            }
        return t.get(title, False)
    def _details(self, cr, uid, data, context):
        debug('==== DATA INFO PACK LETTER ====')
        report_value='info.pack.letter'
        prev_record = pooler.get_pool(cr.dbname).get('cmc.assessment').browse(cr, uid, int(data['id']))
#        client = pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, prev_record.client_id)
        debug('HEllo')
        person_id = prev_record.client_person_id
        data['form']['message'] = ""
        data['form']['footer'] = ""
        type = False
        debug(prev_record.paying)
        paying = prev_record.paying
        referrence_no='Our Ref: '+person_id.person_id 
        type=self.driving_name(prev_record.driving_assessment_type)
        if paying == 'client_paying' :
            if (prev_record.agent_person_id):
                #agent referred
                data['form']['message'] =[]
                data['form']['message'].append('I have received a referral from %s requesting that we arrange for you to have a driving assessment.'%(prev_record.agent_person_id.display_name))
                data['form']['message'].append('Please complete the attached questionnaire and return it as soon as possible with the fee for your assessment.  As soon as we have received your questionnaire and payment, we will write to you with details of your assessment appointment.')
                data['form']['message'].append('If you have any queries or need any further information, please let me know.')
                data['form']['footer'] = 'Enc: Questionnaire, Information sheet, leaflets'
            else:
                #self referral
                data['form']['message'] =[]
                data['form']['message'].append('Thank you for your action about having an assessment.')
                data['form']['message'].append('Please find enclosed an assessment questionnaire, information sheet and leaflets.')
                data['form']['message'].append('Please complete and return the questionnaire with the appropriate fee as soon as possible.  When we have received your questionnaire and payment, we will write to you with details of your assessment appointment. If you have any queries or need any further information, please let me know.')
                data['form']['message'].append('If you have any queries or need any further information, please let me know.')
                data['form']['footer'] = 'Enc: Questionnaire, Information sheet, leaflets'
                
        #=======================================================================
        # Agent paying and referred by Agent            
        #=======================================================================
        elif paying == 'agent_paying' :
            referrence_no=""
            type='REFERRAL FOR ASSESSMENT '
            data['form']['message'] =[]
            data['form']['message'].append('Thank you for requesting information about our assessment service, which is attached.')
            data['form']['message'].append('Please arrange for your client to complete and return the attached questionnaire.  As soon as we have received it we will write to your client with details of their assessment appointment.')
            data['form']['message'].append('We will invoice you for the cost of the assessment when it has taken place.')
            #change person id to be agent for addressing to agent
            person_id=prev_record.agent_person_id
            
        data['form']['person_id'] = referrence_no
        data['form']['title'] = (self.title(person_id.title) if person_id.title != 'other' else person_id.title_other) if person_id.title else ""
        data['form']['name'] = person_id.display_name 
        data['form']['last_name'] = person_id.last_name
        data['form']['address'] = []
        if (person_id.address_line_1):
            data['form']['address'].append(person_id.address_line_1)
        if (person_id.address_line_2):
            data['form']['address'].append(person_id.address_line_2)
        if (person_id.city):
            data['form']['address'].append(person_id.city)
        if (person_id.county):
            data['form']['address'].append(person_id.county)
        if (person_id.postcode):
            data['form']['address'].append(person_id.postcode)
        if person_id.title and person_id.last_name:
            data['form']['title_last_name'] = (self.title(person_id.title)if person_id.title != 'other' else person_id.title_other) + ' ' + person_id.last_name
        elif person_id.is_organisation:
            data['form']['title_last_name'] =person_id.display_name
        data['form']['type'] = type
        report_value='info.pack.letter'
        pooler.get_pool(cr.dbname).get('cmc.assessment.communication').create(cr, uid, {
                 'comm_date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 'assessment_id':prev_record.id,
                 'type':self.driving_name(prev_record.driving_assessment_type),
                 'client_name':prev_record.person_id.id,
                 'user_id':uid,
                 'subject':'Info Pack Letter',
                 'message':'Info Pack Sent to Client By Post'
                })
        return data['form']
    
    states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print', 'report':'info.pack.letter', 'state':'end'}
            }
            
        
    }

wizard_covering_letter_client('covering.letter.client.wizard')
