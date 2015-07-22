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

class wizard_workshop_pdi_manual(wizard.interface):
       
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
        debug("INTO WORKSHOP ENQUIRY FORM")
        debug(data)
        debug(context)
        add=agent_add=postcode=agent_postcode=telephone=agent_telephone=email=agent_email=agent_id=""
        a_title=c_title=""
        agent_id_id=""
        person_id=False
        agent_id=False
#===============================================================================
# #        Fetching Appointment Information
#===============================================================================
        prev_record = pooler.get_pool(cr.dbname).get('cmc.workshop.process').browse(cr, uid, int(data['ids'][0]))
        cr.execute('select * from cmc_appointments where state=\'active\' and workshop_id=%d ' % (int(data['ids'][0])))
        appt_ids = map(itemgetter(0), cr.fetchall())
        debug(cr.fetchall())
        debug(appt_ids)
        try:
            appt_record = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, appt_ids[0])
            cr.execute('select user_id from user_appointment_rel where appointment_id = %d' % (appt_record.id))
        except:
            appt_record=False
        debug(appt_record)
        
        if prev_record.current_user_id.display_name:
            person_id = prev_record.current_user_id
        else:
            raise except_orm('Warning','Following Workshop process has no current user')
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
        postcode = person_id.postcode
        telephone = person_id.telephone if person_id.telephone else "" 
        email = person_id.email_address if person_id.email_address else ""
        debug(email)
        c_title=data['form']['title'] = self.title(person_id.title)if person_id.title != 'other' else person_id.title_other
        #=======================================================================
        # Agent Side Information
        #=======================================================================
        agent_address=[]
        if prev_record.agent_id:
            agent_id=prev_record.agent_id
            if agent_id.address_line_1:
                agent_address.append(agent_id.address_line_1)
            if agent_id.address_line_2:
                agent_address.append(agent_id.address_line_2)
            if agent_id.city:
                agent_address.append(agent_id.city)
            if agent_id.county:
                agent_address.append(agent_id.county)
            debug(len(agent_address))
            debug(agent_address)
            if len(agent_address) > 0 :
                agent_add=','.join(agent_address)
            else:
                agent_add = ""
            agent_telephone=agent_id.telephone
            debug(agent_telephone)
            agent_email=agent_id.email_address
            debug(agent_email)
            agent_id_id=agent_id.person_id
            
            a_title=self.title(agent_id.title)if agent_id.title != 'other' else agent_id.title_other
        pooler.get_pool(cr.dbname).get('cmc.workshop.task.history').create(cr, uid, {
                                                                        'date_task':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                                        'title':'PDI Manual Form',
                                                                        'description':'PDI Manual Form Printed',
                                                                        'workshop_id':int(data['id'])
                                                                        }) 
        #=======================================================================
        # CLIENT WIZARD INFORMATION  
        #=======================================================================
        data['form']['title']=c_title if c_title else ""
        data['form']['id'] = person_id.person_id 
        data['form']['name'] = person_id.display_name 
        data['form']['address']=add if add else ""
        data['form']['email']=person_id.email_address  if person_id.email_address else ""
        data['form']['telephone']=telephone if telephone else ""
        
        #=======================================================================
        # AGENT WIZARD INFORMATION
        #=======================================================================
        data['form']['agent_title']=a_title if a_title else ""
        data['form']['agent_id']=agent_id_id
        data['form']['agent_name']=agent_id.display_name if agent_id else ""
        data['form']['agent_address']=agent_add
        data['form']['agent_email']=agent_email
        data['form']['agent_telephone']=agent_telephone
        
        #=======================================================================
        # EQUIPMENT INFORMATIOn
        #=======================================================================
        data['form']['make']=prev_record.equipment_id.make
        data['form']['model']=prev_record.equipment_id.model
        data['form']['serial_no']=prev_record.equipment_id.serial_no if prev_record.equipment_id.serial_no else "" 
        data['form']['order_no']=prev_record.equipment_id.order_no if prev_record.equipment_id.order_no else ""  
        data['form']['job_no']=prev_record.job_no
        debug(data['form']['make'])
        debug(data['form']['model']) 
        return data['form']
    
   states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print', 'report':'workshop.pdi.manual', 'state':'end'}
            }
            
        
    }

wizard_workshop_pdi_manual('wizard_workshop_pdi_manual')
