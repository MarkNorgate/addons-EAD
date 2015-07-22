import wizard
import time
from tools.misc import debug
import string
import pooler
import base64
import datetime

class wizard_pending_assessment_agent(wizard.interface):
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
        prev_record = pooler.get_pool(cr.dbname).get('cmc.assessment').browse(cr, uid, int(data['ids'][0]))
        debug(prev_record)
        if prev_record.agent_person_id:
            person_id=prev_record.client_person_id
            data['form']['title'] = (self.title(person_id.title) if person_id.title!='other' else person_id.title_other) if person_id.title else ""
            data['form']['last_name'] = person_id.last_name
            data['form']['first_name'] = person_id.first_name if person_id.first_name else person_id.organisation_name
            data['form']['date_birth'] =datetime.datetime.strptime( person_id.birth_date , '%Y-%m-%d').strftime('%d %B %Y') if person_id.birth_date else "" 
            data['form']['ethnicity'] = person_id.ethnicity
            data['form']['telephone'] = person_id.telephone if person_id.telephone else ""
            data['form']['address_line1'] = person_id.address_line_1 if person_id.address_line_1 else "" 
            data['form']['address_line2'] = person_id.address_line_2 if person_id.address_line_2 else ""
            data['form']['email'] = person_id.email_address if person_id.email_address else "" 
            data['form']['postcode'] = person_id.postcode if person_id.postcode else ""
        else:
            raise except_orm('Agent Error','This Assessment has no Agent')
        debug(data)
        return data['form']
    states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print',
                       'report':'pending.assessment.agent',
                       'target':'new',
                       'state':'end'}
            },
    }

wizard_pending_assessment_agent('pending.send.information.pack.agent')
