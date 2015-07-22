import wizard
import time
from tools.misc import debug
import string
from string import Template
import pooler
import base64


class wizard_info_pack_letter(wizard.interface):
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
        report_id=pooler.get_pool(cr.dbname).get('ir.actions.report.xml').search(cr,uid,[('name', '=', 'Info Pack Letter')])[0]
        report_write=pooler.get_pool(cr.dbname).get('ir.actions.report.xml').write(cr,uid,[report_id],{'report_type':'odt'})
        debug(data)
        prev_record = pooler.get_pool(cr.dbname).get('cmc.enquiry').browse(cr, uid, int(data['id']))
        client = pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, prev_record.client_id)
        debug('HEllo')
        person_id = prev_record.person_id
        data['form']['message'] = False
        data['form']['footer'] = False
        type = False
        type = prev_record.type
        debug(prev_record.paying)
        paying = prev_record.paying
        
        if paying == 'client_paying' and type == 'client':
            data['form']['message'] = """
                Thank you for your action about having an assessment.
        Please find enclosed an assessment questionnaire, information sheet and leaflets.  
        Please complete and return the questionnaire with the appropriate fee as soon as possible.  When we have received your questionnaire and payment, we will write to you with details of your assessment appointment.
        If you have any queries or need any further information, please let me know.
                """
            data['form']['footer'] = 'Enc: Questionnaire, Information sheet, leaflets'
        elif paying == 'client_paying' and type == 'agent':
            data['form']['message'] = """
                REFERRAL FOR ASSESSMENT 

Thank you for requesting information about our assessment service, which is attached.  

Please arrange for your client to complete and return the attached questionnaire.  As soon as we have received it we will write to your client with details of their assessment appointment.

Yours sincerely

                """
        
                    
        elif paying == 'agent_paying' and type == 'agent' :
            data['form']['message'] = """
                REFERRAL FOR ASSESSMENT 

Thank you for requesting information about our assessment service, which is attached.  

Please arrange for your client to complete and return the attached questionnaire.  As soon as we have received it we will write to your client with details of their assessment appointment.

We will invoice you for the cost of the assessment when it has taken place.

Yours sincerely
        
                """
        elif paying == 'agent_paying' and type == 'client':
            data['form']['message'] = """
            I have received a referral from AGENT AGENCY requesting that we arrange for you to have a driving assessment. 

Please complete the attached questionnaire and return it as soon as possible with the fee for your assessment.  As soon as we have received your questionnaire and payment, we will write to you with details of your assessment appointment.

If you have any queries, please let me know.

            """
        driving_type = False
        
        debug(data['form']['message'])
        data['form']['person_id'] = person_id.person_id
        data['form']['title'] = self.title(person_id.title) if person_id.title != 'other' else person_id.title_other
        data['form']['display_name'] = person_id.display_name 
        data['form']['last_name'] = person_id.last_name
        if person_id.title and person_id.last_name:
            data['form']['title_last_name'] = 'Dear '+(self.title(person_id.title) if person_id.title != 'other' else person_id.title_other)+' '+person_id.last_name
        data['form']['type'] = self.driving_name(prev_record.enquiry_type)
        
        return data['form']
    
    states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print', 'report':'info.pack.letter', 'state':'end'}
            }
            
        
    }

wizard_info_pack_letter('info.pack.letter.wizard')
