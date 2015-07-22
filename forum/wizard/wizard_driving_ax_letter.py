import wizard
import time
from tools.misc import debug
import string
from string import Template
import pooler
import base64
from operator import itemgetter
import datetime
from osv import fields, osv
from osv.orm import except_orm
import textwrap

class wizard_driving_ax_letter(wizard.interface):
       
   def title(self, title):
        t = {
            'dr': 'Dr',
            'mr':'Mr',
            'ms':'Miss',
            'Ms':'Ms',
            'mrs':'Mrs',
            'other':'Other'
            }
        return t.get(title, '')
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
        debug(context)
        prev_record = pooler.get_pool(cr.dbname).get('cmc.assessment').browse(cr, uid, int(data['ids'][0]))
        if prev_record.client_person_id.display_name:
            person_id = prev_record.client_person_id
            agent_id=prev_record.agent_person_id
        elif prev_record.agent_person_id.display_name == 'dvla':
            person_id=prev_record.agent_person_id
        else:
            raise except_orm('Warning','This Assessment Has no Client')
        display_name = event_start = address1 = address2 = ethinicty = telephone = email = location = birth_date = mobility_component = False
        context_name=False
        apmt_start_date=""
        apmt_start_time=""
        apmt_location=""
        if 'appointment_letter' not in context:
            data['context']['appointment_letter']=prev_record.dummy_docs
            context_name=prev_record.dummy_docs
        context_name=data['context']['appointment_letter']
        debug(data['context']['appointment_letter'])
        if not context_name:
            raise except_orm('Appointment Error!', 'Please Select The One Of the Following From The List')
        # if data['context']['appointment_letter'] in ['Essex Access to Work  Wakes Hall','Essex Car Transfer Wakes Hall',\
                                                     # 'Essex DFW','Essex Drive Only Wakes Hall','Essex DVLA Wakes Hall',\
                                                     # 'Essex Legal Wakes Hall','Essex MAP referral  Wakes Hall',\
                                                     # 'Essex Self Refer Wakes Hall','Essex Self Refer',\
                                                     # 'MAP referral  Wakes Hall','Thetford Access to Work',\
                                                     # 'Thetford Car Transfer','Thetford DFW','Thetford Drive Only'\
                                                     # 'Thetford DVLA','Thetford MAP Car transfer','Thetford MAP referral.odt'\
                                                     # 'Thetford PV','Thetford Self Refer'
                                                     # ]:
        cr.execute('select a.id from cmc_appointments a ' \
		   'inner join cmc_assessment assmt on assmt.id = a.assessment_id ' \
		   'where a.state not in ( \'cancelled\',\'cancelled_within_two_days\') and assmt.id = %d' % (int(data['ids'][0])))
        appt_ids = map(itemgetter(0), cr.fetchall())
        appt_record=False
        if len(appt_ids)>0:
            appt_record = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, appt_ids[0])
        	
        if appt_record:
        	apmt_start_date_time=(appt_record.apmnt_start_date_time).split(" ")
        	apmt_start_date=(datetime.datetime.strptime(apmt_start_date_time[0],"%Y-%m-%d")).strftime("%d %B %Y")
        	apmt_start_time=apmt_start_date_time[1]
        	apmt_location=appt_record.location if appt_record.location else ""
        if data['context']['appointment_letter'] in ['Essex DVLA Wakes Hall','Thetford DVLA','Agent appt confirmation']:
            if agent_id:
                if data['context']['appointment_letter'] in ['Essex DVLA Wakes Hall','Thetford DVLA'] and agent_id.display_name.lower().strip()!='dvla':
                    raise except_orm('Warning','Agent is Not Dvla')
            else:
                raise except_orm('Warning','This record has no agent')
        #=======================================================================
        # Chaning of reports
        #=======================================================================
        report_id=pooler.get_pool(cr.dbname).get('ir.actions.report.xml').search(cr, uid, [("report_name", "=", "driving.ax.letter")])
        report_rml='forum/Msc Reports/'+context_name+'.odt'
        report_name=context_name
        debug(report_rml)
        debug(report_id)
        pooler.get_pool(cr.dbname).get('ir.actions.report.xml').write(cr, uid, [report_id[0]], {
                    'report_rml':report_rml,
                    'name':report_name
                 })
        
        #=======================================================================
        # Person Information
        #=======================================================================
        
        address=[]
        if person_id.address_line_1:
            address.append(person_id.address_line_1)
        if person_id.address_line_2:
            address.append(person_id.address_line_2)
        if person_id.city:
            address.append(person_id.city)
        if person_id.county:
            address.append(person_id.county)
        if person_id.postcode:
            address.append(person_id.postcode)
        if len(address) >0 :
            add=address
        else:
            add = []    
        data['form']['date_birth'] = datetime.datetime.strptime(person_id.birth_date, "%Y-%m-%d").strftime("%d-%m-%Y") if person_id.birth_date else ""
        data['form']['title'] = (self.title(person_id.title)if person_id.title != 'other' else person_id.title_other) if person_id.title else ""
        data['form']['name'] = person_id.display_name
        data['form']['id'] = person_id.file_reference_number if person_id.file_reference_number else ""
        data['form']['type'] =prev_record.driving_assessment_type
        data['form']['address']=add
        debug(person_id.last_name)
        if person_id.title and person_id.last_name:
            data['form']['title_last_name'] = 'Dear ' + (self.title(person_id.title) if person_id.title != 'other' else person_id.title_other) + ' ' + (person_id.last_name if person_id.last_name else '')
        else:
            data['form']['title_last_name'] = 'Dear '+person_id.display_name
        debug(data['form']['title_last_name'])
        data['form']['ethnicity'] = person_id.ethnicity if person_id.ethnicity else ""
        data['form']['file_refrence_no']=person_id.file_reference_number if person_id.file_reference_number else ""
        #=======================================================================
        # Agent Information
        #=======================================================================
        agent_title=agent_name=agent_address=""
        if agent_id:
            agent_title=(self.title(agent_id.title)if agent_id.title != 'other' else agent_id.title_other) if agent_id.title else ""
            agent_name=agent_id.display_name
            address=[]
            if agent_id.address_line_1:
                address.append(agent_id.address_line_1)
            if agent_id.address_line_2:
                address.append(agent_id.address_line_2)
            if agent_id.city:
                address.append(agent_id.city)
            if agent_id.county:
                address.append(agent_id.county)
            if agent_id.postcode:
                address.append(agent_id.postcode)
            if len(address) >0 :
                add=','.join(address)
            else:
                add = ""
        data['form']['agent_address']=add   
        data['form']['agent_title'] = agent_title
        data['form']['agent_name'] = agent_name
        
            
        #=======================================================================
        # Appointment Information
        #=======================================================================
        data['form']['apmt_start_date'] = apmt_start_date
        data['form']['apmt_start_time'] = apmt_start_time
        data['form']['apmnt_start_date'] = apmt_start_date
        data['form']['apmnt_start_time'] = apmt_start_time
        data['form']['location'] = prev_record.where if prev_record.where else ""
        #=======================================================================
        # Communication Log Entry
        #=======================================================================
        pooler.get_pool(cr.dbname).get('cmc.assessment.communication').create(cr, uid, {
                 'comm_date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 'assessment_id':prev_record.id,
                 'type':self.driving_name(prev_record.driving_assessment_type),
                 'client_name':prev_record.client_person_id.id,
                 'user_id':uid,
                 'subject':data['context']['appointment_letter'],
                 'message':data['context']['appointment_letter']+' Printed'
            })
        return data['form']
    
   states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print', 'report':'driving.ax.letter', 'state':'end'}
            }
            
        
    }

wizard_driving_ax_letter('driving.ax.type.letter.wizard')
