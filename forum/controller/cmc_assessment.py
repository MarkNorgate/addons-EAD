# -*- coding: cp1252 -*-
from osv import fields, osv
from osv.orm import except_orm
from string import Template
from tools.misc import debug
from tools.translate import _
import tools
import datetime
import string
import tools
import pooler
import base64
from operator import itemgetter
import smtplib
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.Header import Header
from email.Utils import formatdate, COMMASPACE
from email.Utils import formatdate, COMMASPACE
from email import Encoders
from tools.misc import ustr
import socket
import release
import netsvc

class cmc_assessment(osv.osv):
    _name = "cmc.assessment"
    _rec_name = "ref_id"
    _order = "ref_id desc"
    
    def btn_save(self, cr, uid, ids, context):
        return
    def drving_name(self, type):
        t = {
            'full_driving_assessment': 'Full Driving Assessment',
                'driving_legal_assessment': 'Driving Legal Assessment',
                            'drive_safer_for_longer_assessment': 'Drive Safer For Longer Assessment',
                            'mo_map_adapdation_assessment': 'MO MAP Adaptation Assessment',
                            'review_assessment': 'Review Assessment',
                            'hoist_demo': 'Hoist Demo',
                            'passenger_assessment' : 'Passenger Assessment',
            }
        return t.get(type, '')
    def write(self, cr, uid, ids, vals, context):
        debug("IN ASSESSMENT WRITE")
        subject = None
        message = None
        id=False
        if type(ids).__name__ == 'list':
                id = ids[0]
        else:
                id = ids
        prev_record = self.browse(cr, uid, id)
        if 'appointment_completed_d' in vals and not vals['appointment_completed_d'] and prev_record.appointment_completed_d:
                vals['appointment_completed_d']=prev_record.appointment_completed_d
        if (context.get('cancel', False) != 'appointment' and context.get('complete', False) != 'Appointment' and not context.get('invoice', False)) and len(vals) > 1:
            
            #===================================================================
            # Changing of form when agent changes
            #===================================================================
            
            if 'agent_person_id' in vals:
                if not prev_record.agent_person_id and vals['agent_person_id']:
                    person_b=pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, vals['agent_person_id'])
                    if person_b.display_name== tools.config.options['organisation_name'] :
                        vals['is_dvla']=True
                        vals['referrer_type']='dvla'
                        if prev_record.driving_assessment_type=='full_driving_assessment':
                            vals['total_cost']=150.00
                    else:
                        vals['is_agent']=True
                elif prev_record.agent_person_id and not vals['agent_person_id']:
                     vals['is_client']=True
                     vals['is_agent']=False
                     vals['is_dvla']=False
                     vals['referrer_type']='client_family'
            if 'datas' in vals:
                vals['datas_uploaded_final'] = vals['datas']
                vals['datas_uploaded_fname'] = vals['datas_fname']
                vals['uploaded_final_report'] = True
                vals['created_by'] = uid
                vals['created_on'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                pooler.get_pool(cr.dbname).get('cmc.assessment.communication').create(cr, uid, {
                             'comm_date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             'assessment_id':prev_record.id,
                             'type':self.drving_name(prev_record.driving_assessment_type),
                             'client_name':prev_record.client_person_id.id,
                             'user_id':uid,
                             'subject':'Assessment Report',
                             'message':'Assessment Report Uploaded'
                            })
            #===================================================================
            # if person is not in dirve from wheelchair and he/she select this option
            #===================================================================
            if 'b_wheelchair' in vals and vals['b_wheelchair'] and prev_record.driving_assessment_type!='drive_from_wheelchair_assessment':
                raise except_orm('Warning','As the client drives from wheelchair the assessment type must be Drive From Wheelchair')
            #===================================================================
            # payment recieved checkbox is tick and amount not entered
            #===================================================================
#            if 'state'  in vals:
#                cr.execute("select id from cmc_assessment_state where (name like %s or name like %s) and type=%s" ,('%-Closed','%-All Hours Completed',prev_record.driving_assessment_type))
#                state_close=cr.fetchone()[0]
#                if vals['state']!=prev_record.state.id and vals['state']==state_close:
#                    vals['date_closed']=datetime.datetime.now().strftime("%Y-%m-%d")
            if 'payment_received' in vals and vals['payment_received'] and vals['amount_debit'] == 0:
                raise except_orm('Warning', 'Please Enter Amount Received')
            if vals['review_date']:
                #===============================================================
                # Create Appointment With type Reminder
                #===============================================================
                cr.execute('SELECT name FROM res_users WHERE id=%s', (str(uid)))
                owner_name = cr.fetchone()
                apmnt_start_date_time = datetime.datetime.now().strftime("%Y-%m-%d")
                start_time_hour = datetime.datetime.now().strftime("%H:%M")
                apmnt_end_date_time = vals['review_date'].split(" ")[0]
                minutes = (int(start_time_hour.split(":")[1]) / 5) * 5
                pooler.get_pool(cr.dbname).get('cmc.appointments').create(cr, uid, {
                                                                                    
                     'title':(prev_record.ref_id) + '-' + (prev_record.client_person_id.display_name) + '-' + (owner_name[0]),
                     'assessment_id':prev_record.id,
                     'type':'reminder',
                     'location':'East Anglia',
                     'apmnt_start_date':apmnt_end_date_time.split(" ")[0],
                     'apmnt_date_end':apmnt_end_date_time.split(" ")[0],
                     'start_time_hour':"00",
                     'start_time_minutes':"00",
                     'end_time_hour':"23",
                     'end_time_minutes':"55",
                     'state':'active',
                     'owner':uid
                    })
            state_browse = pooler.get_pool(cr.dbname).get('cmc.assessment.state').browse(cr, uid, vals['state'])
            debug(prev_record.state);
            if prev_record.state.id != vals['state']:
                pooler.get_pool(cr.dbname).get('cmc.assessment.communication').create(cr, uid, {
                             'comm_date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             'assessment_id':prev_record.id,
                             'type':self.drving_name(prev_record.driving_assessment_type),
                             'client_name':prev_record.client_person_id.id,
                             'user_id':uid,
                             'subject':'State Changed',
                             'message':'State Changed From ' + prev_record.state.name + ' to ' + state_browse.name
                            })
        return super(cmc_assessment, self).write(cr, uid, ids, vals, context)
    def _get_default_detail(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        debug("Assessment Appointment Owner")
        if len(ids) > 0 :
            for id in ids:
                result[id]=False
                q='select owner from cmc_appointments where assessment_id=%d and (state=\'active\' or state=\'active_clash\') order by apmnt_start_date_time desc' %(id)
                cr.execute(q)
                ee=cr.fetchall()
                debug(ee)
                if ee is not None and len(ee)>0:
                    result[id]=ee[0][0]
        return result
    _columns = {
        'ref_id':fields.char('Reference Id', size=20, readonly=True),
        'call_id':fields.many2one('cmc.call.history', ''),
        'enquiry_id':fields.many2one('cmc.enquiry', 'Action'),
        'assessment_date': fields.datetime('Created On', readonly=True),
        'person_id':fields.many2one('cmc.person', 'Person'),
        'client_person_id':fields.many2one('cmc.person', 'Client'),
        'agent_person_id':fields.many2one('cmc.person', 'Agent'),
        'agency_reference_id':fields.char('Agency Reference Id', size=20, readonly=False),
        'enquiry_details':fields.text('Enquiry Details'),
        'driving_assessment_type':fields.selection([
                                 ("Car transfer-self refer","Car transfer-self refer-new"),
                                 ("Drive from Wheelchair","Drive from Wheelchair-new"),
                                 ("Self refer drive only","Self refer drive only-new"),
                                 ("Self refer driving assessment","Self refer driving assessment-new"),
                                 ("Legal driving assessment","Legal driving assessment-new"),
                                 ("MAP driving assessment","MAP driving assessment-new"),
                                 ("Scooter assessment","Scooter assessment-new"),
                                 ("Wheelchair assessment","Wheelchair assessment-new"),
                                 ("Tuition","Tuition-new"),
                                ("MAP familiarisation","MAP familiarisation-new"),
                                 ("DVLA driving assessment","DVLA driving assessment-new"),
                                 ("Access to Work driving assessment","Access to Work driving assessment-new"),
                                ("Employer paid driving assessment","Employer paid driving assessment-new"),
                                ("MAP Car transfer","MAP Car transfer-new"),
                                ("DVLA drive only","DVLA drive only-new"),
                                ("Motorcycle assessment","Motorcycle assessment-new"),
                                ("Kids driving assessment","Kids driving assessment-new"),
                                ("Kids passenger assessment","Kids passenger assessment-new"),
                                ("Driving-Consultation and Advice on Car Adaptations","Driving-Consultation and Advice on Car Adaptations"),
                                ("Driving-Driving Ability Assessment (Learner)","Driving-Driving Ability Assessment (Learner)"),
                                ("Driving-Driving tuition","Driving-Driving tuition"),
                                ("Driving-Full Assessment and Advice on Driving Ability","Driving-Full Assessment and Advice on Driving Ability"),
                                ("Driving Motability New Deal Tuition","Driving-Motability New Deal Tuition"),
                                ("Driving Review Assessment","Driving-Review Assessment"),
                                ("Access Driver","Access-Driver"),
                                ("Access Motability New Deal","Access - Motability New Deal"),
                                ("Access Paediatric Passenger","Access-Paediatric Passenger"),
                                ("NHS referral - driving new","NHS referral - driving new"),
                                ("zz Non Forum Advice Session","zz-Non-Forum Advice Session"),
								("Review Assessment","Review Assessment")],
                            'Assessment Type', required=True),
        'paying':fields.selection([('client_paying', 'Client'),
                                ('agent_paying', 'Agent')],
                                 'Who is Paying For Assessment'),
        'referrer_type':fields.selection([
                                ('charity', 'Charity'),
                                ('client_family', 'Client/Family'),
                                ('dvla', 'DVLA'),
                                ('employer', 'Employer'),
                                ('employment_agency', 'Employment Agency(PACT -Access to Work'),
                                ('health_professional', 'Health Professional'),
                                ('insurance_company', 'Insurance Company'),
                                ('motability_grants', 'Motability Grants'),
                                ('motability_operations', 'Motability Operations'),
                                ('nhs', 'NHS'),
                                ('other', 'Other'),
                                ('other_centre', 'Other Assessment Centre'),
                                ('review', 'Review following a previous assessment'),
                                ('social_services', 'Social Services'),
                                ('solicitors', 'Solitcitors'),
                                ],
                                 'Referrer Type'),
        'cognitive_referral':fields.boolean('Cognitive referral'),
        'state': fields.many2one('cmc.assessment.state', 'Status', required=True),
        'communication_id':fields.one2many('cmc.assessment.communication', 'assessment_id', ''),
        'achieve':fields.char('What do you want to achieve from this Assessment', size=255),
        'suggested':fields.boolean('Has Someone Suggested you have this assessment?'),
        'boolean_paying':fields.boolean('Will they be funding any equipment purchased?'),
        'paying_name':fields.many2one('cmc.person','Person'),
        'where':fields.selection([
                            ("2, Napier Place, Thetford, Norfolk  IP24 3RL","2, Napier Place, Thetford, Norfolk  IP24 3RL"),
("Unit No 7, Wakes Hall Business Centre, Wakes Colne, Colchester, Essex CO6 2DY","Unit No 7, Wakes Hall Business Centre, Wakes Colne, Colchester, Essex CO6 2DY"),
("Weston Village Hall, Small Drove, Weston, Spalding, Lincolnshire PE12 6HU","Weston Village Hall, Small Drove, Weston, Spalding, Lincolnshire PE12 6HS"),
                            ('Kings Lynn Outreach Centre','Kings Lynn Outreach Centre'),
                            ('Other','Other')
                            ],'Where would you like to have your assessment?'),
        'other_where':fields.char('Other',size=100),
        'diagnosis':fields.char('What is your diagnosis/disability?', size=100),
        'diagnosis_code':fields.selection([("Amputation Traumatic", "Amputation Traumatic"),
                                            ('Arthritis Inflammatory', 'Arthritis Inflammatory'),
                                            ("Back Problems", "Back Problems"),
                                            ("Brain Damage generalised", "Brain Damage generalised"),
                                            ("Brain Damage traumatic", "Brain Damage traumatic"),
                                            ("Brain Tumour", "Brain Tumour"),
                                            ("Cerebral Palsy", "Cerebral Palsy"),
                                            ("Dementia/Alzheimer's", "Dementia/Alzheimer's"),
                                            ("Dystrophy/Atrophy", "Dystrophy/Atrophy"),
                                            ("Elderly FrailHeart/Lung", "Elderly FrailHeart/Lung"),
                                            ("Learning Disability(Congenital)", "Learning Disability(Congenital)"),
                                            ("Limb Abnormalities Acquired", "Limb Abnormalities Acquired"),
                                            ("Limb Abnormalities Congenital", "Limb Abnormalities Congenital"),
                                            ("Motor Neurone Disease", "Motor Neurone Disease"),
                                            ("Multiple Sclerosis", "Multiple Sclerosis"),
                                            ("Muscle Diseases", "Muscle Diseases"),
                                            ("Not Known", "Not Known"),
                                            ("Osteoarthritis", "Osteoarthritis"),
                                            ("Other Neurological", "Other Neurological"),
                                            ("Other Non-neurological", "Other Non-neurological"),
                                            ("Parkinson's Disease", "Parkinson's Disease"),
                                            ("Peripheral Vascular Amputations", "Peripheral Vascular Amputations"),
                                            ("Polio", "Polio"),
											("Psychiatric","Psychiatric"),
                                            ("Spina Bifida", "Spina Bifida"),
                                            ("Spinal Cord Injuries", "Spinal Cord Injuries"),
                                            ("Static Visual Field Defect", "Static Visual Field Defect"),
                                            ("Stroke (other)", "Stroke (other)"),
                                            ("Stroke Left hemiplegia", "Stroke Left hemiplegia"),
                                            ("Stroke Right hemiplegia", "Stroke Right hemiplegia")], 'Diagnosis'),
        'Epilepsy Blackouts':fields.boolean('Epilepsy/Blackouts'),
        'Diabetes':fields.boolean('Diabetes'),
        'Heart Disease':fields.boolean('Heart Disease'),
        'Psychiatric illness':fields.boolean('Psychiatric Illness'),
        'Speech problems':fields.boolean('Speech problems'),
        'Memory problems':fields.boolean('Memory problems'),
        'Reading Learning difficulties':fields.boolean('Reading/Learning difficulties'),
        'onset_date':fields.date('If possible, please include the date of onset'),
        'had_operations_two_years':fields.text('Have you had any operations in the past two years?'),
        'effect':fields.text('How does your diagnosis/disability affect your daily life?'),
        'allegies':fields.text('Do you have any allergies?'),
        'medication':fields.text('Please List Any Medication You Take'),
        'last_eyesight':fields.char('When and where did you last have your eyesight tested?', size=255),
        'dominant':fields.selection([
                            ('Right', 'Right'),
                            ('Left', 'Left')],
                             'Dominant Hand'),
        'height':fields.char('Height', size=255),
        'weight':fields.char('Weight', size=155),
        'component':fields.selection([
                            ('Higher Rate Mobility Component', 'Higher Rate Mobility Component'),
                            ('War Pensioners Mobility Supplement', 'War Pensioners Mobility Supplement')],
                             'Do you receive Higher Rate Mobility Component or War Pensioners Mobility Supplement?'),
        'aids':fields.boolean('Do you use a wheelchair, scooter or any walking aids?'),
        'b_wheelchair':fields.boolean('Do you drive from a wheelchair? '),
        'b_walk':fields.boolean('Can you walk or take a few steps?'),
        'b_stand':fields.boolean('Can you stand?'),
        'b_tranfer_unaided':fields.boolean('Can you transfer in/out unaided?'),
        'how_wheelchair':fields.text('How do you transfer into/out of your wheelchair?'),
        'b_stow_wheelchair':fields.boolean('Do you currently stow your wheelchair in your vehicle?'),
        'stow_method':fields.char('What method do you use?', size=100),
        'stow_person':fields.char('Does someone else do it for you?',size=100),
        'manual_wheelchair_indoor':fields.boolean('Indoor'),
        'manual_wheelchair_outdoor':fields.boolean('Outdoor'),
        'manual_wheelchair_make_model':fields.text('Make And Model'),
        'power_wheelchair_indoor':fields.boolean('Indoor'),
        'power_wheelchair_outdoor':fields.boolean('Outdoor'),
        'power_wheelchair_make_model':fields.text('Make And Model', size=50),
        'scooter_indoor':fields.boolean('Indoor'),
        'scooter_outdoor':fields.boolean('Outdoor'),
        'scooter_make_model':fields.text('Make And Model', size=50),
        'crutches':fields.boolean('Crutches'),
        'wheeled_walker':fields.boolean('Rollator/wheeled Walker'),
        'walking_stick':fields.boolean('Walking Stick'),
        'zimmer_frame':fields.boolean('Zimmer Frame'),
        'b_driving_licenese':fields.boolean('Do you have a driving License? '),
        'type_lincense':fields.selection([
                            ('Full', 'Full'),
                            ('Provisional', 'Provisional'),
                            ('Provisional Disability Assessment Licence', 'Provisional Disability Assessment Licence'),
                            ('Revoked', 'Revoked'),
                            ('Surrendered', 'Surrendered'),
                            ('Under Review', 'Under Review'),
                            ('Section 88 (license expired, application with DVLA)', 'Section 88 (license expired, application with DVLA)'),
                            ], 'Type'),
        'driver_number':fields.char('Driver Number', size=100),
        'b_issue_uk':fields.boolean('Issued in the UK? '),
        'issue_where':fields.char('If NO where was your licence issued?', size=100),
        'b_dlva_informed':fields.boolean('Have the DVLA been informed of your medical condition?'),
        'dlva_date':fields.date('Date'),
        'license_expiry_date':fields.date('Whats Is your License Expiry Date'),
        'advised_stop':fields.boolean('Have you been advised to stop driving?'),
        'advised_stop_doctor':fields.selection([
                            ('doctor', 'Doctor'),
                            ('dvla', 'DVLA')],
                             'By Whom'),
        'driving_experience':fields.selection([
                            ('I am currently driving', 'I am currently driving'),
                            ('I am not currently driving but I have driven in the past', 'I am not currently driving but I have driven in the past'),
                            ('I have had driving lessons in the past', 'I have had driving lessons in the past'),
                            ('I am currently having driving lessons', 'I am currently having driving lessons'),
                            ('I have never driven', 'I have never driven')],
                             'Driving Experience'),
        'stop_date':fields.date('What date did you stop?'),
        'accidents_recently':fields.boolean('Have you had any accidents recently?'),
        'details_accidents_recently':fields.text('Details'),
        'b_tranfer_wo_help':fields.boolean('Can you transfer from your wheelchair, if you use one, without help from others?'),
        'b_vehicle':fields.boolean('Client Currently Has A Vehicle'),
        'vehicle_make':fields.char('Make', size=100),
         'vehicle_model':fields.char('Model', size=100),
          'vehicle_year':fields.char('Year Of Manufacture', size=100),
          'vehicle_tansmission':fields.selection([
                            ('manual', 'Manual'),
                            ('automatic', 'Automatic')],
                             'Transmission'),
        'b_vehicle_motability':fields.boolean('Did you get your vehicle from Motability?'),
        'vehicle_motablity_date':fields.date('What is the Motability renewal date?'),
        'vehicle_adaptations_fitted':fields.boolean('Does your vehicle have adaptations fitted?'),
        'vehicle_adaptations_fitted_details':fields.text('Details'),
        'b_available_for_cancellation':fields.boolean('Are you available at short notice if we have a cancellation?'),
        'days_not_available':fields.text('Days Not Available'),
        'special_requirments':fields.text('Any Special Requirements'),
        'b_assessment_legal_puporse':fields.boolean('Will you be using your assessment report for legal purposes?'),
        'wish_add':fields.text('Additional information from client'),
        'how_they_heard':  fields.selection([
            ('Unknown', 'Unknown'),
            ('Been Before', 'Been Before'),
            ('disability-group', 'Disability Group'),
            ('disabled-drivers-group', 'Disabled Drivers Group'),
            ('doctors', 'Doctors'),
            ('driving-instructors', 'Driving Instructors'),
            ('dvla', 'DVLA'),
            ('dvlni', 'DVLNI'),
            ('exhibitions', 'Exhibitions'),
            ('friends-relations', 'Friends and Relations'),
            ('garage-modification-firms', 'Garages/Modification Firm'),
            ('motability', 'Motability'),
            ('other', 'Other'),
            ('other-assessment-centres', 'Other Assessment Centres'),
            ('poster', 'Posters'),
            ('publication-media', 'Publication and Media'),
            ('social-workers-services', 'Social Workers/Social Services'),
            ('solicitors', 'Solicitors'),
            ('therapists', 'Therapists'),
            ('website', 'Website')],
        'How did client hear about us'),
        'card_type':fields.selection([('Cash', 'Cash'),
                                      ('Credit/Debit Card','Credit/Debit Card'),
                                      ('Cheque', 'Cheque'),
									  ('Bank Account','Bank Account'),
                                      ], 'Payment Type'),
        'card_name':fields.char('Card Name', size=100),
        'card_number':fields.char('Card Number', size=50),
        'card_start_date':fields.date('Start Date'),
        'card_expiry_date':fields.date('Expiry Date'),
        'card_digits':fields.integer('Last Three Digits'),
        'amount_debit':fields.float('Payment Received',digits=(255,2)),
        'amount_date':fields.date('Amount Date'),
        'appointment_id':fields.one2many('cmc.appointments', 'assessment_id', ''),
        'payment_received': fields.boolean('Has Payment been Received'),
        'payment_date':fields.date('Payment Received Date'),
        'assessment_outcome_virtual': fields.many2one('cmc.assessment.outcome', 'Assessment Outcome'),
        'reason_driving':fields.selection([('inadequate_physical', 'Inadequate physical control/co-ordination'),
                                            ('impaired_perception', 'Impaired perception'),
                                            ('impaired_decision', 'Impaired decision making/judgement'),
                                            ('medical_problems', 'Medical problems'),
                                            ('inadequate_vision', 'Inadequate Vision')], 'Reason advised against driving'),
        'review_later_date':fields.selection([('6', '6 Months'),
                                              ('12', '12 Months'),
                                              ('18', '18 Months'),
                                              ('24', '24 Months')], 'Review At A Later Date'),
        'review_date':fields.date('Reminder Date'),
        'datas_fname': fields.char('Filename', size=64),
        'datas': fields.binary('File'),
        'datas_uploaded_final':fields.binary('Uploaded'),
        'datas_uploaded_fname': fields.char('Filename', size=64),
        'uploaded_final_report':fields.boolean('Upload Final Report'),
        'created_on':fields.date('Created Date', readonly=True),
        'created_by': fields.many2one('res.users', 'Created by', readonly=True),
        'attachments':fields.one2many('assessment.attachments',
                                 'res_id', 'Attachment'),
        'docs': fields.selection([('Agent appt confirmation','Agent appt confirmation'),
                                  ('change appt Spalding','change appt Spalding'),
                                  ('Change appt Thetford','Change appt Thetford'),
                                  ('change appt Essex','Change appt Essex'),
                                  ('change appt Kings Lynn','Change appt Kings Lynn'),
                                  ('EAD leaflets send','EAD leaflets send'),
                                  ('Essex Access to Work  Wakes Hall','Essex Access to Work  Wakes Hall'),
                                  ('Essex Car Transfer Wakes Hall','Essex Car Transfer Wakes Hall'),
                                  ('Essex Courtesy call letter','Essex Courtesy call letter (unable to contact by phone)'),
                                  ('Essex DFW','Essex DFW'),
                                  ('Essex Drive Only Wakes Hall','Essex Drive Only Wakes Hall'),
                                  ('Essex DVLA Wakes Hall','Essex DVLA Wakes Hall'),
                                  ('Essex Legal Wakes Hall','Essex Legal Wakes Hall'),
                                  ('Essex MAP referral  Wakes Hall','Essex MAP referral  Wakes Hall'),
                                  ('Essex MAP car transfer 2013','Essex MAP car transfer 2013'),
				  ('Essex - nhs referral','Essex - nhs referral'),
				  ('Essex Review 2013','Essex Review 2013'),
                                  ('Essex Self Refer Wakes Hall','Essex Self Refer Wakes Hall'),
                                  ('Essex Self Refer Drive Only WH','Essex Self Refer Drive Only Wakes Hall'),
                                  ('Essex Guardians Ref Home Visit','Essex Guardians Referral Home Visit'),
                                  ('Essex Guardians Ref Wakes Hall','Essex Guardians Referral Wakes Hall'),
                                  ('Information request','Information request'),
                                  ('Kings Lynn DVLA','Kings Lynn DVLA'),
                                  ('Kings Lynn Drive Only dvla','Kings Lynn ref by DVLA Drive Only'),
                                  ('Kings Lynn MAP referral','Kings Lynn MAP referral'),
				  ('Kings Lynn - nhs referral','Kings Lynn - nhs referral'),
				  ('Kings Lynn Review 2015','Kings Lynn Review 2015'),
                                  ('Kings Lynn Self Refer','Kings Lynn Self Refer'),
                                  ('Kings Lynn Self refer drive only','Kings Lynn Self refer drive only'),
                                  ('Thetford Access to Work','Thetford Access to Work'),
                                  ('Thetford Car Transfer','Thetford Car Transfer'),
                                  ('Thetford DFW','Thetford DFW'),
                                  ('Thetford Drive Only','Thetford Drive Only'),
                                  ('Thetford Drive Only dvla','Thetford ref by DVLA Drive Only'),
                                  ('Thetford DVLA','Thetford DVLA'),
                                  ('Thetford Legal 2013','Thetford Legal 2013'),
                                  ('Thetford MAP Car transfer','Thetford MAP Car transfer'),
                                  ('Thetford MAP referral','Thetford MAP referral'),
				  ('Thetford - nhs referral','Thetford - nhs referral'),
				  ('Thetford Review 2013','Thetford Review 2013'),
                                  ('Thetford PV','Thetford PV'),
                                  ('Thetford Self Refer','Thetford Self Refer'),
                                  ('Spalding Access to Work','Spalding Access to Work'),
                                  ('Spalding Car Transfer','Spalding Car Transfer'),
                                  ('Spalding Drive Only dvla','Spalding Drive Only dvla'),
                                  ('Spalding DVLA','Spalding DVLA'),
                                  ('Spalding Legal 2013','Spalding Legal 2013'),
                                  ('Spalding MAP referral','Spalding MAP referral'),
				  ('Spalding - nhs referral','Spalding - nhs referral'),
				  ('Spalding Review 2013','Spalding Review 2013'),
                                  ('Spalding Self refer','Spalding Self refer'),
                                  ('Spalding Self refer drive only','Spalding Self refer drive only'),
                                  ], 'Docs'),
        'is_dvla':fields.boolean('Is it DVLA'),
        'is_agent':fields.boolean('Is Agent'),
        'is_client':fields.boolean('Is Client'),
        'report_template':fields.selection([('full_driving_assessment_template', 'Standard Assessment Report Template'),
                                            ('dvla_report_template', 'DVLA Reprt Template')], 'Template'),
        'report_template_id':fields.many2one('cmc.assessment.report', 'Template'),
        'dvla_medical_advisor':fields.char('DVLA Medical Advisor',size=100),
        'owner': fields.many2one('res.users', 'Assessor'),
        'is_close':fields.boolean('Is the Assesment Closed'),
        'is_completed':fields.boolean('Is the Assesment Completed'),
        'total_cost':fields.float('Total Cost',digits=(255,2)),
        'total_balance':fields.float('Total Received',digits=(255,2)),
        'appointment_completed_date':fields.datetime('Appointment Complete Date'),
        'appointment_completed_d':fields.date('Appointment Completion Date'),
        'invoice_status':fields.char('Invoice',size=100),
        'ilme_paperwork':fields.selection([('mobility_assessment_form','MOBILITY ASSESSMENT FORM'),
                                            ('enviromental_assessment_form','ENVIRONMENT Ax FORM'),
                                            ('enviromenrmobility_assessment_form','COMBINED MOBILITY AND ENVIRONMENTAL Ax FORM')],'Assessment Forms'),
        'cancel_date':fields.datetime('Cancellation date'),
        'invoice_no':fields.char('Invoice No',size=100),
        'dvla_medical_advisor':fields.char('DVLA Medical Advisor',size=100),
        'dummy_docs':fields.char('Dummy Appointment',size=100),
        'dummy_paperwork':fields.char('Dummy Appointment',size=100),
		'dvla_report_date':fields.datetime('Report Date Time'),
        'current_owner_id': fields.function(_get_default_detail, method=True, type='many2one', relation='res.users', string='Assessor',store=True),
        'invoice_produced':fields.boolean('Invoice Produced'),
        'date_closed':fields.date('Date Closed'),
        'extra_report_attachement':fields.one2many('ead.extra.reports', 'res_id', ''),
        'refund':fields.float('Refund',digits=(255,2))
     }
    _default = {
        'uploaded_final_report': lambda * a: False,
        'is_dvla': lambda * a: False,
        'is_client': lambda * a: True,
        'is_close': lambda * a: False,
        'is_completed':lambda * a: False,
        'dummy': lambda * a: 'full_driving_assessment',
    }
    def onchange_review_date(self, cr, uid, ids, time, context={}):
        values = {}
        values['value'] = {}
        time = int(time)
        values['value']['review_date'] = (datetime.datetime.now() + datetime.timedelta(time * 365 / 12)).strftime("%Y-%m-%d")
        return values
    def onchange_balance(self, cr, uid, ids, cost,debit, context={}):
        values = {}
        values['value'] = {}
        values['value']['total_balance'] = cost-debit
        return values
    def onchange_dummy_doc(self, cr, uid, ids, doc,context={}):
        values = {}
#        debug(doc)
        values['value'] = {}
        values['value']['dummy_docs']=doc
        return values
    
    def onchange_referrer_type(self, cr, uid, ids, type,assessment_type,context={}):
        values = {}
        values['value'] = {}
        values['value']['total_cost'] = 0
        if type:
            query="select price from cmc_assessment_price where referrer_type='"+type+"' and type='"+assessment_type+"'"
            cr.execute(query)
            price_id=cr.fetchone()
            if price_id is None:
                values['value']['total_cost'] = 0
            else:
                values['value']['total_cost'] = price_id[0]
        values['value']['total_balance']=values['value']['total_cost']
        return values
cmc_assessment()
