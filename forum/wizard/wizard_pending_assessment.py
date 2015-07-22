import wizard
import time
from tools.misc import debug
import string
import pooler
import base64

class wizard_pending_assessment(wizard.interface):
    def title(self, title):
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
        debug('====DATA PENDING ASSESSMENT ====')
        prev_record = pooler.get_pool(cr.dbname).get('cmc.enquiry').browse(cr, uid, int(data['ids'][0]))
        debug(prev_record)
        states = ['full_driving_assessment', 'adaptations_assessment', 'wheelchair_assessment', 'drive_from_wheelchair_assessment', 'passenger_assessment', 'car_assessment']
        for st in states:
            if prev_record.enquiry_type == st:
                debug(st)
                data['form'][st] = 'Y'
            else:
                data['form'][st] = ""
        person_id=prev_record.person_id
        data['form']['title'] = (self.title(person_id.title) if person_id.title!='other' else person_id.title_other) if person_id.title else ""
        data['form']['last_name'] = person_id.last_name
        data['form']['first_name'] = person_id.first_name if person_id.first_name else person_id.organisation_name 
        data['form']['date_of_birth'] = person_id.birth_date if person_id.birth_date else ""
        data['form']['ethnicity'] = person_id.ethnicity if person_id.ethnicity else ""
        data['form']['telephone'] = person_id.telephone if person_id.telephone is not None else ""
        data['form']['address_line1'] = person_id.address_line_1 if person_id.address_line_1 is not None else "" 
        data['form']['address_line2'] = person_id.address_line_2 if person_id.address_line_2 is not None else ""
        data['form']['email'] = person_id.email_address if person_id.email_address else "" 
        data['form']['postcode'] = person_id.postcode if person_id.postcode else ""
        return data['form']
    states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print',
                       'report':'pending.assessment',
                       'target':'new',
                       'state':'end'}
            },
    }

wizard_pending_assessment('pending.send.information.pack')
