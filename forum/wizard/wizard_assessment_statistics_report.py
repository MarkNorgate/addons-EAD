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
from collections import OrderedDict
from datetime import date


class wizard_assessment_statistics_report(wizard.interface):
    _assess_report_detail = '''<?xml version="1.0"?>
    <form string="Assessment Statistics Report-Select Date">
                    <group colspan="4" col="4">
                        <field name="from_date" colspan="4" />
                        <field name="to_date" colspan="4" />
                    </group>
    </form>'''
    _assess_report_fields = {
    'from_date': {'type':'date', 'string':'From', 'required':True, 'default': lambda * a: time.strftime('%Y-%m-01')},
    'to_date': {'type':'date', 'string':'To', 'required':True, 'default': lambda * a: time.strftime('%Y-%m-%d')},
    
      }
    def _init(self, cr, uid, data, context):
        data['form']['assessment_type'] = {
            "Driving-Consultation and Advice on Car Adaptations":"Driving-Consultation and Advice on Car Adaptations",
"Drive from Wheelchair":"Drive from Wheelchair",
"Self refer drive only":"Self refer drive only",
"Driving-Driving Ability Assessment (Learner)":"Driving-Driving Ability Assessment (Learner)",
"Driving-Driving tuition":"Driving-Driving tuition",
"Driving-Full Assessment and Advice on Driving Ability":"Driving-Full Assessment and Advice on Driving Ability",
"Self refer driving assessment":"Self refer driving assessment",
"Legal driving assessment":"Legal driving assessment",
"MAP driving assessment":"MAP driving assessment",
"Driving-Motability New Deal Tuition":"Driving-Motability New Deal Tuition",
"Scooter assessment":"Scooter assessment",
"Driving-Review Assessment":"Driving-Review Assessment",
"Access-Driver":"Access-Driver",
"Access-Motability New Deal":"Access-Motability New Deal",
"Access-Paediatric Passenger":"Access-Paediatric Passenger",
"Car transfer-self refer":"Car transfer-self refer",
"zz-Non-Forum Advice Session":"zz-Non-Forum Advice Session",
"Tuition":"Tuition",
"MAP familiarisation":"MAP familiarisation",
"MAP familiarisation":"MAP familiarisation",
"DVLA driving assessment":"DVLA driving assessment",
"Access to Work driving assessment":"Access to Work driving assessment",
"Employer paid driving assessment":"Employer paid driving assessment",
"MAP Car transfer":"MAP Car transfer",
"DVLA drive only":"DVLA drive only",
"Motorcycle assessment":"Motorcycle assessment",
"Kids driving assessment":"Kids driving assessment",
"Kids passenger assessment":"Kids passenger assessment",
"Wheelchair assessment":"Wheelchair assessment",
"Review Assessment":"Review Assessment",
"NHS referral - driving new":"NHS referral - driving new",
}
        data['form']['outcome_list'] = ['Suitable to drive', 'Might be suitable (learner)',
                      'Might be suitable (off road assessment only)', 'Requires familiarisation tuition',
                      'Advised against ','Review At a Later Date','Unsafe to drive','Complete','Able to drive safely','Able to drive safely with adaptations',
                      'May be able to drive safely with adaptations and tuition','May be able to drive safely after tuition',
                      'Shows the potential to learn to drive a suitable vehicle','Further assessment required',
                      'Advised unsafe to drives']
        data['form']['driving_list'] = {'inadequate_physical':'Inadequate physical control/co-ordination',
                      'impaired_perception':'Impaired perception',
                       'impaired_decision': 'Impaired decision making/judgement',
                       'medical_problems': 'Medical problems',
                        'inadequate_vision': 'Inadequate Vision'}
        data['form']['license_list'] = [
                            'Full',
                            'Provisional',
                            'Provisional Disability Assessment Licence',
                            'Revoked ',
                            'Surrendered',
                            'Under Review',
                            'Section 88 (license expired, application with DVLA)'
                       ]
        data['form']['r_type'] = {'charity':'Charity',
                'client_family':'Client/Family',
                'dvla': 'DVLA',
                'employer': 'Employer',
                'employment_agency':'Employment Agency(PACT -Access to Work',
                'health_professional': 'Health Professional',
                'insurance_company': 'Insurance Company',
                'motability_grants': 'Motability Grants',
                'motability_operations': 'Motability Operations',
                'nhs': 'NHS',
                'other': 'Other',
                'other_centre': 'Other Assessment Centre',
                'review': 'Review following a previous assessment',
                'social_services': 'Social Services',
                'solicitors': 'Solitcitors'}
        return data['form']
    def _details(self, cr, uid, data, context):
        debug("Into Assessment Statistics Report")
        data['form']['from_d'] = datetime.datetime.strptime(data['form']['from_date'] , '%Y-%m-%d').strftime('%d-%m-%Y')
        data['form']['to_d'] = datetime.datetime.strptime(data['form']['to_date'] , '%Y-%m-%d').strftime('%d-%m-%Y')
        data['form']['type_stats'] = []
        data['form']['driv_stats'] = []
        assessment_type = data['form']['assessment_type']
        total = 0
        driving_total = 0
        for driving_name in assessment_type:
            cr.execute("select count(DISTINCT(ass.id)),ass.driving_assessment_type from cmc_assessment as ass left join cmc_appointments as a on a.assessment_id = ass.id where ass.driving_assessment_type='%s' and a.assessment_id is not null and a.state='completed' and a.apmnt_start_date >='%s' and a.apmnt_start_date<='%s' group by ass.driving_assessment_type" % (driving_name, data['form']['from_date'], data['form']['to_date']))
            res = cr.dictfetchall()
            r = res[0] if len(res) > 0 else res
            data['form']['type_stats'].append({
            'name':assessment_type.get(driving_name, ''),
            'count':(str(int(r['count']))) if len(res) > 0 else 0
            })
            total += (int(r['count'])) if len(res) > 0 else 0
            data['form']['type_total_count'] = total
        data['form']['type_stats'] = sorted(data['form']['type_stats'], key=lambda x: x['name'])
        #debug(data['form']['driv_stats'])
        outcome_list = data['form']['outcome_list']
        total = 0
        data['form']['outcome_stats'] = []
        for outcome in outcome_list:
            cr.execute("select count(DISTINCT(ass.id)),outcome.name from cmc_assessment as ass left join cmc_assessment_outcome as outcome on ass.assessment_outcome_virtual=outcome.id left outer join cmc_appointments as a on a.assessment_id = ass.id where outcome.name='%s' and a.assessment_id is not null and a.state='completed' and a.apmnt_start_date >='%s' and a.apmnt_start_date<='%s' group by outcome.name order by outcome.name" % (outcome, data['form']['from_date'], data['form']['to_date']))
            res = cr.dictfetchall()
            vals = {}
            if len (res) > 0:
                r = res[0]
            #debug(res)
            vals = {
                    'outcome_name':outcome,
                    'outcome_count':r['count'] if len(res) > 0 else 0
                }
            data['form']['outcome_stats'].append(vals)
            total += vals['outcome_count']
        data['form']['outcome_total_count'] = total
        driving_list = data['form']['driving_list']
        
        data['form']['driving_stats'] = []
        total = 0
        for driving_name in driving_list:
            
            cr.execute("select count(DISTINCT(ass.id)),ass.reason_driving as hours from cmc_assessment as ass left join cmc_appointments as a on a.assessment_id = ass.id where ass.reason_driving='%s' and a.assessment_id is not null and a.state='completed' and a.apmnt_start_date <='%s' and a.apmnt_start_date>='%s' group by ass.reason_driving" \
            % (driving_name, data['form']['to_date'], data['form']['from_date']))
            res = cr.dictfetchall()
            vals = {}
            vals = {
            'driving_name':driving_list.get(driving_name),
            'driving_count':res[0]['count'] if len(res) > 0 else 0
            }
            data['form']['driving_stats'].append(vals)
            total += vals['driving_count']
        data['form']['driving_total_count'] = total
        total = 0
        license_list = data['form']['license_list']
        data['form']['license_stats'] = []
        for license_name in license_list:
            
            cr.execute("select count(DISTINCT(ass.id)),ass.type_lincense as hours from cmc_assessment as ass left join cmc_appointments as a on a.assessment_id = ass.id where ass.type_lincense='%s' and a.assessment_id is not null and a.state='completed' and a.apmnt_start_date <='%s' and a.apmnt_start_date>='%s' group by ass.type_lincense" \
            % (license_name, data['form']['to_date'], data['form']['from_date']))
            res = cr.dictfetchall()
            vals = {
            'license_name':license_name,
            'license_count':res[0]['count'] if len(res) > 0 else 0
            }
            data['form']['license_stats'].append(vals)
            total += vals['license_count']
        data['form']['license_total_count'] = total
        total = 0
        gender_list = {'male':"p.gender='male'",
                        'female':"p.gender='female'",
                        'Not Specified':"p.gender is null"}
        data['form']['gender_stats'] = []
        for gender_name in gender_list:
            cr.execute("select count(DISTINCT(ass.id)) from cmc_assessment as ass left join cmc_appointments as a on a.assessment_id = ass.id inner join cmc_person AS p ON ass.client_person_id = p.id where %s and a.state='completed' and a.apmnt_start_date <='%s' and a.apmnt_start_date>='%s'" % (gender_list[gender_name], data['form']['to_date'], data['form']['from_date']))
            res = cr.dictfetchall()
            vals = {
            'gender_name':'Male' if gender_name == 'male' else ('Female' if gender_name == 'female' else gender_name),
            'gender_count':res[0]['count'] if len(res) > 0 else 0
            }
            data['form']['gender_stats'].append(vals)
            total += vals['gender_count']
        data['form']['gender_total_count'] = total
        total = 0
        data['form']['age_stats'] = []
        current_date = datetime.datetime.now()
        # age_list = [(datetime.datetime.now()-datetime.timedelta(days=365.24*100), '86 and over'),
