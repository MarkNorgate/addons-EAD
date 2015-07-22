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


class wizard_merge_client_record(wizard.interface):
    _action_detail = '''<?xml version="1.0"?>
    <form string="Merge Person Record">
                    <newline />
                    <group colspan="4" string="">
                    <label align="0.0" colspan="4" string="The Current Person Record will be Deleted And It will be replace by the Selected Person" />
                        <group colspan="2" col="2">
                            <field name="person_id" readonly="1" />
                        </group>
                        <newline />
                        <group colspan="2" col="2">
                            <field name="new_person_id" string="Select the Person to Merge With" domain="[('id','!=',person_id)]"/>
                        </group>
                    </group>
                </form>'''
    _action_fields = {
        'person_id':{'type':'many2one', 'relation':'cmc.person', 'string':'Current Person'},
        'new_person_id':{'type':'many2one', 'relation':'cmc.person', 'string':''},
    }
    def _person_details(self, cr, uid, data, context):
        debug("<<<Person WIZARD>>>")
        debug(data)
        data['form']['person_id'] = data['id']
        person = False
        return data['form']
    def _save(self, cr, uid, data, context):
        debug("<<<SAVE PERSON WIZARD>>")
        debug(data)
        if data['form']['new_person_id'] == data['form']['person_id']:
            raise except_orm('Warning', 'You cannot Merge the same person')
        del_person=pooler.get_pool(cr.dbname).get('cmc.person').read(cr, uid, [data['form']['person_id']], ['display_name','person_id'])
        debug(del_person)
        try :
            debug("Update Assessments Records as Client")
            cr.execute("update cmc_assessment set client_person_id=%d where client_person_id=%d" % (data['form']['new_person_id'], data['form']['person_id']))
            debug("Update Assessments Records as Agent")
            cr.execute("update cmc_assessment set agent_person_id=%d where agent_person_id=%d" % (data['form']['new_person_id'], data['form']['person_id']))
            debug("Update Assessment Communication Records")
            cr.execute("update cmc_assessment_communication set client_name=%d where client_name=%d" % (data['form']['new_person_id'], data['form']['person_id']))
            debug("Update ACtion Client records")
            cr.execute("update cmc_enquiry set client_id=%d where client_id=%d" % (data['form']['new_person_id'], data['form']['person_id']))
            debug("Update ACtion Agent records")
            cr.execute("update cmc_enquiry set agent_id=%d where agent_id=%d" % (data['form']['new_person_id'], data['form']['person_id']))
            debug("Update Call History Client records")
            cr.execute("update cmc_call_history set client_id=%d where client_id=%d" % (data['form']['new_person_id'], data['form']['person_id']))
            debug("Update Call History Agent records")
            cr.execute("update cmc_call_history set agent_id=%d where agent_id=%d" % (data['form']['new_person_id'], data['form']['person_id']))
            debug("Update Equipment Supply Client Records")
            
            debug("Update Equipment Current User Records")
            cr.execute("update cmc_equipment set current_user_id=%d where current_user_id=%d" % (data['form']['new_person_id'],data['form']['person_id']))
            
            debug("Update Equipment Owner Records")
            cr.execute("update cmc_equipment set owner=%d where owner=%d" % (data['form']['new_person_id'],data['form']['person_id']))
            
            debug("Update Person Agent records")
            cr.execute("update cmc_client_agent_rel_id set client_id=%d where client_id=%d" % (data['form']['new_person_id'],data['form']['person_id']))
            debug("DELeting this person record")
            cr.execute("delete from cmc_person where id=%d"  %(data['form']['person_id']))
            debug("Done all completed")
            debug(del_person[0]['person_id'])
            pooler.get_pool(cr.dbname).get('cmc.user.activity').create(cr, uid, {
                                   'date': datetime.datetime.now(),
                                   'user_id': uid,
                                   'type': 'Merging Records',
                                   'activity':'Record merged with duplicate - '+del_person[0]['person_id'],
                                   'person_id':data['form']['new_person_id']})
            
        except:
            raise except_orm('Warning','Merging unsucessful')
        return {}
    def _go_to_menu(self, cr, uid, data, context):
        #cr.execute('select id, name from ir_ui_view where model=%s and name=%s', ('cmc.person', 'cmc.person.form'))
        #view_res = cr.fetchone()
        return {
            'type': 'ir.actions.act_url',
            'url':'/',
            'target': '_top'
            }
    states = {
        'init': {
            'actions': [_person_details],
            'result': {'type': 'form',
                       'arch':_action_detail,
                       'fields':_action_fields,
                       'state':[('save', 'Save'),
                                ('end', 'Cancel')]}
            },
        'save': {
            'actions': [_save],
            'result': {'type': 'action', 'action': _go_to_menu, 'state':'end'}
        }
    }       

wizard_merge_client_record('wizard_merge_client_record')

