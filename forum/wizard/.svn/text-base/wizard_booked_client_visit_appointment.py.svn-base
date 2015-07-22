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


class booked_client_visit_appointment(wizard.interface):
    _assessment_detail = '''<?xml version="1.0"?>
    <form string="Appointment Booking -Edit">
                    <group colspan="4">
                            <field colspan="4" name="title" string="Subject" />
                            <field colspan="4" name="event" string="Event (if not assessment)" />
                        </group>
                        
                        
                        <group />
                        <group colspan="4" col="8">
                                    <group />
                                    <group />
                                    <field colspan="1" name="apmnt_start_date" string="Start" align="0.0"/>
                                    <field colspan="1" name="start_time_hour" invisible="0" string="Time" align="0.0"/>
                                    <field colspan="1" name="start_time_minutes" invisible="0" nolabel="1"  align="0.0"/>
                                    <group />
                                    <newline />
                                    <group />
                                    <group />
                                    <field colspan="1" name="apmnt_date_end" string="Finish" align="0.0"/>
                                    <field colspan="1" name="end_time_hour" invisible="0" string="Time" />
                                    <field colspan="1" name="end_time_minutes" invisible="0" nolabel="1" />    
                                    <group />
                        </group>
                        <group colspan="4">
                            <field colspan="4" name="location" string="Location"  />
                            <field colspan="4" name="owner" string="Owner"  widget="selection" />
                        </group>
                        <group colspan="4" col="4">
                            <group colspan="4">
                                
                                <field colspan="1" name="save_clash" string="Save With Clash"  />
                            </group>
                            <newline />
                            <group colspan="4">
                                <field colspan="4" name="user_ids" string="Attendees"  />
                                <field colspan="4" name="equipment_ids" string="Equipments"  />
                            </group>
                        </group>
                </form>'''
    
    
    
    _assessment_fields = {
        'apmnt_start_date': {'type':'date', 'string':'Date', 'required':True},
        'apmnt_date_end': {'type':'date', 'string':'Date', 'required':True},
        'start_time_hour': {'type':'selection',
                         'selection':[('00', '00'), ('01', '01'), ('02', '02'),
                                      ('03', '03'), ('04', '04'),
                                      ('05', '05'), ('06', '06'), ('07', '07'),
                                      ('08', '08'), ('09', '09'),
                                      ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'),
                                      ('14', '14'), ('15', '15'),
                                      ('16', '16'), ('17', '17'),
                                      ('18', '18'), ('19', '19'),
                                      ('20', '20'), ('21', '21'),
                                      ('22', '22'), ('23', '23'),
                          ], 'string':'Time', 'required':True},
       'end_time_hour': {'type':'selection',
                         'selection':[('00', '00'), ('01', '01'), ('02', '02'),
                                      ('03', '03'), ('04', '04'),
                                      ('05', '05'), ('06', '06'), ('07', '07'),
                                      ('08', '08'), ('09', '09'),
                                      ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'),
                                      ('14', '14'), ('15', '15'),
                                      ('16', '16'), ('17', '17'),
                                      ('18', '18'), ('19', '19'),
                                      ('20', '20'), ('21', '21'),
                                      ('22', '22'), ('23', '23'),
                          ], 'string':'Time', 'required':True},
        'start_time_minutes': {'type':'selection',
                         'selection':[('00', '00'), ('05', '05'), ('10', '10'),
                                             ('15', '15'), ('20', '20'), ('25', '25'),
                                             ('30', '30'), ('35', '35'), ('40', '40'),
                                             ('45', '45'), ('50', '50'), ('55', '55')], 'string':'Minutes', 'required':True},
        'end_time_minutes': {'type':'selection',
                         'selection':[('00', '00'), ('05', '05'), ('10', '10'),
                                             ('15', '15'), ('20', '20'), ('25', '25'),
                                             ('30', '30'), ('35', '35'), ('40', '40'),
                                             ('45', '45'), ('50', '50'), ('55', '55')], 'string':'Minutes', 'required':True},
        
        'title': {'type':'char', 'string':'Subject', 'size':100, },
        'event': {'type':'char', 'string':'Event', 'size':100},
        'location':{'type':'char', 'string':'Location', 'size':100},
        'owner': {'type':'many2one','relation':'res.users','string':'Assessor','required':True},
        'user_ids': {'type':'many2many','relation':'res.users'},
        'save_clash':{'type':'boolean','string':'Clash'},
        'equipment_ids': {'type':'many2many','relation':'cmc.equipment'}
        }
    def _person_details(self, cr, uid, data, context):
        # debug(data)
        # debug(context)
        id = int(data['id'])
        if context.get('type', False) == 'Reminder':
            debug("From equipment")
            id = int(data['id'])
            data['form']['reminder_id'] = id
            data['form']['type'] = 'reminder'
            equipment_browse = pooler.get_pool(cr.dbname).get('cmc.equipment').browse(cr, uid, id)
            if equipment_browse.make:
                data['form']['title'] = equipment_browse.make + "-" + equipment_browse.model +(( "-" + equipment_browse.serial_no) if equipment_browse.serial_no else "")
        elif context.get('type', False) == 'Reminder Workshop':
            workshop_browse = pooler.get_pool(cr.dbname).get('cmc.workshop.process').browse(cr, uid, id)
            equipment_browse = pooler.get_pool(cr.dbname).get('cmc.equipment').browse(cr, uid, workshop_browse.equipment_id.id)
            id = workshop_browse.equipment_id.id
            if equipment_browse.make:
                data['form']['title'] = equipment_browse.make + "-" + equipment_browse.model +(( "-" + equipment_browse.serial_no) if equipment_browse.serial_no else "")
            data['form']['type'] = 'reminder'
            data['form']['reminder_id'] = id
            
        elif context.get('type', False) == 'Workshop':
            workshop_browse = pooler.get_pool(cr.dbname).get('cmc.workshop.process').browse(cr, uid, id)
            if workshop_browse.make:
                data['form']['title'] = workshop_browse.make + "-" + workshop_browse.model + "-" + workshop_browse.job_no if workshop_browse.job_no else ""
                data['form']['workshop_id']=int(id)
                data['form']['save_clash']=False  
        else:
            equipment_client=False
            if context.get('app',False) == 'Client':
                equipment_client=True
                
            person_id = context.get('person_id', False)
            person_browse = False
            if person_id:
                person_browse = pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, person_id)
            owner = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid)
            data['form']['title'] = (person_browse.display_name if person_id else "")+('-Delivery' if not equipment_client else "") 
            data['form']['equipment_supply_process_id'] = int(data['id'])
        data['form']['apmnt_start_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
        data['form']['apmnt_date_end'] = datetime.datetime.now().strftime("%Y-%m-%d")
        data['form']['start_time_hour'] = '09'
        data['form']['end_time_hour'] = '10'
        return data['form']
    
    def _save(self, cr, uid, data, context):
        debug(self)
        data['form']['state'] = 'active'
        appointment_id = pooler.get_pool(cr.dbname).get('cmc.appointments').create(cr, uid, data['form'])
        return {}
    
    
    states = {
        'init': {
            'actions': [_person_details],
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
                'type': 'state',
                'state':'end'
            } 

        }
}        
booked_client_visit_appointment('booked_client_visit_appointment')
