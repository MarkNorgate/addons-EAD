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
import time

period_form = """<?xml version="1.0"?>
                    <form string="DVLA Pending Reports within 10 Days">
                            <group colspan="1" col="1">
                                <field name="date_from"/>
                                <field name="date_to"/>
                            </group>
                    </form>"""
period_fields = {
    'date_from': {'string':"Start date", 'type':'date', 'required':True , 'default': lambda * a: time.strftime('%Y-%m-01')},
    'date_to': {'string':"End date", 'type':'date', 'required':True, 'default': lambda * a: time.strftime('%Y-%m-%d')}
    }
def _my_dvla_pending_assessments(self, cr, uid, data, context):
    debug("=====Completed Assessments=====")
    debug(data)
    debug(uid)
    date_from=datetime.datetime.strptime(data['form']['date_from'],"%Y-%m-%d").strftime("%Y-%m-%d 00:00:00")
    date_to=datetime.datetime.strptime(data['form']['date_to'],"%Y-%m-%d").strftime("%Y-%m-%d 23:59:00")
    if date_from > date_to :
        raise except_orm('Warning','Please Enter the Valid Date')
    debug(date_from)
    debug(date_to)
    my_pending_payment_assessments=[]
    cr.execute('select distinct(a.id) from cmc_assessment as a,cmc_appointments as aa \
    where aa.state=\'completed\'and a.id=aa.assessment_id and \
    (a.dvla_report_date is NULL or a.dvla_report_date-aa.apmnt_end_date_time >= interval\'10\')\
    and a.agent_person_id in (select id from cmc_person where organisation_name=\'Driver & Vehicle Licensing Agency\' or organisation_name=\'DVLA\') \
    and (a.assessment_date >=%s and a.assessment_date<=%s)',(date_from,date_to)) 
    my_pending_payment_assessments = cr.fetchall()
    cr.execute("select view_id from ir_act_window where name='All ILME Assessment Records'")
    view= cr.fetchall()
    debug(my_pending_payment_assessments)
    return  {
            'name': 'DVLA Pending Reports (10 days)',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.assessment',
            'view_id': view[0],
            'type': 'ir.actions.act_window',
            'domain': "[('id','in',%s)]" % str(my_pending_payment_assessments),
            }
class wizard_dvla_pending_report_10_days(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type':'form',
                       'arch':period_form,
                       'fields':period_fields,
                       'state':[
                                ('end', 'Cancel'),
                                ('save', 'Proceed')
                                ]}
        },
        'save': {
            'actions': [],
            'result': {'type': 'action', 'action': _my_dvla_pending_assessments, 'state':'end'}
            }
        }
    
    
wizard_dvla_pending_report_10_days('wizard_dvla_pending_report_10_days')