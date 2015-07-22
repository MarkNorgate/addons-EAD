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
# This is communication log of the assessments 
#===============================================================================


class cmc_assessment_communication(osv.osv):
    _name='cmc.assessment.communication'
    _description='cmc.assessment.communication'
    _columns={
          'comm_date':fields.datetime('Date'),
          'assessment_id':fields.many2one('cmc.assessment','Assessment'),
          'appointment_id':fields.many2one('cmc.appointments','Appointment'),
          'type':fields.char('Type',size=255),
          'client_name':fields.many2one('cmc.person','Client Name'),
          'subject':fields.char('Subject',size=255),
          'message':fields.char('Message',size=255),
          'user_id':fields.many2one('res.users','User')
        }
    
cmc_assessment_communication()