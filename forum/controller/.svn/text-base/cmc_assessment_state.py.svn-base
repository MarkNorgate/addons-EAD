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

class cmc_assessment_state(osv.osv):
    _name = 'cmc.assessment.state'
    _description = 'cmc.assessment.state'
    _rec_name = 'name'
    _order='name'
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False):
        
        if args:
            if isinstance(args, basestring):
                if args.rfind('id=')==0:
                   if str(args.split("=")[1]) == 'None':
                        cr.execute("SELECT id FROM cmc_assessment_state order by name asc")
                   else:
                        cr.execute('SELECT s.id FROM cmc_assessment_state as s ' \
                                   'inner join cmc_assessment a ' \
                                   'on (a.id = '+str(args.split("=")[1])+' and a.driving_assessment_type = s.type) order by s.name asc')
                   ids = cr.fetchall()
                   if not ids:
                       if count:
                           return 0
                       ids = []
                   else:
                        ids = [x[0] for x in ids]
                   args = [('id','in',ids)]
        ids = super(cmc_assessment_state, self).search(cr, uid, args, offset=offset, 
                                                limit=limit, order=order, 
                                                context=context, count=False)
        if not ids:
            if count:
                return 0
            return []
        return ids
    
    _columns = {
        'name':fields.char('Name',size=200,required=True),
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
                                ("NHS referral - driving new","NHS referral - driving new"),
                                ("zz Non Forum Advice Session","zz-Non-Forum Advice Session"),
								("Review Assessment","Review Assessment")], 
                'Action Type', required=True),
    }
cmc_assessment_state()
