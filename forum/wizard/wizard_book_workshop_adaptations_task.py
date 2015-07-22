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

class wizard_book_workshop_adaptations_task(wizard.interface):
    _action_detail = '''<?xml version="1.0"?>
    <form string="Workshop Task">
                    <newline />
                    <group colspan="4" string="">
                            <field colspan="1" name="equipment_id" string="Choose Equipment" />
                            <field colspan="1" name="nature_job" string="What is the nature of the job/task?"/>
                            <field colspan="1" name="job_type" string="Job Type"/>
                            <newline />
                            <field colspan="1" name="paying_adaptation_repair" string="Who Will be Paying For Adaptation/User" />
                            <newline />
                            <field colspan="1" name="other_person_id" string="Person" attrs="{'invisible':[('paying_adaptation_repair','!=','Other')]}" >
                                <tree string="Person">
                                    <field name="display_name" string="Display_name" />
                                    <field name="birth_date" string="Date Of Birth" />
                                </tree>
                            </field>
                            <newline />
                            <field colspan="4" name="requirement" string="Requirement Details" />
                            <newline />
                    </group>
                </form>'''
    _action_fields = {
        'equipment_id': {'type':'many2one', 'relation':'cmc.equipment', 'size':100,'required':True},
        'job_type': {'type':'selection',
                          'selection':[('Adaptations', 'Adaptations'),('Workshop','Workshop')],
                            'string':'Job Type', 'required':True},
        'paying_adaptation_repair':{'type':'selection','selection':[('Equipment Owner', 'Equipment Owner'), ('Equipment User', 'Equipment User'), ('Other', 'Other')], 'string':'Who will be paying for the adaptation/repair?','required':True},
        'requirement':{'type':'text','string':'Requirement'},
        'other_person_id':{'type':'many2many', 'relation':'cmc.person', 'size':100},
        'nature_job': {'type':'selection',
                          'selection':[('Repair', 'Repair'), ('Service', 'Service'), ('Modifications', 'Modifications'), ('PDI', 'PDI'), ('Refurb', 'Refurb')],
                            'string':'Nature Of Task', 'required':True},
    }
    def _defualt_detail(self,cr,uid,data,context):
        debug(data)
        debug(context)
        if context.get('equipment_supply',False) == 'Equipment Supply':
            data['form']['equipment_id']=int(data['id'])
        return data['form']
    def _save(self, cr, uid, data, context):
        debug(data)
        debug(context)
        id=data['id']
        data['form']['equipment_collect']='No'
        data['form']['equipment_return']='No'
        if data['form']['paying_adaptation_repair']=='Other' and not data['form']['other_person_id']:
            raise except_orm('Warning','Please Select User For Other paying')
        data['form']['state']='New Proposal'
        debug(data)
        data['form']['appointment_letters']='Appointment letter to Current User print'
        equipment_id=pooler.get_pool(cr.dbname).get('cmc.workshop.process').create(cr, uid, data['form'],context)
        debug(equipment_id)
        data['form']['equipment_id']=int(equipment_id)
        
        return data['form']
    def _go_to_menu(self, cr, uid, data, context):
#        cr.execute('select id, name from ir_ui_view where model=%s and name=%s', ('cmc.call.history', 'view_cmc_my_call_tree'))
#        view_res = cr.fetchone()
        debug(uid)
        if context.get('equipment_supply',False) != 'Equipment Supply':
            return  {
                    'name': 'Book Job',
                    'view_type': 'form',
                    'res_model': 'cmc.workshop.process',
                    'view_mode': 'form,tree',
                    'res_id': data['form']['equipment_id'],
                    'view_id': False,
                    'type': 'ir.actions.act_window'
                    }
        else:
            return {}
    states = {
        'init': {
            'actions': [_defualt_detail],
            'result': {'type': 'form',
                       'arch':_action_detail,
                       'fields':_action_fields,
                       'state':[('save','Save'),
                                ('end','Cancel')]}
            },
        'save': {
            'actions': [_save],
            'result': {'type': 'action', 'action': _go_to_menu, 'state':'end'}

        },
    }       

wizard_book_workshop_adaptations_task('wizard_book_workshop_adaptations_task')

