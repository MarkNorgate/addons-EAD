from osv import fields, osv
from tools.misc import debug

class assessment_attachments(osv.osv):
    def btn_delete_attachment(self, cr, uid, ids, context={}):
        cr.execute("delete from assessment_attachments where id='%s'" % (ids[0]))
        return
    _name = "assessment.attachments"
    _inherit = "ir.attachment"
    _description = "assessment.attachments"
    _columns = {
        'name': fields.char('Name', size=64),
        'datas_fname': fields.char('Filename', size=64),
        'datas': fields.binary('Data'),
        'import_url':fields.char('Import File Name', size=255)
    }
assessment_attachments()

class ead_extra_reports(osv.osv):
    _name = "ead.extra.reports"
    _inherit = "ir.attachment"
    _description = "assessment.attachments"
    _columns = {
        'name': fields.char('Name', size=64),
        'datas_fname': fields.char('Filename', size=64),
        'datas': fields.binary('Data'),
        }                 
ead_extra_reports()


class equipment_attachments(osv.osv):
    _name = "equipment.attachments"
    _inherit = "ir.attachment"
    _description = "equipment.attachments"
    _columns = {
        'name': fields.char('Name', size=64),
        'datas_fname': fields.char('Filename', size=64),
        'datas': fields.binary('Data'),
        'equipment_id':fields.many2one('cmc.equipment', '')
    }
equipment_attachments()

class equipment_supply_attachments(osv.osv):
    _name = "equipment.supply.attachments"
    _inherit = "ir.attachment"
    _description = "equipment.attachments"
    _columns = {
        'name': fields.char('Name', size=64),
        'datas_fname': fields.char('Filename', size=64),
        'datas': fields.binary('Data'),
        'equipment_supply_id':fields.many2one('cmc.equipement.supply.process', '')
    }
equipment_supply_attachments()

class workshop_attachments(osv.osv):
    _name = "workshop.attachments"
    _inherit = "ir.attachment"
    _description = "workshop.attachments"
    _columns = {
        'name': fields.char('Name', size=64),
        'datas_fname': fields.char('Filename', size=64),
        'datas': fields.binary('Data'),
        'workshop_id':fields.many2one('cmc.workshop.process', '')
    }
workshop_attachments()

class person_attachments(osv.osv):
    _name = "person.attachments"
    _inherit = "ir.attachment"
    _description = "person.attachments"
    
    def btn_download(self, cr, uid, ids, context={}):
        prev_record = self.browse(cr, uid, ids[0])
        return {
            'type': 'ir.actions.act_url',
            'url':'http://cmc.emobilitysystem.co.uk/static/documents/' + prev_record.import_url.replace('\\', '/'),
            'target': 'self'
        }
        
    _columns = {
        'name': fields.char('Name', size=64),
        'datas_fname': fields.char('Filename', size=64),
        'datas': fields.binary('Data'),
        'person_id':fields.many2one('cmc.person', ''),
        'import_url':fields.char('Import File Name', size=255)
    }
person_attachments()

class user_attachments(osv.osv):
    _name = "user.attachments"
    _inherit = "ir.attachment"
    _description = "user.attachments"
    
    _columns = {
        'name': fields.char('Name', size=64),
        'datas_fname': fields.char('Filename', size=64),
        'datas': fields.binary('Data'),
        'user_id':fields.many2one('res.users', ''),
        'import_url':fields.char('Import File Name', size=255)
    }
user_attachments()

