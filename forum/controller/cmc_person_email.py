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


class email_address(osv.osv):
    _name = "cmc.person.email"
    _description = "cmc.person.email"

    _columns = {
        'email_type':fields.selection([('home','Home'),
                                         ('work','Work'),
                                         ('previous','Previous')],'Type'),
        'email_address': fields.char('Email Address', 
                            size=255 
                            ),

        'email_description':fields.char('Email Description',size=255),
        
         'person_id':fields.many2one('cmc.person','')
        
        }
email_address()
        
