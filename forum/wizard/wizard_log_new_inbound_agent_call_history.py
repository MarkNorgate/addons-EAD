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


class call_inbound_agent_history(wizard.interface):
    _call_history_detail = '''<?xml version="1.0"?>
    <form string="New Inbound Agent Contact">
                    <group colspan="2" col="2">
                        <field name="user_id" select="2" readonly="0" widget="selection"/>
                        <field name="call_type" select="2" readonly="1" />
                        <field name="call_channel" select="2" />
                    </group>
                    <group colspan="2" col="2">
                        <label string="Please select a client the agent is calling about." colspan="2" />
                        <field name="client_id" select="2" readonly="0" />
                        <field name="agent_id" select="2" readonly="1" />
                    </group>
                    <newline />
                    <group string="Call Details" colspan="4" col="3">
                        <field string="Call Target - Client or Agent (mandatory)" colspan="3" name="call_person_type" select="1" readonly="1" />
                        <field colspan="3" name="call_reason" />
                        <field colspan="3" name="call_summary" select="1" attrs="{'readonly':[('state','!=','none')]}" />
                        <field colspan="3" name="call_details" select="1" attrs="{'readonly':[('state','!=','none')]}" />
                        <field colspan="3" name="reference" select="1" attrs="{'readonly':[('state','!=','none')]}" />
                        <newline />
                        <field name="datas" filename="datas_fname" />
                        <field name="datas_fname" readonly="0" nolabel="1"/>
                    </group>
                    <newline />
                    <group string="Call Control" colspan="4" col="3">
                        <group colspan="1" col="1">
                            <label string="This call can be transferred to an individual or a group of users. \n\nThis call is assigned to you at the moment. Unless you allocate this call to another person or group, it will remain allocated to you." align="0.0"/>
                        </group>
                        <group colspan="2" col="2">
                            <group colspan="1" col="1">
                                <label string="Please select other User to Allocate to:" />
                                <field name="allocated_user_id" widget="selection" nolabel="1"/>
                            </group>
                            <group colspan="1" col="1">
                                <label string="Please select a User Group to Allocate to:" />
                                <field name="allocated_user_group_id" widget="selection" nolabel="1"/>
                            </group>
                        </group>
                    </group>
    </form>'''
    
    _call_history_fields = {
        'call_date_time': {'type':'datetime', 'string':'Call Time'},
        'user_id':{'type':'many2one', 'relation':'res.users', 'string':'Created By','required':True},
        'call_channel': {'type':'selection',
                         'selection':[
                          ('Telephone', 'Telephone'),
                          ('Email', 'Email'),
                          ('Fax', 'Fax'),
                          ('Letter', 'Letter'),
                          ('In Person', 'In Person'),
                          ('Other', 'Other')], 'string':'Channel', 'required':True},
        'call_type':     {'type':'selection',
                          'selection':[
                            ('inbound', 'Inbound'),
                            ('outbound', 'Outbound')],
                            'string':'Type', 'required':True},
        'call_person_type':{'type':'selection',
                          'selection':[
                            ('client', 'Client'),
                            ('agent', 'Agent')],
                            'string':'Client/Agent', 'required':True},
        'call_summary': {'type':'char', 'string':'Call Summary (mandatory)', 'size':64,},
        'call_details': {'type':'text', 'string':'Call Details ', 'size':64},
        'client_id':{'type':'many2one', 'relation':'cmc.person', 'string':'Client','required':True},
        'agent_id':{'type':'many2one', 'relation':'cmc.person', 'string':'Agent'},
        'reference': {'type':'char', 'string':'Client/Agent\'s Reference', 'size':64},
        'allocated_user_id':{'type':'many2one', 'relation':'res.users', 'string':'Created By'},
        'allocated_user_group_id':{'type':'many2one', 'relation':'res.groups', 'string':'Group'},
        'datas': {'type':'binary', 'string':'Upload Email/Letter'},
        'datas_fname': {'type':'char', 'string':'Filename', 'size':64},
        'call_reason':{'type':'selection', 'string':'Reason', 'selection':[
                            ('all_assessment', 'All Assessments'),
                            ('driving_tution', 'Driving Tution'),
                            ('Driving Ax','Driving Ax'),
                                    ('Passenger Ax','Passenger Ax'),
                                    ('Drive from wheelchair Ax','Drive from wheelchair Ax'),
                                    ('Wheelchair Scooter Ax','Wheelchair/Scooter Ax'),
                                    ('Childrens Service','Childrens Service'),
                                    ('Motorbike Ax','Motorbike Ax'),
                            ('all_other_enquiries', 'All Other Enquiries'),
                            ('forum_calls','Forum Calls')], 'required':True}
    }
    
    def _client_details(self, cr, uid, data, context):
        person = pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, int(data['ids'][0]))
        data['form']['user_id'] = uid
        data['form']['call_date_time'] = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        data['form']['agent_id'] = person.id
        data['form']['call_type'] = 'inbound'
        data['form']['call_person_type'] = 'agent'
        return data['form']
    
    def _save(self, cr, uid, data, context):
        debug(data)
        if data['form']['user_id'] == uid and not data['form']['call_summary']:
            raise except_orm('Incomplete','Please Provide Call Summary')
        if data['form']['allocated_user_group_id'] and data['form']['allocated_user_id']:
                raise except_orm('Call Error!', 'Both UserGroup And User Cannot Be Selected')
        if data['form']['user_id'] != uid :
            if data['form']['allocated_user_group_id'] :
                raise except_orm('Warning','You Cannot Select the Group')
            data['form']['allocated_user_id']=data['form']['user_id']
        else:
            if not data['form']['allocated_user_group_id'] and not data['form']['allocated_user_id']:
                raise except_orm('Call Error!', 'Only one can be selected')
            
        person = pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, int(data['ids'][0]))
        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid)
        data['form']['call_date_time'] = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        data['form']['call_person_type'] = 'agent'
        data['form']['state'] = 'allocated'
        if not data['form']['client_id']:
            data['form']['calling_about']='Self'
        else:
            cr.execute('select display_name from cmc_person where id=%d' %(data['form']['client_id']))
            d=cr.fetchone()
            data['form']['calling_about']=d[0]
        
        call_id = pooler.get_pool(cr.dbname).get('cmc.call.history').create(cr, uid, data['form'],
                    {'wizard':True, 'person': person, 'user':user})
        return {}
    
    
    def _call_completed(self, cr, uid, data, context):
        debug(data)
        if data['form']['user_id'] == uid and not data['form']['call_summary']:
            raise except_orm('Incomplete','Please Provide Call Summary')
        if data['form']['allocated_user_group_id'] and data['form']['allocated_user_id']:
                raise except_orm('Call Error!', 'Both UserGroup And User Cannot Be Selected')
        if data['form']['user_id'] != uid :
            if data['form']['allocated_user_group_id'] :
                raise except_orm('Warning','You Cannot Select the Group')
            data['form']['allocated_user_id']=data['form']['user_id']
        else:
            if not data['form']['allocated_user_group_id'] and not data['form']['allocated_user_id']:
                raise except_orm('Call Error!', 'Only one can be selected')
        person = pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, int(data['ids'][0]))
        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid)
        data['form']['call_date_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data['form']['call_person_type'] = 'agent'
        data['form']['state'] = 'closed'
        if not data['form']['client_id']:
            data['form']['calling_about']='Self'
        else:
            cr.execute('select display_name from cmc_person where id=%d' %(data['form']['client_id']))
            d=cr.fetchone()
            data['form']['calling_about']=d[0]
        call_id = pooler.get_pool(cr.dbname).get('cmc.call.history').create(cr, uid, data['form'],
                    {'wizard':True, 'person': person, 'user':user})
        return {}
    def _go_to_menu(self, cr, uid, data, context):
#        cr.execute('select id, name from ir_ui_view where model=%s and name=%s', ('cmc.call.history', 'view_cmc_my_call_tree'))
#        view_res = cr.fetchone()
        debug(uid)
        return  {
                'domain': "[]",
                'name': 'Find a Person or Organisation',
                'view_type': 'form',
                'res_model': 'cmc.person',
                'view_mode': 'form,tree',
                'res_id': int(data['id']),
                'view_id': False,
                'type': 'ir.actions.act_window',
                'context':{'by_pass':'Now'}
                }
    def _go_to_wizard_assessment_client(self, cr, uid, data, context):
        #cr.execute('select id, name from ir_ui_view where model=%s and name=%s', ('cmc.person', 'cmc.person.form'))
        #view_res = cr.fetchone()
        return {
            'name': 'Create New Assessment',
            'type': 'ir.actions.wizard',
            'wiz_name': 'create_assessment'
            }
    def _go_to_wizard_assessment_agent(self, cr, uid, data, context):
        #cr.execute('select id, name from ir_ui_view where model=%s and name=%s', ('cmc.person', 'cmc.person.form'))
        #view_res = cr.fetchone()
        return {
            'name': 'Create New Assessment',
            'type': 'ir.actions.wizard',
            'wiz_name': 'create_assessment_agent'
            }
    def _go_to_wizard_action(self, cr, uid, data, context):
        #cr.execute('select id, name from ir_ui_view where model=%s and name=%s', ('cmc.person', 'cmc.person.form'))
        #view_res = cr.fetchone()
        return {
            'name': 'New Action',
            'type': 'ir.actions.wizard',
            'wiz_name': "wizard_create_action"
            }
    states = {
        'init': {
            'actions': [_client_details],
            'result': {'type':'form',
                       'arch':_call_history_detail,
                       'fields':_call_history_fields,
                       'state':[('call_completed', 'Call Completed and Close'),
                                ('end', 'Cancel'),
                                
                                ('save', 'Save'),
                                ]}
        },
        'save': {
            'actions': [_save],
            'result': {'type': 'action', 'action': _go_to_menu, 'state':'end'}

        },
        'call_completed':{
        'actions':[_call_completed],
        'result' : {'type':'action', 'action':_go_to_menu , 'state':'end'}
        },
#        'create_as_client':{
#        'actions':[_save],
#        'result' : {'type':'action', 'action':_go_to_wizard_assessment_client , 'state':'end'}
#        },
#        'create_as_agent':{
#        'actions':[_save],
#        'result' : {'type':'action', 'action':_go_to_wizard_assessment_agent , 'state':'end'}
#        },
#        'create_action':{
#        'actions':[_save],
#        'result' : {'type':'action', 'action':_go_to_wizard_action , 'state':'end'}
#        },
    }
    
call_inbound_agent_history('call_inbound_agent_history')
