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

class cmc_communication(osv.osv):
    _name='cmc.communication'
    _inherit = "emobility.communication"
    _description='cmc.communication'
    _columns={
              'person_id':fields.many2one('cmc.person','Person'),
              'call_id':fields.many2one('cmc.call.history','Call'),
              'assessment_id':fields.many2one('cmc.assessment','Assessment'),
              'enquiry_id':fields.many2one('cmc.enquiry','Action'),
              'attachments':fields.one2many('cmc.attachment', 'communication_id', 'Communication Record')

    }
    
cmc_communication()

class emobility_communication_document(osv.osv):
    _name = "cmc.attachment"
    _description = "cmc.attachment"
    _rec_name = "name"
    _order = "date desc"
    
    def create(self, cr, uid, vals, context={}):
        msg = []
        
        if not vals['name']:
            msg.append('You must provide title for the attachment!\n\n')
        if 'datas' not in vals:
            msg.append('You must attach a document!\n\n')
        if len(msg)>0:
            raise osv.except_osv('Attachment missing!', ' '.join(msg))
        vals['user_id'] = uid
        #vals['name'] = vals['datas_fname']
        vals['state'] = 'complete'
        vals['date'] = datetime.datetime.now()
        
        return super(emobility_communication_document, self).create(cr, uid, vals, context)
    
    _columns = {
        'date': fields.datetime('Date', readonly=True),
        'communication_id': fields.many2one('cmc.communication', 'Communication'),
        'user_id':fields.many2one('res.users','User'),
        'person_id':fields.many2one('cmc.person','Person'),
        'call_id':fields.many2one('cmc.call.history','Call'),
        'assessment_id':fields.many2one('cmc.assessment','Assessment'),
        'enquiry_id':fields.many2one('cmc.enquiry','Action'),
        'user_id':fields.many2one('res.users', 'User'),
        'name': fields.char('Attachment Name',size=64),
        'datas': fields.binary('Data'),
        'datas_fname': fields.char('Filename',size=64),
        'description': fields.text('Description'),
        'state': fields.selection([
            ('none', 'None'),
            ('complete', 'Complete')],
            'Status', required=True),
    }
    _default = {
        'user_id': lambda self,cr,uid,ctx : uid,
        'state': lambda self,cr,uid,ctx : 'none',
        'date': lambda * a: datetime.datetime.now(),
    }

emobility_communication_document() 
