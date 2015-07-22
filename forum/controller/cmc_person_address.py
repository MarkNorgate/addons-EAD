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

class cmc_person_address(osv.osv):
    _name = "cmc.person.address"
    _description = "cmc.person.address"

    def create(self, cr, uid, vals, context={}):
        debug(context)
        
        debug(vals)
        
        return super(cmc_person_address, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context={}):
        debug(context)
        debug(vals)
        return super(cmc_person_address, self).write(cr, uid, ids, vals, context)
        
    _columns = {
                
        'organisation':fields.char('Organisation',
                      size=255),
        'address_line_1':fields.char('Address Line 1', size=255),
        'address_line_2':fields.char('Address Line 2', size=255),
        'address_type':fields.selection([('home','Home'),
                                         ('work','Work'),
                                         ('previous','Previous')],'Type'),
        'city':fields.char(' City',
                          size=255),
        'county':fields.char(' County',
                          size=255),
        'postcode':fields.char('PostCode',
                          size=255),
        'description':fields.char('Description',
                          size=255),
        'person_id':fields.many2one('cmc.person', '')
    }
    _defaults = {
    }
cmc_person_address()
                                                                                        