# (datetime.datetime.now()-datetime.timedelta(days=365.24*85), '81-85'),
# (datetime.datetime.now()-datetime.timedelta(days=365.24*80), '76-80'),
# (datetime.datetime.now()-datetime.timedelta(days=365.24*75), '71-75'),
# (datetime.datetime.now()-datetime.timedelta(days=365.24*70), '66-70'),
# (datetime.datetime.now()-datetime.timedelta(days=365.24*65), '56-65'),
# (datetime.datetime.now()-datetime.timedelta(days=365.24*55), '46-55'),
# (datetime.datetime.now()-datetime.timedelta(days=365.24*45), '36-45'),
# (datetime.datetime.now()-datetime.timedelta(days=365.24*35), '26-35'),
# (datetime.datetime.now()-datetime.timedelta(days=365.24*25), '16-25'),
# (datetime.datetime.now()-datetime.timedelta(days=365.24*15), 'Under 16')]
        age_list = [15, 25, 35, 45, 55, 65, 70, 75, 80, 85, 120]
        #age_list=sorted(age_list.items())
        # age_list.reverse()
        lower_limit = 0
        # upper_limit=age_list[0]
        for age in age_list:
            lower_age = lower_limit
            #debug("select count(p.birth_date) from cmc_assessment as ass left join cmc_appointments as a on a.assessment_id = ass.id left outer join cmc_person AS p ON ass.client_person_id = p.id where p.birth_date is not null and extract(YEAR FROM (age(p.birth_date)))>='%s' and extract(YEAR FROM (age(p.birth_date)))<='%s' and a.state='completed' and a.apmnt_start_date <='%s' and a.apmnt_start_date>='%s' and ass.driving_assessment_type in ('full_driving_assessment','drive_from_wheelchair_assessment','driving_legal_assessment','review_assessment','drive_safer_for_longer_assessment')" % (lower_age,age, data['form']['to_date'], data['form']['from_date']))
            cr.execute("select count(DISTINCT(ass.id)) from cmc_assessment as ass left join cmc_appointments as a on a.assessment_id = ass.id left outer join cmc_person AS p ON ass.client_person_id = p.id where p.birth_date is not null and extract(YEAR FROM (age(p.birth_date)))>='%s' and extract(YEAR FROM (age(p.birth_date)))<='%s' and a.state='completed' and a.apmnt_start_date <='%s' and a.apmnt_start_date>='%s'" % (lower_age, age, data['form']['to_date'], data['form']['from_date']))
            count = int(cr.fetchone()[0])
            vals = {
            'age_name':str(lower_age) + "-" + str(age) if age != 120 else "86 and over",
            'age_count':count
            }
            data['form']['age_stats'].append(vals)
            total += count
            lower_limit = age + 1
        data['form']['age_stats']   
        data['form']['age_total_count'] = total
        r_type = data['form']['r_type']
        total = 0
        data['form']['referrer_stats'] = []
        for r in r_type:
            cr.execute("select count(DISTINCT(ass.id)),ass.referrer_type as hours from cmc_assessment as ass left join cmc_appointments as a on a.assessment_id = ass.id where ass.referrer_type='%s' and a.assessment_id is not null and a.state='completed' and a.apmnt_start_date <='%s' and a.apmnt_start_date>='%s' group by ass.referrer_type" \
            % (r, data['form']['to_date'], data['form']['from_date']))
            res = cr.dictfetchall()
            vals = {
                'name':r_type.get(r),
                'count':res[0]['count'] if len(res) > 0 else 0
            }
            data['form']['referrer_stats'].append(vals)
            total += vals['count']
        data['form']['referrer_total_count'] = total
        return data['form']
    def _export(self, cr, uid, data, context):
        debug("Appointment  list")
        data['form']['from_d'] = datetime.datetime.strptime(data['form']['from_date'] , '%Y-%m-%d').strftime('%d-%m-%Y')
        data['form']['to_d'] = datetime.datetime.strptime(data['form']['to_date'] , '%Y-%m-%d').strftime('%d-%m-%Y')
        data['form']['all_stats'] = []
