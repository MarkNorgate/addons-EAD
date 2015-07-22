import wizard
import time
from tools.misc import debug
import string
import pooler
import base64
from operator import itemgetter
import datetime
from StringIO import StringIO
import tools
from osv import fields, osv
from osv.orm import except_orm
report=False
class wizard_ilme_mobility_enviromental_forms(wizard.interface):
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
        debug('==== DATA PRINT ASSESSMENT PACK ====')
        report='print.assessment.paperwork'
        template_name=context.get('paperwork')
        event_start = False
        prev_record = pooler.get_pool(cr.dbname).get('cmc.assessment').browse(cr, uid, int(data['ids'][0]))
        cr.execute('select a.id from cmc_appointments a ' \
                   'inner join cmc_assessment assmt on assmt.id = a.assessment_id ' \
                   'where a.state = \'active\' and assmt.id = %d' % (int(data['ids'][0])))
        appt_ids = map(itemgetter(0), cr.fetchall())
        debug(appt_ids)
        try:
            appt_record = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, appt_ids[0])
            cr.execute('select user_id from user_appointment_rel where appointment_id = %d' % (appt_record.id))
        except:
            appt_record=False
            
        if prev_record.driving_assessment_type:
            user_ids = map(itemgetter(0), cr.fetchall())
            user_record = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, user_ids)
            license_status = driver_number = dlva_informed = dlva_date_informed = False
            location = prev_record.where
            mobility_component = 'Y' if prev_record.component == 'high_rate' else 'N'
            license_status = prev_record.type_lincense
            driver_number = prev_record.driver_number
            dlva_informed = 'Y' if prev_record.b_dlva_informed else 'N'
            if prev_record.is_client:
                if prev_record.client_person_id.display_name:
                    person_id = prev_record.client_person_id
                    agent_id=prev_record.agent_person_id
                else:
                    raise except_orm('Warning','No Client')
            address1 = person_id.address_line_1
            address2 = person_id.address_line_2
            add = False
            if address1 :
                add = address1
            elif address2 :
                add = address2
            elif address1 and address2 :
                add = address1 + ',' + address2
            postcode = person_id.postcode
            telephone = person_id.telephone
            email = person_id.email_address
            pooler.get_pool(cr.dbname).get('cmc.assessment.communication').create(cr, uid, {
                     'comm_date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                     'assessment_id':prev_record.id,
                     'type':self.driving_name(prev_record.driving_assessment_type),
                     'client_name':prev_record.person_id.id,
                     'user_id':uid,
                     'subject':'Assessment Paperwork(' + self.driving_name(prev_record.driving_assessment_type) + ')',
                     'message':'Assessment Paperwork Printed'
                    })
            
            data['form']['type'] = self.driving_name(prev_record.driving_assessment_type)
            data['form']['name'] = person_id.display_name
            data['form']['event_start'] = event_start if event_start else ""
            data['form']['address'] = add if add else ""
            data['form']['telephone'] = telephone
            data['form']['email'] = email if email else ""
            data['form']['location'] = location if location else ""
            data['form']['birth_date'] = datetime.datetime.strptime(person_id.birth_date , '%Y-%m-%d').strftime('%d %B %Y') if person_id.birth_date else "" 
            data['form']['mobility_component'] = mobility_component if mobility_component else ""
            data['form']['license_status'] = license_status if license_status else ""
            data['form']['driver_number'] = driver_number if driver_number else "" 
            data['form']['dvla_informed'] = dlva_informed
            data['form']['ethnicity'] = person_id.ethnicity if person_id.ethnicity else ""
            data['form']['start_date'] = appt_record.apmnt_start_date if appt_record else ""
            data['form']['owner'] = appt_record.owner.name if appt_record else ""
            data['form']['assessment_date']=datetime.datetime.strptime(apmnt_start_date , '%Y-%m-%d').strftime('%d %B %Y') if appt_record else ""
            data['form']['agent_name']=agent_id.display_name if agent_id.display_name else ""
            data['form']['dvla_date']=prev_record.dlva_date if prev_record.dlva_date else ""
            data['form']['diagnosis']=prev_record.diagnosis if prev_record.diagnosis else ""
            data['form']['town']=prev_record.city if prev_record.city else ""
            data['form']['county']=prev_record.county if prev_record.county else ""
            data['form']['postcode']=prev_record.postcode if prev_record.postcode else ""
            persons = []
            debug(user_record)
            for user in user_record:
                persons.append(user.name)
            data['form']['persons'] = ','.join(persons) if len(persons) >0 else ""
            
        return data['form']
    states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print', 'report':'ilme.mobility.enviromental.form', 'target':'new', 'state':'end'}
            }
    }
wizard_ilme_mobility_enviromental_forms('wizard_ilme_mobility_enviromental_forms')
