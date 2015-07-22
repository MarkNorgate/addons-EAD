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

class wizard_driving_ax_report(wizard.interface):
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
        debug('==== DATA FINAL REPORT ====')
        debug(data)
        report_type=""
        report_rml=""
        report_template=context.get('report_template',False)
        if not report_template:
            raise except_orm('Warning','Please Select One Template')
        if context:
            prev_record = pooler.get_pool(cr.dbname).get('cmc.assessment').browse(cr, uid, int(data['ids'][0]))
            report_temp_browse = pooler.get_pool(cr.dbname).get('cmc.assessment.report').browse(cr, uid, report_template)
            debug(report_temp_browse)
            if report_temp_browse:
                debug(report_temp_browse.name)
                report_id=pooler.get_pool(cr.dbname).get('ir.actions.report.xml').search(cr, uid, [("name", "=", "Print Assessment Pack")])
                if report_temp_browse.name == 'Standard Report':
                    debug('standard')
                    if prev_record.driving_assessment_type in ['hoist_demo','bathing_assessment','other_ilme_equipment_assessment','wheel_walker']:
                        report_rml="eMobility/Report Template/"+prev_record.driving_assessment_type+".ods"
                        report_type_r='oo-xls'
                    else:
                        report_rml="eMobility/Report Template/"+prev_record.driving_assessment_type+".odt"
                        report_type_r='oo-doc'
                    debug(report_rml)
                    debug(report_temp_browse.name)
                    report_type='standard'
                elif report_temp_browse.name == 'Dvla Template':
                    report_type='dvla'
                    report_rml='eMobility/Report Template/'+prev_record.driving_assessment_type+'_dvla.odt'
                    report_type_r='oo-doc'
                else:
                    raise except_orm('Warning','No Report Found')
            report_id=pooler.get_pool(cr.dbname).get('ir.actions.report.xml').search(cr, uid, [("name", "=", "Driving Ax Report")])
            pooler.get_pool(cr.dbname).get('ir.actions.report.xml').write(cr, uid, [report_id[0]], {
                    'report_rml': report_rml,
                    'report_type':report_type_r
                 })
            cr.execute('select * from cmc_appointments where state=\'completed\' and assessment_id=%d ' % (int(data['ids'][0])))
            appt_ids = map(itemgetter(0), cr.fetchall())
            debug(cr.fetchall())
            debug(appt_ids)
            try:
                appt_record = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, appt_ids[0])
                cr.execute('select user_id from user_appointment_rel where appointment_id = %d' % (appt_record.id))
            except:
                appt_record=False
            debug(appt_record)
            agent_id=False
            if prev_record.client_person_id.display_name:
                person_id = prev_record.client_person_id
                agent_id=prev_record.agent_person_id
            elif prev_record.agent_person_id.display_name == 'dvla':
                person_id=prev_record.agent_person_id
            else:
                raise except_orm('Warning','This Assessment Has no Client')
            address1 = person_id.address_line_1
            address2 = person_id.address_line_2
            add = False
            if address1 :
                add = address1
            elif address2 :
                add = address2
            elif address1 and address2:
                add = address1 + ',' + address2
            postcode = person_id.postcode
            telephone = person_id.telephone
            email = person_id.email_address
                
            license_status = prev_record.type_lincense
            driver_number = prev_record.driver_number
            states = ['currently_driving', 'currently_driving_past', 'never_driven', 'driving_lessons_current']
            for st in states:
                    if prev_record.driving_experience == st:
                        data['form'][st] = 'Yes'
                    else:
                        data['form'][st] = 'No'
            
            debug(report_type)
            debug(report_rml)
            debug(report_type_r)
            debug(person_id)
            if report_type == 'standard':
                debug("In standard Zone")
                data['form']['id'] = person_id.person_id 
                data['form']['type'] = self.driving_name(prev_record.driving_assessment_type)
                data['form']['location'] = prev_record.where if prev_record.where else ""
                data['form']['name'] = person_id.display_name 
                data['form']['address']=add if add else ""
                data['form']['agent_name']=agent_id.display_name if agent_id else ""
                data['form']['email']=person_id.email_address  if person_id.email_address else ""
                data['form']['telephone']=telephone if telephone else "" 
                data['form']['ethnicity']=person_id.ethnicity if person_id.ethnicity else ""
                data['form']['date_birth'] = datetime.datetime.strptime(person_id.birth_date,"%Y-%m-%d").strftime("%d-%m-%Y") if person_id.birth_date else ""
                data['form']['birth_date'] = datetime.datetime.strptime(person_id.birth_date,"%Y-%m-%d").strftime("%d-%m-%Y") if person_id.birth_date else ""
                data['form']['license_status'] = license_status if license_status else "" 
                data['form']['number'] = driver_number if prev_record.driver_number else "" 
                data['form']['glass_required'] = ""
                data['form']['dlva_notification'] = 'Yes' if prev_record.b_dlva_informed else 'No'
                data['form']['diagnosis'] = prev_record.diagnosis if prev_record.diagnosis else ""
                data['form']['assessment_date'] = appt_record.apmnt_start_date if appt_record else ""
                data['form']['owner'] = appt_record.owner if appt_record else ""
                data['form']['number'] = ""
                data['form']['vehicle_used'] =""
                data['form']['method_control'] = ""
                data['form']['plate_test'] = ""
                data['form']['reference number']=""
                data['form']['driver_number']=""
                data['form']['allowance_status']=""
                data['form']['license_expired']=""
                pooler.get_pool(cr.dbname).get('cmc.assessment.communication').create(cr, uid, {
                     'comm_date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                     'assessment_id':prev_record.id,
                     'type':self.driving_name(prev_record.driving_assessment_type),
                     'client_name':prev_record.person_id.id,
                     'user_id':uid,
                     'subject':'Assessment Report',
                     'message':'Final Assessment Report Printed'
                    })
            elif report_type == 'dvla':

                if prev_record.agent_person_id:
                    if prev_record.agent_person_id.display_name.lower().strip()=='dvla':
                        if prev_record.client_person_id:
                            debug("this person has client")
                            person_id=prev_record.client_person_id
                            data['form']['title']= self.title(person_id.title)if person_id.title != 'other' else person_id.title_other
                            data['form']['name']=person_id.display_name
                            data['form']['date_birth']=person_id.birth_date
                            data['form']['names']=data['form']['name']
                            data['form']['reference_number']=prev_record.agent_person_id.person_id
                            data['form']['driver_number']=person_id.driver_number
                            data['form']['assessment_date']=appt_record.apmnt_start_date if appt_record else ""
                            data['form']['location']=appt_record.location if appt_record else "" 
                            data['form']['vehicle_used']=""
                            data['form']['method_control']=""
                            data['form']['owner'] = appt_record.owner if appt_record else ""
                        else:
                            raise except_orm('Assessment Error','Dvla has no Client')
                    else:
                        raise except_orm('Assessment Error','This Assessment does not have DVLA as agent.')
                else:
                    raise except_orm('Assessment Error','This Assessment does not have DVLA as agent.')
            else:
                raise except_orm('Template Error','Invalid Report selected?')
        
        return data['form']
    
    states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print', 'report':'driving.ax', 'state':'end'}
            }
            
        
    }

wizard_driving_ax_report('driving.ax.wizard')
