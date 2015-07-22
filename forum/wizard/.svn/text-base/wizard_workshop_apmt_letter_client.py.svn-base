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

class wizard_workshop_apmt_letter_client(wizard.interface):
       
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
        debug("INTO WORKSHOP APMT FORM")
        debug(data)
        start_date_time=end_date_time=""
        cr.execute('select * from cmc_appointments where state=\'confirmed\' and workshop_id=%d ' % (int(data['ids'][0])))
        appt_ids = map(itemgetter(0), cr.fetchall())
        debug(cr.fetchall())
        debug(appt_ids)
        start_date=end_date=start_time=end_time=""
        appointment_letter = context.get('appointment_letter', False)
        if len(appt_ids) == 0:
            raise except_orm('Warning','Please First Confirm the active appointment')
        try:
            appt_record = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, appt_ids[0])
            start_date_time=appt_record.apmnt_start_date_time
            end_date_time=appt_record.apmnt_end_date_time
            start_date_time = appt_record.apmnt_start_date_time.split(" ")
            start_date= datetime.datetime.strptime(start_date_time[0], '%Y-%m-%d').strftime('%d-%B-%Y')
            start_time=start_date_time[1]
            end_date_time = appt_record.apmnt_end_date_time.split(" ")
            end_date= datetime.datetime.strptime(end_date_time[0], '%Y-%m-%d').strftime('%d-%B-%Y')
            end_time=start_date_time[1]
        except:
            appt_record=False
        
        debug(appt_record)
        debug(context)
        add=agent_add=postcode=agent_postcode=telephone=agent_telephone=email=agent_email=agent_id=""
        a_title=c_title=postcode=""
        information=""
        agent_client_info=[]
        heading_before_apmt_details=""
        description=""
        agent_client_add=""
        person_id=False
        agent_id=False
#===============================================================================
# #        Fetching Appointment Information
#===============================================================================
        prev_record = pooler.get_pool(cr.dbname).get('cmc.workshop.process').browse(cr, uid, int(data['ids'][0]))
        debug(appointment_letter)
        if appointment_letter == 'Appointment letter to Current User print':
            if prev_record.current_user_id.display_name:
                person_id = prev_record.current_user_id
                description='Appointment To Current User Printed'
                information="""
                We may need to change your appointment date at short notice if we have ordered parts and they do not arrive in time for your appointment.  
                If we need to change your appointment date we will let you know as soon as possible.
                """
                heading_before_apmt_details="Please let me know as soon as possible if this date will be convenient for you."
            else:
                raise ('Warning','This Workshop Process Has no Current User')
        elif appointment_letter == 'Appointment letter to Current Owner print':
            if prev_record.owner.display_name:
                person_id = prev_record.owner
                description='Appointment To Current Owner Printed'
                information="""
                We may need to change your appointment date at short notice if we have ordered parts and they do not arrive in time for your appointment.  
                If we need to change your appointment date we will let you know as soon as possible.
                """
                heading_before_apmt_details="Please let me know as soon as possible if this date will be convenient for you."
            else:
                raise ('Warning','This Workshop Process Has no Current Owner')
        elif appointment_letter == 'Appointment letter to Agent Dealership print':
            if prev_record.agent_id.display_name:
                person_id = prev_record.agent_id
                description='Appointment To Agent Printed'
                heading_before_apmt_details="We have made an appointment for the above named as follows:"
                agent_client_info.append("CLIENT: "+prev_record.current_user_id.display_name)
                address=[]
                agent_client_id=prev_record.current_user_id
                if agent_client_id.address_line_1:
                    address.append(agent_client_id.address_line_1)
                if agent_client_id.address_line_2:
                    address.append(agent_client_id.address_line_2)
                if agent_client_id.city:
                    address.append(agent_client_id.city)
                if agent_client_id.county:
                    address.append(agent_client_id.county)
                if len(address) >0 :
                    agent_client_add=','.join(address)
                else:
                    agent_client_add = ""
                agent_client_info.append("ADDRESS: "+agent_client_add)
            else:
                raise ('Warning','This Workshop Process Has no Agent')
        #=======================================================================
        # Client Side Information 
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
        if len(address) >0 :
            add=','.join(address)
        else:
            add = ""
        debug(add)
        postcode = person_id.postcode if person_id.postcode else ""
        telephone = person_id.telephone if person_id.telephone else "" 
        email = person_id.email_address if person_id.email_address else ""
        debug(email)
        if person_id.is_organisation:
            c_title=""
        else:
            c_title=data['form']['title'] = self.title(person_id.title) if person_id.title != 'other' else person_id.title_other
        #=======================================================================
        # Agent Side Information
        #=======================================================================
        pooler.get_pool(cr.dbname).get('cmc.workshop.task.history').create(cr, uid, {
                                                                        'date_task':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                                        'title':'Appointment Letter',
                                                                        'description':description,
                                                                        'workshop_id':int(data['id'])
                                                                        }) 
        #=======================================================================
        # CLIENT WIZARD INFORMATION  
        #=======================================================================
        data['form']['title']=c_title if c_title else ""
        data['form']['person_id'] = person_id.person_id 
        data['form']['name'] = person_id.display_name 
        data['form']['address']=add if add else ""
        data['form']['email']=person_id.email_address  if person_id.email_address else ""
        data['form']['telephone']=telephone if telephone else ""
        data['form']['postcode']=postcode
        debug(self.title(person_id.title))
        debug(person_id.is_organisation)
        debug(prev_record.display_name)
        if not person_id.is_organisation:
            data['form']['title_last_name'] = 'Dear '+(self.title(person_id.title) if person_id.title != 'other' else person_id.title_other) + ' ' + (person_id.last_name if person_id.last_name else "")
        else:
            data['form']['title_last_name'] ='Dear '+str(person_id.display_name)
        #=======================================================================
        # Appointment Letter details 
        #=======================================================================
        data['form']['apmt_start_date']=start_date
        data['form']['apmt_end_date']=end_date
        data['form']['apmt_start_time']=start_time
        data['form']['apmt_end_time']=end_time
        data['form']['information']=information
        data['form']['agent_client_info']=agent_client_info
        data['form']['heading_before_apmt_details']=heading_before_apmt_details
        #=======================================================================
        # EQUIPMENT INFORMATIOn
        #=======================================================================
        data['form']['make']=prev_record.equipment_id.make
        data['form']['model']=prev_record.equipment_id.model
        return data['form']
    
   states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print', 'report':'workshop.apmt.letter', 'state':'end'}
            }
            
        
    }

wizard_workshop_apmt_letter_client('wizard_workshop_apmt_letter_client')
