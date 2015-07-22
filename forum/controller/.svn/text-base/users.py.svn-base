# -*- encoding: utf-8 -*-
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
import time


class cmc_users(osv.osv):
    _name = "res.users"
    _inherit = "res.users"
    
    _columns = {
        'email': fields.char('Email Address', size=128),
        'attachment_id':fields.one2many('user.attachments','user_id','Attachments'),

         }
cmc_users()

