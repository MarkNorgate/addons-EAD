import wizard
import time
from tools.misc import debug
import string
from string import Template
import pooler
import base64
from osv import fields, osv
from osv.orm import except_orm
import datetime


class wizard_call_history_statistics_report(wizard.interface):
    _assess_report_detail = '''<?xml version="1.0"?>
    <form string="Contacts Statistics Report-Select Date">
                    <group colspan="4" col="4">
                        <field name="from_date" colspan="4" />
                        <field name="to_date" colspan="4" />
                    </group>
    </form>'''
    _assess_report_fields = {
    'from_date': {'type':'date', 'string':'From', 'required':True,'default': lambda * a: time.strftime('%Y-%m-01')},
    'to_date': {'type':'date', 'string':'To', 'required':True,'default': lambda * a: time.strftime('%Y-%m-%d')},
    
      }
    def _details(self, cr, uid, data, context):
        debug("Into Contacts Statistics Report")
        data['form']['date_from'] = datetime.datetime.strptime(data['form']['from_date'] , '%Y-%m-%d').strftime('%d-%m-%Y')
        data['form']['date_to'] = datetime.datetime.strptime(data['form']['to_date'] , '%Y-%m-%d').strftime('%d-%m-%Y')
        data['form']['contacts_stats']=[]
        contacts=['Telephone','Email','Fax','Letter','In Person','Other']
        total=0
        for cc in contacts:
            cr.execute("select count(id) from cmc_call_history where call_type='inbound' and call_channel ='%s' and call_date_time>='%s' and call_date_time<='%s'" %(cc,data['form']['from_date'],data['form']['to_date']))
            count = cr.fetchone()[0]
            vals = {
            'name':cc,
            'count':int(count)
            }
            data['form']['contacts_stats'].append(vals)
            total += int(count)
        data['form']['contact_total']=total
        return data['form']
    def _redirect(self, cr, uid, data, context):
        return {
            'type': 'ir.actions.act_url',
            'url':'/menu',
            'target': '_top'
        }
    states = {
        'init': {
            'actions': [],
            'result': {'type':'form',
                       'arch':_assess_report_detail,
                       'fields':_assess_report_fields,
                       'state':[
                                ('cancel', 'Cancel'),
                                ('report', 'Print Report'),
                                ]}
        },
        'report': {
            'actions': [_details],
            'result': {'type':'print', 'report':'contacts.statistics.report', 'state':'end'}
        },
        'cancel' :{
             'actions': [],
             'result':{
                'type':'action',
                'action': _redirect,
                'state':'end'
            }
        }
        
    }

wizard_call_history_statistics_report('wizard_call_history_statistics_report')



