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

class wizard_workshop_adaptation_client_agent_paying(wizard.interface):
       
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
        postcode=""
        quote_no=your_ref_no=ca_ref_no=agent_client_name=""
        footer_info=""
        description=""
        client_paying='N'
        person_id=False
        agent_id=False
        quote=context.get('Quote',False)
#===============================================================================
# #        Fetching Appointment Information
#===============================================================================
        if quote:
            prev_record = pooler.get_pool(cr.dbname).get('cmc.workshop.process').browse(cr, uid, int(data['ids'][0]))
            
            if quote == 'Adaptation Quote Client Paying Dep Required' or quote == 'Adaptation Quote Client Paying Dep Not Required':
                 if prev_record.current_user_id.display_name:
                    person_id = prev_record.current_user_id
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
                    postcode = person_id.postcode if person_id.postcode else ""
                    telephone = person_id.telephone if person_id.telephone else "" 
                    email = person_id.email_address if person_id.email_address else ""
                    c_title=self.title(person_id.title)if person_id.title != 'other' else person_id.title_other
                    if not c_title:
                        c_title=""
                    quote_no='Quote No:'
                    your_ref_no=""
                    ca_ref_no=""
                    agent_client_name=""
                    client_paying='Y'
                    description="Adaptation Quote To Client Client Paying Printed"
                    if quote == 'Adaptation Quote Client Paying Dep Required':
                        footer_info="""A deposit of 20 % (   ) is required to confirm booking.  The balance is payable on delivery.  You can pay by debit,credit card over the phone or send a cheque, payable to Cornwall Mobility Centre, to the address at the top of the page."""
                    else:
                        footer_info=""
            elif quote == 'Adaptation Quote Agent Paying Dep Required' or quote == 'Adaptation Quote Agent Paying Dep Not Required':
                if prev_record.agent_id.display_name:
                    person_id=prev_record.agent_id
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
                    postcode = person_id.postcode if person_id.postcode else ""
                    telephone = person_id.telephone if person_id.telephone else "" 
                    email = person_id.email_address if person_id.email_address else ""
                    c_title=self.title(person_id.title)if person_id.title != 'other' else person_id.title_other
#                    Agent Client Information
                    query="select id from cmc_person where id in (select client_id from cmc_client_agent_rel_id where client_id ="+str(prev_record.owner.id)+")"
                    cr.execute(query)
                    a_id=cr.fetchone()
                    your_ref_no="Your Ref No:"
#                        client_id=pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, int(a_id[0]))
                    client_id=prev_record.owner
                    agent_client_name="Client:"+client_id.display_name
                    your_ref_no="Your Ref No:"+client_id.person_id
                    quote_no=""
                    ca_ref_no="CA No:"
                    client_paying='N'
                    description="Adaptation Quote Agent Paying Printed"
                    if quote == 'Adaptation Quote Client Paying Dep Required':
                        footer_info="""A deposit of 20% (   ) is required to confirm booking.  The balance is payable on delivery."""
                    else:
                        footer_info=""
                else:
                    raise except_orm('Warning','No agent')
            else:
                raise except_orm('Warning','Invalid Selection')
            #======================================================
            # CLIENT WIZARD INFORMATION  
            #=======================================================================
            data['form']['title']=c_title if c_title else ""
            data['form']['person_id'] = person_id.person_id 
            data['form']['name'] = person_id.display_name 
            data['form']['address']=add if add else ""
            data['form']['email']=email
            data['form']['postcode']=postcode
            data['form']['telephone']=telephone if telephone else ""
            data['form']['your_ref_no']=your_ref_no
            data['form']['quote_no']=quote_no
            data['form']['ca_no']=ca_ref_no
            data['form']['agent_client_name']=agent_client_name
            data['form']['client_paying']=client_paying
            data['form']['footer_info']=footer_info
            
            #=======================================================================
            # EQUIPMENT INFORMATIOn
            #=======================================================================
            data['form']['make']=prev_record.equipment_id.make
            data['form']['model']=prev_record.equipment_id.model
            pooler.get_pool(cr.dbname).get('cmc.workshop.task.history').create(cr, uid, {
                                                                            'date_task':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                                            'title':'Adaptation Letter',
                                                                            'description':description,
                                                                            'workshop_id':int(data['id'])
                                                                            })
        return data['form']
    
   states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print', 'report':'workshop.adaptation.client.agent.form', 'state':'end'}
            }
            
        
    }

wizard_workshop_adaptation_client_agent_paying('wizard_workshop_adaptation_client_agent_paying')
