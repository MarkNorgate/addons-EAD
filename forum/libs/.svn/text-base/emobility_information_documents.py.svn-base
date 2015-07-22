# -*- encoding: utf-8 -*-
from osv import fields, osv
from tools.misc import debug
import datetime

# object for leaflets of URLs 
# object Name="mobility.attachments"

class emobility_information_documents(osv.osv):
    _name = "emobility.information.documents"
    _inherit = "ir.attachment"
    _description = "emobility.information.document"

    _columns = {
        'type':  fields.selection([
                ('file', 'File'),
                ('url', 'URL')],
                "Document Type", required=True),
        'url': fields.char('Document URL', size=255),
        'name': fields.char('Attachment Name',size=64, required=True),
        'datas': fields.binary('Data'),
        'datas_fname': fields.char('Filename',size=64),
        'description': fields.text('Description'),
    }

emobility_information_documents() 

# object for Communication Document to be used to attach with communication
# object Name="emobility.document"

