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


class cmc_person_telephone(osv.osv):
    _name = "cmc.person.telephone"
    _description = "cmc.person.telephone"
    _rec_name='telephone'

    _columns = {
        'telephone_type':fields.selection([('home','Home'),
                                         ('work','Work'),
                                         ('mobile','Mobile'),
                                         ('previous','Previous')],'Type'),
        'telephone':fields.char('Number', 
                            size=255),

        'extension':fields.char('Extension',size=255 ),
        
        'description':fields.char(' Description', 
                                size=255),

         'person_id':fields.many2one('cmc.person','')                          
        }
cmc_person_telephone()
    