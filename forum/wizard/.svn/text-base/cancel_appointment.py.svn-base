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


class cancel_appointment(wizard.interface):
    _call_history_detail = '''<?xml version="1.0"?>
    <form string="Cancellation Form">
                    <field name="come_from" invisible="1" />
                    <group colspan="2" col="2">
                        <field name="title" select="2" readonly="1" />
                        <field name="from_date" select="2" readonly="1" />
                        <field name="to_date" select="2" readonly="1"/>
                    </group>
                    <group colspan="2" col="2">
                        <field name="location" select="2" readonly="1" />
                        <field name="status" select="2" readonly="1" />
                    </group>
                    <newline />
                    <group string="Reason" colspan="4" col="3">
                        <field colspan="3" name="cancelled_2_days" /> 
                        <field colspan="3" name="reason" />
                        <group colspan="4" attrs="{'invisible':[('come_from','=',False)]}">
                            <field colspan="3" name="is_fail_to_attend" select="1" attrs="{'invisible':[('come_from','=',False)]}"/>
                            <field colspan="3" name="is_deceased" select="1" attrs="{'invisible':[('come_from','=',False)]}"/>
                        </group>
                        <newline />
                    </group>
    </form>'''
    
    _call_history_fields = {
        'title': {'type':'char', 'string':'Title', 'size':64},
        'from_date':{'type':'datetime', 'string':'From', 'size':64},
        'to_date':{'type':'datetime', 'string':'To', 'size':64},
        'location':{'type':'char', 'string':'Location', 'size':64},
        'status':{'type':'char', 'string':'Status', 'size':64},
        'reason': {'type':'text', 'string':'Reason', 'required':True},
        'is_deceased':{'type':'boolean',
                            'string':'Is the Person Deceased'},
        'cancelled_2_days':{'type':'boolean',
                            'string':'Cancelled Within 48 Hours'},
        'is_fail_to_attend':{'type':'boolean',
                            'string':'Failed to Attend'},
        'come_from':{'type':'boolean', 'string':'Come from'}
        
    }
    def driving_name(self, type):
        t = {
            'general':'GENERAL',
            'full_driving_assessment': 'FULL DRIVING ASSESSMENT',
            'wheelchair_assessment':'WHEELCHAIR ASSESSMENT',
            'drive_from_wheelchair_assessment':'DRIVE FROM WHEELCHAIR ASSESSMENT',
            'passenger_assessment':'PASSENGER ASSESSMENT',
            'car_seat_harness_assessment':'CAR SEAT HARNESS ASSESSMENT',
            'driving_legal_assessment':'Driving Legal Assessment',
            'drive_safer_for_longer_assessment':'Drive Safer For Longer Assessment',
            'driving_adaptation_assessment':'Driving Adaptation Assessment',
            'mo_map_adapdation_assessment':'MO MAP Adaptation Assessment',
            'review_assessment':'Review Assessment',
            'wheel_walker':'Wheeled Walker',
            'chair_assessment':'Chair Assessment',
            'bathing_assessment':'Bathing Assessment',
            'other_ilme_equipment_assessment':'Other ILME Equipment Assessment',
            'buggy_assessment':'Buggy Assessment',
            'scooter_assessment':'Scooter Assessment',
            'pct_wheelchair_buggy':'PCT Wheelchair/Buggy',
            'hoist_demo':'Hoist Demo',
            'momap_access':'MO MAP Access','Drive From Wheelchair Tution':'Drive From Wheelchair Tution',
            'pressure_mapping_assessment':'Pressure Mapping Assessment','Driving Tution':'Driving Tution','MoMap Familiarisation':'MoMap Familiarisation',
            }
        return t.get(type, False)
    def _client_details(self, cr, uid, data, context):
        debug(context)
        if context.get('cancel', False) == 'equipment' or context.get('cancel', False) == 'workshop':
            data['form']['come_from'] = False
        else:
            data['form']['come_from'] = True
        app_record = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, data['id'])
        data['form']['title'] = app_record.title
        data['form']['from_date'] = app_record.apmnt_start_date_time
        data['form']['to_date'] = app_record.apmnt_end_date_time
        data['form']['location'] = app_record.location 
        data['form']['status'] = app_record.state
        return data['form']
    def _diff(self,time1):
        diff=abs(datetime.datetime.now()-datetime.datetime.strptime(time1,"%Y-%m-%d %H:%M:%S"))
        if int(diff.total_seconds()) <=172800 and int(diff.total_seconds()) >= 0:
            return 'cancelled_within_two_days'
        else:
            return 'cancelled'
    def _save(self, cr, uid, data, context):
        debug("CANCEL APPOINTMENT")
        debug(data)
        data['form']['warning']=False
        app_record = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, int(data['id']))
        cancel_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #state_can=self._diff(app_record.apmnt_start_date_time)
        if data['form']['cancelled_2_days']:
            state_can='cancelled_within_two_days'
        else:
            state_can='cancelled'
        data['form']['other_active']=False
        if data['form']['is_deceased']:
            if app_record.assessment_id.id:
                cr.execute("select count(id) from cmc_appointments where (state='active' or state='active_clash' or state='confirmed') and assessment_id in \
                    (select id from cmc_assessment where client_person_id='%s')" %(app_record.assessment_id.client_person_id.id))
                if cr.fetchone()[0] >0:
                    data['form']['other_active']=True
                    query="update cmc_assessment set client_deceased=True where client_person_id=%s" %(app_record.assessment_id.client_person_id.id)
                    cr.execute(query)
                query_ids="select id from cmc_appointments where (state='active' or state='active_clash' or state='confirmed') and assessment_id in \
                    (select id from cmc_assessment where client_person_id='%s')" %(app_record.assessment_id.client_person_id.id)
                cr.execute(query_ids)
                q_ids=cr.fetchall()
                if q_ids is not None:
                    for id in q_ids:
                        app_record_cancel = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, id[0])
                        if app_record_cancel.state in ['confirmed','active','active_clash']:
                            pooler.get_pool(cr.dbname).get('cmc.appointments').write(cr, uid, id,{'reason':data['form']['reason'],
                                                                                                  'cancel_date':cancel_date,
                                                                                                  'state':'cancelled',
                                                                                                  }
                                                                                                  )
                    pooler.get_pool(cr.dbname).get('cmc.assessment.communication').create(cr, uid, {
                     'comm_date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                     'assessment_id':app_record.assessment_id.id,
                     'type':app_record.assessment_id.driving_assessment_type,
                     'client_name':app_record.assessment_id.person_id.id,
                     'user_id':uid,
                     'subject':'Appointment Cancelled',
                     'message':'Client is deceased'
                    })
                query="update cmc_person set is_deceased=True where id=%s" %(app_record.assessment_id.client_person_id.id)
                cr.execute(query)
            elif app_record.workshop_id.id:
                query="update cmc_appointments set state='cancelled',reason='"+data['form']['reason']+"',cancel_date='"+cancel_date+"' where workshop_id="+str(app_record.workshop_id.id)
                cr.execute(query)
                pooler.get_pool(cr.dbname).get('cmc.workshop.task.history').create(cr, uid, {
                                                                        'date_task':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                                        'title':'Appointment',
                                                                        'description':'Client is deceased',
                                                                        'workshop_id':app_record.workshop_id.id   
                                                                                       })
        else:    
            if app_record.assessment_id.id:
                query="update cmc_appointments set state='%s',is_fail_to_attend=%s,reason='%s',cancel_date='%s' where assessment_id=%s and id=%s" %(state_can,data['form']['is_fail_to_attend'],data['form']['reason'],cancel_date,app_record.assessment_id.id,data['ids'][0])
                debug(query)
                cr.execute(query)
                pooler.get_pool(cr.dbname).get('cmc.assessment.communication').create(cr, uid, {
                     'comm_date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                     'assessment_id':app_record.assessment_id.id,
                     'type':app_record.assessment_id.driving_assessment_type,
                     'client_name':app_record.assessment_id.client_person_id.id,
                     'user_id':uid,
                     'subject':'Appointment Cancelled',
                     'message':'Appointment on '+app_record.apmnt_start_date_time+' was cancelled, the reason was:'+data['form']['reason']
                    })
                
            elif app_record.reminder_id.id:
                query="update cmc_appointments set state='%s',reason='%s',cancel_date='%s' where reminder_id=%s and id=%s" %(state_can,data['form']['reason'],cancel_date,app_record.reminder_id.id,data['ids'][0])
                cr.execute(query)
            if app_record.assessment_id and app_record.assessment_id.agent_person_id:
                if app_record.assessment_id.agent_person_id.display_name==tools.config.options['organisation_name']:
                    cr.execute("select state from cmc_appointments where assessment_id='%s' order by apmnt_start_date_time desc limit 3" %(app_record.assessment_id.id))
                    count=cr.fetchall()
                    debug(count)
                    if len(count)>0:
                        state_count=[x[0] for x in count if x[0]=='cancelled_within_two_days']
                        if len(state_count)>=3:
                            data['form']['warning']=True
        return {}
    
    
    def _go_to_menu(self, cr, uid, data, context):
#        cr.execute('select id, name from ir_ui_view where model=%s and name=%s', ('cmc.call.history', 'view_cmc_my_call_tree'))
        if data['form']['warning']:
            return {
            'name': 'Warning',
            'type': 'ir.actions.wizard',
            'wiz_name': 'wizard_dvla_record_cancellation_app'
            }
        elif data['form']['is_deceased'] and data['form']['other_active']:
            return {
            'name': 'Warning',
            'type': 'ir.actions.wizard',
            'wiz_name': 'wizard_cancellation_deceased_warning'
            }
        else:
            return {}
    states = {
        'init': {
            'actions': [_client_details],
            'result': {'type':'form',
                       'arch':_call_history_detail,
                       'fields':_call_history_fields,
                       'state':[
                                ('end', 'Cancel'),
                                ('save', 'Proceed'),
                                ]}
        },
        'save': {
            'actions': [_save],
            'result': {'type': 'action', 'action': _go_to_menu, 'state':'end'}

        }
    }
    
cancel_appointment('cancel.appointment.wizard')
