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

#===============================================================================
# This is master table of equipment where the wheelchair and appointment takes place
#===============================================================================

class cmc_assessment_price(osv.osv):
    _name = 'cmc.assessment.price'
    _description = 'cmc.assessment.price'
    _rec_name = 'price'
	
    def create(self, cr, uid, vals, context={}):
        cr.execute("select count(id) from cmc_assessment_price where type='%s' and price=%f" %(vals['type'],vals['price']))
        count=cr.fetchone()
        if len(count)>0:
            raise except_orm('Warning','This price is already associated with the selected assessment type')
        
        return super(cmc_assessment_price, self).create(cr, uid, vals, context)
    _columns = {
        'price':fields.float('Cost'),
        'type':fields.selection([
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
                                ("zz Non Forum Advice Session","zz-Non-Forum Advice Session"),
								("Review Assessment","Review Assessment")], 
                'Action Type', required=True),
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
    }
cmc_assessment_price()
