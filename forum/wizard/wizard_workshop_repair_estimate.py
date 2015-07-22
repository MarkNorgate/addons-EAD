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

class wizard_workshop_repair_estimate(wizard.interface):
       
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
        debug("INTO wizard_workshop_repair_estimate ENQUIRY FORM")
        debug(data)
        debug(context)
        add=agent_add=postcode=agent_postcode=telephone=agent_telephone=email=agent_email=agent_id=""
        a_title=c_title=postcode=""
        person_id=False
        agent_id=False
#===============================================================================
# #        Fetching Appointment Information
#===============================================================================
        prev_record = pooler.get_pool(cr.dbname).get('cmc.workshop.process').browse(cr, uid, int(data['ids'][0]))
        if prev_record.current_user_id.display_name:
            person_id = prev_record.current_user_id
        else:
            raise except_orm('Warning','No Current User')
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
                                                                        'title':'Repair Estimate Sheet',
                                                                        'description':'Repair Estimate Sheet Printed',
                                                                        'workshop_id':int(data['id'])
                                                                        }) 
        #=======================================================================
        # CLIENT WIZARD INFORMATION  
        #=======================================================================
        data['form']['title']=c_title
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
        # EQUIPMENT INFORMATIOn
        #=======================================================================
        data['form']['make']=prev_record.equipment_id.make
        data['form']['model']=prev_record.equipment_id.model
        return data['form']
    
   states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print', 'report':'workshop.repair.estimate', 'state':'end'}
            }
            
        
    }

wizard_workshop_repair_estimate('wizard_workshop_repair_estimate')
