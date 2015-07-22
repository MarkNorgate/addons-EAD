import wizard
import time
from tools.misc import debug
import string
from string import Template
import pooler
import base64

class wizard_car_assessment(wizard.interface):
    def _details(self, cr, uid, data, context):
        debug('==== DATA INFO PACK LETTER ====')
        prev_record = pooler.get_pool(cr.dbname).get('cmc.assessment').browse(cr, uid, int(data['ids'][0]))
        if prev_record.is_client:
            if prev_record.client_person_id.first_name :
                person_id = prev_record.client_person_id
        else:
            raise except_orm('Error','Following Assessment Has no Client')
            
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
            
        data['form']['location']=False
        data['form']['name']=person_id.display_name
        data['form']['birth_date']=person_id.birth_date
        data['form']['diagnosis']=prev_record.diagnosis if prev_record.diagnosis else False
        data['form']['assessment_date']=prev_record.assessment_date
        data['form']['owner']=prev_record.owner if prev_record.owner else False
        
        return data['form']
    
    states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print', 'report':'car.assessment', 'state':'end'}
            }
            
        
    }

wizard_car_assessment('car.assessment.wizard')
