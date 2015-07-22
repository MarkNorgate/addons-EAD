from osv import fields, osv
from osv.orm import except_orm
from string import Template
from tools.misc import debug
from tools.translate import _
import tools
import datetime
import string
import pooler
import base64
import wizard


class wizard_create_assessment(wizard.interface):
    _assessment_detail = '''<?xml version="1.0"?>
    <form string="Assessment as Client">
                    <group colspan="2" col="2" string="Person Details">
                        <group colspan="2" col="2">
                            <field name="person_ref_id" readonly="1"/>
                            <field name="person_id" readonly="1"/>
                            
                        </group>
                    </group>
                    <newline />
                    <group string="Details" colspan="4" col="3">
                        <field string="Due Date" colspan="3" name="duedate" select="1"  />
                        <field colspan="3" name="driving_assessment_type" select="1" />
                        <field colspan="3" name="paying" />
                        <field colspan="3" name="agent_id" attrs="{'invisible':[('paying','=','client_paying')]}" />
                        <field colspan="3" name="assessment_details" select="1" />
                        <newline />
                    </group>
    </form>'''
    
    _assessment_fields = {
        'duedate': {'type':'datetime', 'string':'Call Time'},
        'driving_assessment_type':{'type':'selection',
                          'selection':[
                 ("Car transfer-self refer","Car transfer-self refer-new"),
("Drive from Wheelchair","Drive from Wheelchair-new"),
("Self refer drive only","Self refer drive only-new"),
("Self refer driving assessment","Self refer driving assessment-new"),
("Legal driving assessment","Legal driving assessment-new"),
("MAP driving assessment","MAP driving assessment-new"),
("Scooter assessment","Scooter assessment-new"),
("Wheelchair assessment","Wheelchair assessment-new"),
("Tuition","Tuition-new"),
("MAP familiarisation","MAP familiarisation-new"),
("DVLA driving assessment","DVLA driving assessment-new"),
("Access to Work driving assessment","Access to Work driving assessment-new"),
("Employer paid driving assessment","Employer paid driving assessment-new"),
("MAP Car transfer","MAP Car transfer-new"),
("DVLA drive only","DVLA drive only-new"),
("Motorcycle assessment","Motorcycle assessment-new"),
("Kids driving assessment","Kids driving assessment-new"),
("Kids passenger assessment","Kids passenger assessment-new"),
("Review Assessment","Review Assessment"),
("NHS referral - driving new","NHS referral - driving new")],
                            'string':'Type', 'required':True},
        'paying':{'type':'selection',
                          'selection':[
                            ('client_paying', 'Client'),
                            ('agent_paying', 'Agent')],
                            'string':'Who is Paying', 'required':True},
        'person_type':{'type':'selection',
                          'selection':[
                            ('client', 'Client'),
                            ('agent', 'Agent')],
                            'string':'Is The following person is', 'required':True},
        'assessment_details': {'type':'text', 'string':'Details ', 'size':64},
        'person_id':{'type':'many2one', 'relation':'cmc.person', 'string':'Name'},
        'agent_id':{'type':'many2one', 'relation':'cmc.person', 'string':'Agent'},
        'person_ref_id':{'type':'char','size':'64','string':'Reference Id'}
    }
    def _client_details(self, cr, uid, data, context):
        debug(data)
        debug(context)
        id = int(data['id'])
        if context.get('from',False) == 'call history':
           call_browse=pooler.get_pool(cr.dbname).get('cmc.call.history').browse(cr, uid, id)
           person_id=call_browse.person_id.id
        else: 
            person_id=id
            
        person = pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, person_id)
        if person.is_deceased:
            raise except_orm('Warning','This person has been marked as deceased so no further bookings can be made from this record')
        data['form']['person_type'] = 'client'
        data['form']['person_ref_id'] = person.person_id 
        data['form']['person_id'] = person.id 
        data['form']['duedate'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return data['form']
    
    def _save(self, cr, uid, data, context):
        debug(data)
        id = int(data['id'])
        person_id=id
        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid)
        if not data['form']['agent_id'] and  data['form']['paying'] == 'agent_paying':
            raise osv.except_osv('Error!',
                                 'Please Provide an Agent!\n\n')
        if data['form']['agent_id'] == person_id and data['form']['agent_id']!=False:
            raise osv.except_osv('Error!',
                                 'You Cant Select same person as Agent !\n\n')
        data['form']['total_cost']=0;
        data['form']['is_dvla']=False
        data['form']['is_agent']=False
        data['form']['referrer_type']=None
        data['form']['is_client']=True
        if data['form']['paying'] == 'agent_paying':
            agent_person = pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, data['form']['agent_id'])
            if data['form']['agent_id'] and  data['form']['paying'] == 'agent_paying':
                if agent_person.is_dvla:
                    data['form']['is_dvla']=True
                    data['form']['referrer_type']='dvla'
                else:
                    data['form']['is_agent']=True
        data['form']['client_id'] = person_id
        data['form']['agent_id'] = data['form']['agent_id'] if data['form']['agent_id'] else None
        if data['form']['agent_id'] is None and data['form']['paying']=='client_paying':
            data['form']['referrer_type']='client_family'
        if not data['form']['duedate']:
                data['form']['duedate'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if data['form']['client_id'] and data['form']['agent_id']:
            query="insert into cmc_client_agent_rel_id values("+str(data['form']['agent_id'])+','+str(data['form']['client_id'])+")"
            cr.execute(query)
        data['form']['agent_person_id']=data['form']['agent_id']
        data['form']['client_person_id']=data['form']['client_id']
        data['form']['enquiry_details']=data['form']['assessment_details']
        data['form']['person_id']=person_id
        if data['form']['referrer_type']=='client_family' :
            query="select price from cmc_assessment_price where referrer_type='client_family' and type='"+data['form']['driving_assessment_type']+"'"
            cr.execute(query)
            price_id=cr.fetchone()
            data['form']['total_cost']=price_id[0] if price_id is not None else 0
        data['form']['total_balance']=data['form']['total_cost']
        return data['form']
    
    def _go_to_next_state(self, cr, uid, data, context):
         debug(data)
         debug(context)
         return {
            'name': 'Create New Assessment',
            'type': 'ir.actions.wizard',
            'wiz_name': 'next_state_assessment'

            }
    
    states = {
        'init': {
            'actions': [_client_details],
            'result': {'type':'form',
                       'arch':_assessment_detail,
                       'fields':_assessment_fields,
                       'state':[('end', 'Cancel'),
                                ('save', 'Save')
                                ]}
        },
        'save': {
            'actions': [_save],
            'result': {
                'type': 'action',
                'action':_go_to_next_state,
                'state':'end'
            } 

        }
    }
    
wizard_create_assessment('create_assessment')
