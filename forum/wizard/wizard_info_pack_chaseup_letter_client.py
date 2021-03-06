import wizard
import time
from tools.misc import debug
import string
from string import Template
import pooler
import base64


class wizard_info_chaseup_pack_letter(wizard.interface):
    def driving_name(self, type):
        t = {
            'general':'GENERAL',
            'full_driving_assessment': 'FULL DRIVING ASSESSMENT',
            'wheelchair_assessment':'WHEELCHAIR ASSESSMENT',
            'drive_from_wheelchair_assessment':'DRIVE FROM WHEELCHAIR ASSESSMENT',
            'passenger_adult':'Passenger Adult','passenger_child':'Passenger Child',
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
            'momap_access':'MO MAP Access',
            'pressure_mapping_assessment':'Pressure Mapping Assessment',
            }
        return t.get(type, False)
    def title(self,title):
        t = {
            'dr': 'Dr',
            'mr':'Mr',
            'ms':'Miss',
            'Ms':'Ms',
            'mrs':'Mrs',
            'other':'Other'
            }
        return t.get(title, False)
    
    def _details(self, cr, uid, data, context):
        debug(context)
        debug('==== DATA INFO PACK CHASE UP LETTER ====')
#        report_id=pooler.get_pool(cr.dbname).get('ir.actions.report.xml').search(cr,uid,[('name', '=', 'Info Pack Chase Up Letter')])[0]
#        report_write=pooler.get_pool(cr.dbname).get('ir.actions.report.xml').write(cr,uid,[report_id],{'report_type':'odt'})
        debug(data)
        prev_record = pooler.get_pool(cr.dbname).get('cmc.assessment').browse(cr, uid, int(data['id']))
#        client = pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, prev_record.client_id)
        debug('HEllo')
        person_id = prev_record.client_person_id
        data['form']['message'] = False
        type = False
        type = prev_record.type
        debug(prev_record.paying)
        paying = prev_record.paying
        data['form']['address'] = []
        if (person_id.address_line_1):
            data['form']['address'].append(person_id.address_line_1)
        if (person_id.address_line_2):
            data['form']['address'].append(person_id.address_line_2)
        if (person_id.city):
            data['form']['address'].append(person_id.city)
        if (person_id.county):
            data['form']['address'].append(person_id.county)
        if (person_id.postcode):
            data['form']['address'].append(person_id.postcode)

        data['form']['person_id'] = person_id.person_id
        if person_id.title:
            data['form']['title'] = self.title(person_id.title)if person_id.title != 'other' else person_id.title_other
        else:
            data['form']['title'] =""
        data['form']['name'] = person_id.display_name 
        data['form']['last_name'] = person_id.last_name
        debug("WHAT HAPPENED DUSH BAG!!!")
        debug(person_id.last_name)
        if person_id.title and person_id.last_name:
            data['form']['title_last_name'] = (self.title(person_id.title) if person_id.title != 'other' else person_id.title_other)+' '+person_id.last_name
        else:
            data['form']['title_last_name'] =person_id.display_name
        debug(data['form']['title_last_name'])
        data['form']['type'] = self.driving_name(prev_record.driving_assessment_type)
        
        return data['form']
    
    states = {
        'init': {
            'actions': [_details],
            'result': {'type':'print', 'report':'info.pack.chaseup.letter', 'state':'end'}
            }
            
        
    }

wizard_info_chaseup_pack_letter('wizard.info.chaseup.letter.client')
