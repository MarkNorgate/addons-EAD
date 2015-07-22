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


class wizard_final_report_covering_letter(wizard.interface):
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
        prev_record = pooler.get_pool(cr.dbname).get('cmc.assessment').browse(cr, uid, int(data['id']))
#        client = pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, prev_record.client_id)
        debug('HEllo')
        person_id = prev_record.client_person_id
        type = False
        debug(prev_record.paying)
        paying = prev_record.paying
        referrence_no='Our Ref:'+person_id.person_id 
        data['form']['person_id'] = referrence_no
        data['form']['title'] = (self.title(person_id.title)if person_id.title != 'other' else person_id.title_other) if person_id.title else ""
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
            data['form']['title_last_name'] = (self.title(person_id.title) if person_id.title != 'other' else person_id.title_other)+' '+person_id.last_name
        else:
            data['form']['title_last_name'] =person_id.display_name
        data['form']['type'] = type
        data['form']['today'] = datetime.datetime.now().strftime('%d/%m/%Y')
        pooler.get_pool(cr.dbname).get('cmc.assessment.communication').create(cr, uid, {
                 'comm_date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 'assessment_id':prev_record.id,
                 'type':'Assessment Covering Letter',
                 'client_name':prev_record.person_id.id,
                 'user_id':uid,
                 'subject':'Assessment Report Covering Letter',
                 'message':'Assessment Report Covering Letter for Client printed'
                })
        return data['form']
    
    states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print', 'report':'assessment.report.covering.letter.client', 'state':'end'}
            }
            
        
    }

wizard_final_report_covering_letter('wizard_final_report_covering_letter')