#        cr.execute("select EXTRACT(EPOCH FROM ass.create_date) as date_time, ass.create_date,ass.ref_id,a.apmnt_start_date_time,a.state as app_state,outcome.name as outcome,state.name as ass_state,ass.driving_assessment_type,ass.paying,users.name as ax_name,ass.reason_driving,ass.referrer_type,p.ethnicity,p.gender,p.postcode,p.birth_date,p.first_name,p.last_name,ass.type_lincense,ass.diagnosis_code from cmc_assessment as ass left join cmc_appointments as a on a.assessment_id = ass.id left join res_users as users on users.id=a.owner left outer join cmc_person as p on ass.client_person_id=p.id left outer join cmc_assessment_outcome as outcome on ass.assessment_outcome_virtual=outcome.id left outer join cmc_assessment_state as state on ass.state=state.id where a.assessment_id is not null and a.type!='reminder' and a.apmnt_start_date >='%s' and a.apmnt_start_date<='%s' order by ass.ref_id" % (data['form']['from_date'], data['form']['to_date']))
        cr.execute("select EXTRACT(EPOCH FROM ass.create_date) as date_time, ass.create_date,ass.ref_id,a.apmnt_start_date_time,a.state as app_state,outcome.name as outcome,state.name as ass_state,ass.driving_assessment_type,ass.paying,users.name as ax_name,ass.reason_driving,ass.referrer_type,p.ethnicity,p.file_reference_number,p.gender,p.postcode,p.birth_date,p.first_name,p.last_name,ass.type_lincense,ass.diagnosis_code from cmc_assessment as ass left join cmc_appointments as a on a.assessment_id = ass.id left join res_users as users on users.id=a.owner left outer join cmc_person as p on ass.client_person_id=p.id left outer join cmc_assessment_outcome as outcome on ass.assessment_outcome_virtual=outcome.id left outer join cmc_assessment_state as state on ass.state=state.id where a.assessment_id is not null and a.type!='reminder' and a.apmnt_start_date >='%s' and a.apmnt_start_date<='%s' order by ass.ref_id" % (data['form']['from_date'], data['form']['to_date']))
        re = cr.dictfetchall()
        today= date.today()
        for result in re:
            if result['app_state'] == 'cancelled' and result['ass_state'] == 'complete':
                debug(result['app_state'])
                debug(result['ass_state'])
                # Don't include in report
            else:
                born = result['birth_date']
                if born:
                    year = born[0:4]
                    month = born[5:7]
                    day = born[8:10]
                    age=today.year - int(year) - ((today.month, today.day) < (int(month), int(day)))

                data['form']['all_stats'].append(
                {'create_date':datetime.datetime.fromtimestamp(result['date_time']).strftime('%Y-%m-%d %H:%M:%S') if result['date_time'] is not None else '',
    #             'ref_id':result['ref_id'],
                 'ref_id':result['file_reference_number'],
                 'start_time':datetime.datetime.strptime(result['apmnt_start_date_time'] , '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y %H:%M') if result['apmnt_start_date_time'] is not None else '',
                 'app_state':result['app_state'],
                 'outcome':result['outcome'] if result['outcome'] is not None else '',
                 'ass_state':result['ass_state'],
                 'type':data['form']['assessment_type'].get(result['driving_assessment_type'], ''),
                 'paying':'Client paying' if result['paying'] == 'client_paying' else ('Agent Paying'if result['paying'] == 'agent_paying' else ''),
                 'ax_name':result['ax_name'],
                 'reason_driving':data['form']['driving_list'].get(result['reason_driving'], ''),
                 'referrer_type':data['form']['r_type'].get(result['referrer_type'], '') if result['referrer_type'] is not None else '',
                 'ethnicity':result['ethnicity'] if result['ethnicity'] is not None else '',
                 'gender':'Male' if result['gender'] == 'male' else ('Female' if result['gender'] == 'female' else ''),
                 'postcode':result['postcode'] if result['postcode'] is not None else '',
                 'birth_date':datetime.datetime.strptime(result['birth_date'] , '%Y-%m-%d').strftime('%d-%m-%Y') if result['birth_date'] is not None else '',
                 'age':age if result['birth_date'] is not None else '',
                 'first_name':result['first_name'] if result['first_name'] is not None else '',
                 'last_name':result['last_name'] if result['last_name'] is not None else '',
                 'type_lincense':result['type_lincense'] if result['type_lincense'] is not None else '',
                 'diagnosis_code':result['diagnosis_code'] if result['diagnosis_code'] is not None else ''
                 })
        # debug(data['form']['all_stats'])
        return data['form']
    def _redirect(self, cr, uid, data, context):
        return {
            'type': 'ir.actions.act_url',
            'url':'/menu',
            'target': '_top'
        }
    states = {
        'init': {
            'actions': [_init],
            'result': {'type':'form',
                       'arch':_assess_report_detail,
                       'fields':_assess_report_fields,
                       'state':[
                                ('cancel', 'Cancel'),
                                ('report', 'Print Report'),
                                ('report_export_appointment', 'Export Appointment'),
                                ]}
        },
        'report': {
            'actions': [_details],
            'result': {'type':'print', 'report':'assessment.statistics.report', 'state':'end'}
        },
        'cancel' :{
             'actions': [],
             'result':{
                'type':'action',
                'action': _redirect,
                'state':'end'
            }
        },
        'report_export_appointment' :{
        'actions': [_export],
            'result': {'type':'print', 'report':'assessment.statistics.report.all', 'state':'end'}
             
        },
        
    }

wizard_assessment_statistics_report('wizard_assessment_statistics_report')



