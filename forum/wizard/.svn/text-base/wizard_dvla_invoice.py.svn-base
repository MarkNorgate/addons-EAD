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

class wizard_dvla_invoice(wizard.interface):
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
#        report_id=pooler.get_pool(cr.dbname).get('ir.actions.report.xml').search(cr,uid,[('name', '=', 'Info Pack Chase Up Letter')])[0]
#        report_write=pooler.get_pool(cr.dbname).get('ir.actions.report.xml').write(cr,uid,[report_id],{'report_type':'odt'})
        debug(data)
        prev_record = pooler.get_pool(cr.dbname).get('cmc.assessment').browse(cr, uid, int(data['id']))
#        client = pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, prev_record.client_id)
#        debug('HEllo')
        person_id = prev_record.agent_person_id
        data['form']['advisor']=""
        if prev_record.client_person_id:
            data['form']['name']=prev_record.client_person_id.display_name
        else:
            raise except_orm('Error','DVLA has no Client')
        
        type = False
        type = self.driving_name(prev_record.driving_assessment_type)
        data['form']['invoice_no']=prev_record.invoice_no if prev_record.invoice_no else "" 
        data['form']['person_id'] = prev_record.client_person_id.person_id
        data['form']['reference']=prev_record.agency_reference_id if prev_record.agency_reference_id else "" 
        data['form']['type'] = self.driving_name(prev_record.driving_assessment_type)
        data['form']['location']=prev_record.where if prev_record.where else ''
        #find the active appointment
        data['form']['start_date'] = ''
        if prev_record.appointment_id:
             for appointment in prev_record.appointment_id:
                 if appointment.state=='active':
                     data['form']['start_date']=datetime.datetime.strptime(appointment.apmnt_start_date_time, '%Y-%m-%d %H:%M:%S').strftime('%d-%B-%Y') if appointment.apmnt_start_date_time else ""
        
        data['form']['advisor']=prev_record.enquiry_details
        pooler.get_pool(cr.dbname).get('cmc.assessment.communication').create(cr, uid, {
                 'comm_date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 'assessment_id':prev_record.id,
                 'type':self.driving_name(prev_record.driving_assessment_type),
                 'client_name':prev_record.person_id.id,
                 'user_id':uid,
                 'subject':'Invoice',
                 'message':'Invoice to DVLA Printed'
                })
        return data['form']
    
    states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print', 'report':'dvla.invoice', 'state':'end'}
            }
            
        
    }

wizard_dvla_invoice('wizard.dvla.invoice')
