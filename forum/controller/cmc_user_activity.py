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

 #==============================================================================
 # object to record all activities related with a person
 # this object will be inserted with records by all objects that inherit the cmc.osv object 
 # primary use is to track who looked at the client records which is person object
 #==============================================================================

class cmc_user_activity(osv.osv):
    _name = "cmc.user.activity"
    _rec_name ='activity'
    _order = "date desc"
    _columns = {
        'date': fields.datetime('When', readonly=True),
        'user_id': fields.many2one('res.users', 'Who', readonly=True),
        'activity':fields.char('What',size=255, readonly=True),
        'type':fields.char('How',size=64, readonly=True),
        'client_id':fields.many2one('cmc.person','Client', readonly=True),
        'person_id':fields.many2one('cmc.person','Client', readonly=True),
        'agent_id':fields.many2one('cmc.person','Agent', readonly=True),
        'call_id':fields.many2one('cmc.call.history','Call', readonly=True),
        'assessment_id':fields.many2one('cmc.assessment','Assessment', readonly=True),
        'enquiry_id':fields.many2one('cmc.enquiry','Action', readonly=True),
       }
cmc_user_activity()