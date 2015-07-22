import wizard
import time
from tools.misc import debug
import string
from string import Template
import pooler
import base64
import datetime
from operator import itemgetter


class wizard_client_invoice(wizard.interface):
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
        debug('==== DATA INFO PACK CHASE UP LETTER ====')
        debug(data)
        prev_record = pooler.get_pool(cr.dbname).get('cmc.assessment').browse(cr, uid, int(data['id']))
        person_id=prev_record.client_person_id
        data['form']['invoice_no']=prev_record.invoice_no if prev_record.invoice_no else "" 
        data['form']['name']=person_id.display_name
        data['form']['address_line1'] = person_id.address_line_1 if person_id.address_line_1 else ""
        data['form']['address_line2'] = person_id.address_line_2 if person_id.address_line_2 else ""
        data['form']['address_line3'] = (person_id.city if person_id.city else "")+' '+(person_id.county if person_id.county else "")
        data['form']['person_id'] = person_id.person_id
        data['form']['type']=self.driving_name(prev_record.driving_assessment_type)
        data['form']['date']=""
        data['form']['location']=""
        cr.execute('select a.id from cmc_appointments a ' \
                   'inner join cmc_assessment assmt on assmt.id = a.assessment_id ' \
                   'where a.state = \'active\' and assmt.id = %d' % (int(data['ids'][0])))
        appt_ids = map(itemgetter(0), cr.fetchall())
        if len(appt_ids) >0:
            appt_record = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, appt_ids[0])
            start_date_time=appt_record.apmnt_start_date_time.split(" ")
            start_time=datetime.datetime.strptime(start_date_time[0], '%Y-%m-%d').strftime('%d-%B-%Y')
            data['form']['date'] = (start_time if appt_record else "")
            data['form']['location'] = appt_record.location if appt_record.location else "" 
        data['form']['total_cost']=prev_record.total_cost 
        pooler.get_pool(cr.dbname).get('cmc.assessment').write(cr, uid, int(data['id']),{'invoice_status':'Invoice Sent'},{'invoice':'client'})
        pooler.get_pool(cr.dbname).get('cmc.assessment.communication').create(cr, uid, {
                 'comm_date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 'assessment_id':prev_record.id,
                 'type':self.driving_name(prev_record.driving_assessment_type),
                 'user_id':uid,
                 'client_name':prev_record.person_id.id,
                 'subject':'Invoice',
                 'message':'Invoice to Client Posted'
                })
        return data['form']
    
    states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print', 'report':'client.invoice', 'state':'end'}
            }
            
        
    }

wizard_client_invoice('wizard.client.invoice')
