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

user_form = """<?xml version="1.0"?>
                    <form string="Calendar Action">
                            <group colspan="2" col="1">
                                <field name="user" string="Please select multi users to view Calendar of" />
                                <field name="user_group" string="Please select an Group" />
                                <field name="equipment" string="Please select an Equipment to view Calendar of"/>
                                
                            </group>
                    </form>"""
user_fields = {
    'user': {'string':"", 'type':'many2many', 'relation':'res.users'},
     'equipment': {'string':"", 'type':'many2one', 'relation':'cmc.equipment'},
     'user_group':{'string':"", 'type':'many2one', 'relation':'res.groups'}
    }


def _appointments(self, cr, uid, data, context):
    debug("=====DEBUG======")
    debug(data)
    debug(context)
    query=[]
    usr = data['form']['user'][0][2]
    user_len = len(usr)
    debug(usr)
    group=False
    user_ids=False
    equipment=False
    if (user_len > 0 or data['form']['user_group']) and not data['form']['equipment']:
        title = 'User Equipment Appointment Diary'
    else:
        title = 'Appointment Diary'
    if data['form']['user_group']:
        query.append('select id from cmc_appointments where owner in (select uid from res_groups_users_rel where gid = %s)' %(str(data['form']['user_group'])))
    debug(query)
    if user_len > 0 :
        query.append( 'select id from cmc_appointments where owner in ('+ ','.join([str(u) for u in usr]) +')')
        query.append('select appointment_id from user_appointment_rel  where user_id in ('+','.join([str(u) for u in usr]) + ')')
    debug(query)
    if data['form']['equipment']:
        query.append('select appointment_id from equipment_appointment_rel where equipment_id =' + str(data['form']['equipment']))
    
    if len(query) == 0:
        cr.execute("select id from cmc_appointments")
    else:
        cr.execute(' union '.join(query))
    my_appointments = cr.fetchall()
    debug(my_appointments)
    
    return  {
            'name': title,
            'view_type': 'form',
            'view_mode': 'calendar,form,tree',
            'res_model': 'cmc.appointments',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': "[('id','in',%s)]" % str(my_appointments),
        }


class wizard_cmc_user_equipment_appointment_tree(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type':'form',
                       'arch':user_form,
                       'fields':user_fields,
                       'state':[
                                ('show', 'Show Calendar'),
                                ('end', 'Cancel') 
                                ]}
        },
        'show':{
                'actions': [],
                'result': {'type': 'action', 'action': _appointments, 'state':'end'}
                }
    }       

wizard_cmc_user_equipment_appointment_tree('wizard_cmc_user_equipment_appointment_tree')

