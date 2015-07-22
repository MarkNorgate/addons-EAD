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
                                <field name="user" string="Please select users whose calendars you want to view" domain="[('id','in',[30,34,36,37,38,79,90,98,101,103])]" />
                                <field name="user_group" string="Please select a Group" />
                                <field name="equipment" string="Please select a list of equipment to view" />
                                
                            </group>
                    </form>"""
user_fields = {
    'user': {'string':"", 'type':'many2many', 'relation':'res.users'},
     'equipment': {'string':"", 'type':'many2many', 'relation':'cmc.equipment'},
     'user_group':{'string':"", 'type':'many2one', 'relation':'res.groups'}
    }

def _init(self, cr, uid, data, context):
    debug(data)
    data['form']['user']= [(6, 0, [37])]
    return data
def _appointments(self, cr, uid, data, context):
    debug("=====DEBUG======")
    query=[]
    usr=[]
    usr = data['form']['user'][0][2]
    equip=data['form']['equipment'][0][2]
    
    group=False
    user_ids=False
    equipment=False
    users_group=[]
    user_len = len(usr)
    if (user_len > 0 or data['form']['user_group']) and not data['form']['equipment']:
        title = 'User Equipment Appointment Diary'
    else:
        title = 'Appointment Diary'
    if data['form']['user_group']:
        cr.execute('select uid from res_groups_users_rel where gid = %s' %(str(data['form']['user_group'])))
        ret_group=cr.fetchall()
        if ret_group >0:
            users_group=[x[0] for x in ret_group]  
        group=True
    usr.extend(users_group)
    user_len = len(usr)
    
    if user_len > 0 :
        user_ids=True
        query.append('select id from cmc_appointments where type not in (\'reminder\') and state not in (\'cancelled\',\'cancelled_within_two_days\') and (owner in ('+ ','.join([str(u) for u in usr]) +') or id in (select appointment_id from user_appointment_rel  where user_id in ('+','.join([str(u) for u in usr]) + ')))')
    equipment=False
    if len(equip) >0 :
        equipment=True
        query.append('select appointment_id from equipment_appointment_rel where equipment_id in ('+ ','.join([str(u) for u in equip]) +')')
    if len(query) == 0:
        cr.execute("select id from cmc_appointments where type not in ('reminder') and state not in (\'cancelled\',\'cancelled_within_two_days\')")
        data['form']['all_search']=True
    else:
        cr.execute(' union '.join(query))
        data['form']['all_search']=False
    my_appointments = cr.fetchall()
    debug(data)
    
    return  {
            'name': title,
            'view_type': 'form',
            'view_mode': 'calendar,form,tree',
            'res_model': 'cmc.appointments',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': "[('id','in',%s)]" % str(my_appointments),
            'context':{'app_data':data['form']}
        }


class wziard_appointment_search_user_equipment_group(wizard.interface):
    states = {
        'init': {
            'actions': [_init],
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

wziard_appointment_search_user_equipment_group('wziard_appointment_search_user_equipment_group')

