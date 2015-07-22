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

class wizard_equipment_supply_handover_note(wizard.interface):
       
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
        debug("INTO Equipment Supply Handover template")
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
        prev_record = pooler.get_pool(cr.dbname).get('cmc.equipement.supply.process').browse(cr, uid, int(data['ids'][0]))
        cr.execute('select id from cmc_appointments where state=\'active\' and equipment_supply_process_id=%d ' % (int(data['ids'][0])))
        appt_ids = map(itemgetter(0), cr.fetchall())
        debug(cr.fetchall())
        debug(appt_ids)
        try:
            appt_record = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, appt_ids[0])
            cr.execute('select user_id from user_appointment_rel where appointment_id = %d' % (appt_record.id))
        except:
            appt_record=False
        debug(appt_record)
        
        if prev_record.client_id.display_name:
            person_id = prev_record.client_id
        else:
            raise except_orm('Warning','Following Workshop process has no user')
        #=======================================================================
        # Client Side Information 
        #=======================================================================
        data['form']['pct']='N'
        if (person_id.display_name.lower()).strip()=='pct':
            data['form']['pct']='Y'
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
        c_title=data['form']['title'] = (self.title(person_id.title) if person_id.title != 'other' else person_id.title_other) if person_id.title else ""
        #=======================================================================
        # Agent Side Information
        #=======================================================================
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
        # EQUIPMENT INFORMATIOn
        #=======================================================================
        return data['form']
    
   states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print', 'report':'equipment.supply.handover.note', 'state':'end'}
            }
            
        
    }

wizard_equipment_supply_handover_note('wizard_equipment_supply_handover_note')
