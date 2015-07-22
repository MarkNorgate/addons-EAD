from osv import fields, osv
from tools.misc import debug
import pooler

# communication object to record all interactions with the client or internal
# category will be used to separate different types of communications
# call, enquiry, assessment, complaint are some of them.
class super_communication(osv.osv):
    _name = 'super.communication'
    _description = 'super.communication'
    
    _columns = {
            'date':fields.datetime('Date'),
            'user_id':fields.many2one('res.users', 'User'),
            'from':fields.char('From', size=100),
            'to':fields.char('To', size=100),
            'type':fields.selection([
                 ('Telephone', 'Telephone'),
              ('Email', 'Email'),
              ('Fax', 'Fax'),
              ('Letter', 'Letter'),
              ('In Person', 'In Person'),
              ('Other', 'Other')], 'Type'),
            'subject':fields.char('Subject', size=100),
            'message':fields.text('Message'),
            'category':fields.char('Category', size=100),
            'datas': fields.binary('File', help='The Email Message if available'),
            'attachments':fields.one2many('emobility.communication.document', 'communication_id', 'Communication Record')
        }
super_communication()