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


class wizard_create_action(wizard.interface):
    _action_detail = '''<?xml version="1.0"?>
    <form string="Action Entry">
                    <newline />
                    <field name="state" invisible="0" select="1"
                        attrs="{'invisible':[('state','in',['none'])]}" />
                    <group colspan="4" string="Tracking">
                        <group colspan="2" col="2">
                            <field name="enquiry_id" readonly="1" />
                            <field name="enquiry_date" readonly="1" />
                            <field name="complete_date" readonly="1" />
                            <field name="email_check" invisible="1" />
                        </group>
                        <group colspan="2" col="2">
                            <field name="user_id" string="Raised By" readonly="1" />
                        </group>
                    </group>
                    <field colspan="4" name="person_id" readonly="1"></field>
                    <newline />
                    <group colspan="4" attrs="{'invisible':[('type','=','client')]}">
                            <group colspan="4" >
                                <field colspan="4" name="client_id"  />
                            </group>
                            <field colspan="4" name="agent_id" attrs="{'invisible':[('type','=','agent')]}"/>
                    </group>
                    <field colspan="4" name="type"
                        attrs="{'readonly':[('state','in',['pending', 'awaiting', 'closed'])]}"></field>
                    <newline />
                    <field colspan="4" name="due_date"
                        attrs="{'readonly':[('state','in',['pending', 'awaiting', 'closed'])]}" />
                    <field colspan="4" name="enquiry_type" string="Action / Request Type"
                        attrs="{'readonly':[('state','in',['pending', 'awaiting', 'closed'])]}" />
                    <newline />
                    <field colspan="4" name="enquiry_details" string="Action / Request Details"
                        attrs="{'readonly':[('state','in',['closed','pending','awaiting'])]}" />
                    <newline />

                    <group string="Action/Request Allocation Control" colspan="4"
                        col="3" attrs="{'invisible':[('state','in',['closed','awaiting'])]}">
                        <group colspan="1" col="1">
                            <label
                                string="This action can be transferred to an individual or a group of users. You can allocate to specific user or group of users"
                                align="0.0" />
                        </group>
                        <group colspan="2" col="2">
                            <group colspan="1" col="1">
                                <label string="Please select other User to Allocate to:"
                                    align="0.0" />
                                <field name="allocated_user_id" widget="selection"
                                    nolabel="1" />
                                <group colspan="1" col="1" />
                                    attrs="{'invisible':[('dummy','!=','allocated_user_id_changed')]}">

                            </group>
                            <group colspan="1" col="1">
                                <label string="Please select a User Group to Allocate to:"
                                    align="0.0" />
                                <field name="allocated_user_group_id" widget="selection"
                                    nolabel="1" />
                            </group>
                        </group>
                    </group>
                </form>'''
    _action_fields = {
        'person_id':{'type':'many2one', 'relation':'cmc.person', 'string':'Create Action For'},
        'enquiry_date': {'type':'datetime', 'string':'Action Date'},
        'due_date': {'type':'datetime', 'string':'Due Date'},
        'complete_date': {'type':'datetime', 'string':'Completion Date'},
        'email_check':{'type':'boolean','string':'Email'},
        'user_id':{'type':'many2one', 'relation':'res.users', 'string':'Raised By'},
        'client_id':{'type':'many2one', 'relation':'cmc.person', 'string':'Client'},
        'agent_id':{'type':'many2one', 'relation':'cmc.person', 'string':'Agent'},
        'enquiry_id': {'type':'char', 'string':'Id', 'size':100},
        'type': {'type':'selection',
                         'selection':[
                          ('client', 'Client'),
                          ('agent', 'Agent')], 'string':'Is This Person:', 'required':True},
        'enquiry_type':     {'type':'selection',
                          'selection':[
                            ('General', 'General'),
                ('Return Call','Return Call'),
                ('Equipment Supply Process','Equipment Supply Process'),
                ('Adaptation Process','Adaptation Process'),
                ('Workshop Process','Workshop Process'),
                ('Accounting Process','Accounting Process')],
                            'string':'Action Type', 'required':True},
        'state':{'type':'selection',
                  'selection':[
                            ('none', 'None'),
                           ('pending', 'Pending Action'),
                           ('awaiting', 'Awaiting Client Response'),
                           ('closed', 'Closed')],
                                     'string':'State', 'required':True},
        
        'call_details': {'type':'text', 'string':'Call Details'},
        'enquiry_details':{'type':'text', 'string':'Enquiry Details'},
        'allocated_user_id':{'type':'many2one', 'relation':'res.users', 'string':'Created By'},
        'allocated_user_group_id':{'type':'many2one', 'relation':'res.groups', 'string':'Group'},
    }
    def _person_details(self, cr, uid, data, context):
        debug("<<<ACTION WIZARD>>>")
        debug(data)
        debug(context)
        person=False
        if context.get('from',False) == 'call history':
            en = pooler.get_pool(cr.dbname).get('cmc.call.history').browse(cr, uid, int(data['id']))
            person=en.person_id
            debug('CHECKSD')
        else:
            id_id=int(data['id'])
            person = pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, id_id)
        if person.is_deceased:
            raise except_orm('Warning','This person has been marked as deceased ensure you are in the correct record')
        data['form']['person_id']=person.id
        data['form']['client_id']=''
        data['form']['agent_id']=''
        data['form']['user_id'] = uid
        data['form']['due_date']=datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        data['form']['allocated_user_id']=uid
        return data['form']
    def _save(self, cr, uid, data, context):
        debug("<<<SAVE ACTION WIZARD>>")
        debug(data)
        debug(context)
        
        if not data['form']['enquiry_details']:
            raise except_orm('Warning','Please Provide Action Details')
        debug(context.get('from'))
        if context.get('from',False) == 'call history':
            en = pooler.get_pool(cr.dbname).get('cmc.call.history').browse(cr, uid, int(data['id']))
            person=en.person_id
            debug('CHECKSD')
        else:
            id_id=int(data['id'])
            person = pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, id_id)
        
        if data['form']['allocated_user_id'] and data['form']['allocated_user_group_id']:
            raise except_orm('Warning','Please Select One Allocation')
        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid)
        data['form']['state'] = 'pending'
        data['form']['person_id']=person.id
        debug(data['form']['person_id'])
        if data['form']['allocated_user_id'] == uid:
            data['form']['allocated_user_id']=data['form']['user_id']
        enquiry_id = pooler.get_pool(cr.dbname).get('cmc.enquiry').create(cr, uid, data['form'])
        return data['form']
    states = {
        'init': {
            'actions': [_person_details],
            'result': {'type': 'form',
                       'arch':_action_detail,
                       'fields':_action_fields,
                       'state':[('save','Save'),
                                ('end','Cancel')]}
            },
        'save': {
            'actions': [_save],
            'result': {'type': 'state','state':'end'}
        }
    }       

wizard_create_action('wizard_create_action')

