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
# This is master table of equipment where the wheelchair and appointment takes place
#===============================================================================
#class cmc_asset_type(osv.osv):
#    _name = 'cmc.asset.type'
#    _description = 'cmc.asset.type'
#    _rec_name='name'
#   
#    _columns={
#     'name': fields.char('Name', size=255)
#             }
#cmc_asset_type()

class cmc_equipment(osv.osv):
    _name = 'cmc.equipment'
    _description = 'cmc.equipment'
    _rec_name = 'model'
    
    def create(self, cr, uid, vals, context={}):
        debug('CREATE EQUIPMENT')
        debug(vals)
        vals['state'] = 'in_stock'
        if 'is_external' in vals:
            if vals['is_external']:
                vals['state'] = 'external'
		if 'current_user_id' in vals:
			person=pooler.get_pool(cr.dbname).get('cmc.person').browse(cr,uid,vals['current_user_id'])
			if person.display_name.strip()=='North East Drive Mobility' or person.display_name.lower().strip()=='pct assets':
				vals['owner_cmc_pct']=True
        if 'owner' in vals:
            if not vals['owner']:
                raise except_orm('Warning', 'Please Provide Owner') 
        
        
        return super(cmc_equipment, self).create(cr, uid, vals, context)
    def write(self, cr, uid, ids, vals, context={}):
        debug("<<EQUIPMENT WRITE MODE>>")
        debug(vals)
        debug(ids)
        if not context.get('booked', False) or not context.get('bypass', False):
            prev_record = self.browse(cr, uid, ids[0])
            owner_table = pooler.get_pool(cr.dbname).get('cmc.user.owner.equipment.history')
            #===================================================================
            # Equipment checking 
            #===================================================================
            if 'owner' in vals:
                if vals['owner'] != prev_record.owner.id :
                    owner_table.create(cr, uid, {
                                                   'name':prev_record.owner.display_name,
                                                   'name_owner_id':prev_record.id,
                                                   'date_ownership':datetime.datetime.now().strftime("%Y-%m-%d"),
                                                   'person_id':prev_record.owner.id
                                                   })
                                                   
                if not vals['current_user_id'] and (prev_record.owner.display_name=='North East Drive Mobility' or prev_record.owner.display_name=='PCT Assets'):
                    debug("Found")
                    vals['state']='in_stock'
                else:
                    vals['state']='external'   
                if vals['current_user_id'] != prev_record.current_user_id.id :
                    owner_table.create(cr, uid, {
                                                   'name':prev_record.current_user_id.display_name,
                                                   'name_history_id':prev_record.id,
                                                   'date_ownership':datetime.datetime.now().strftime("%Y-%m-%d"),
                                                   'person_id':prev_record.current_user_id.id
                                                   })
        return super(cmc_equipment, self).write(cr, uid, ids, vals, context)
    
    
    def btn_booked(self, cr, uid, ids, context={}):
        debug(context)
        vals = {'state':'booked',
            }
        debug(ids)
        self.write(cr, uid, ids[0], vals, {'booked':'book'})
        return
    
    def _id_default(self, cr, uid, context={}):
        debug(context)
        query = "select id from cmc_person where display_name='East Anglia Drive Centre'"
        cr.execute(query)
        ids = cr.fetchone()
        debug(ids)
        if ids is not None :
            return ids[0]
        else:
            return False
    def _filter(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        debug("Filter Process")
        debug(ids)
        for m in self.browse(cr, uid, ids):
            debug(m)
            debug(m.state)
            is_stock=is_search=in_app=False
            if m.owner:
                if (m.owner.display_name.strip()=='North East Drive Mobility' \
                or m.owner.display_name.strip()=='PCT Assets') and not m.current_user_id and m.state=='in_stock':
                    is_stock=True
                if m.owner.display_name.strip()=='North East Drive Mobility' and not m.current_user_id:
                    in_search=True
                if m.current_user_id:
                    if m.owner.display_name.strip()=='North East Drive Mobility' and (m.current_user_id.display_name.strip()=='North East Drive Mobility') and not m.is_external:
                        in_app=True
            res[m.id]={'in_stock_filter':is_stock,
                       'in_se_filter':is_search,
                       'in_app':in_app}
        return res
    _columns = {
        'state':fields.selection([('external', 'External'),
                                  ('in_stock', 'In Stock'),
                                  ('supplied', 'Supplied'),
                                  ('booked', 'Reserved'),
                                  ('sold', 'Sold'),
                                  ('ordered', 'Ordered'),
                                  ('destroyed', 'Destroyed')], 'State'),
        'make':fields.char('Make', size=255, required=True),
        'model':fields.char('Model', size=255, required=True),
        'serial_no':fields.char('Serial Number', size=255),
        'size':fields.char('Size', size=255),
        'manufacture_date':fields.date('Date Received'),
        'asset_type':fields.selection([('Wheelchair Manual SP-Basic Manual','Wheelchair Manual SP-Basic Manual'),
                                       ('Wheelchair Manual SP-Manual with seating system','Wheelchair Manual SP-Manual with seating system'),
                                       ('Wheelchair Manual TR-Basic Manual','Wheelchair Manual TR-Basic Manual'),
                                       ('Wheelchair Manual TR-Manual with seating system','Wheelchair Manual TR-Manual with seating system'),
                                       ('Powerhubs','Powerhubs'),
                                       ('Wheelchair powered-Basic', 'Wheelchair powered-Basic'),
                                       ('Powerpack-User controllable','Powerpack-User controllable'),
                                       ('Powerpack-Attendant controllable','Powerpack-Attendant controllable'), 
                                        ('Wheelchair Powered - With electric seating', 'Wheelchair Powered - With electric seating'),
                                        ('Wheelchair Powered - Stand up', 'Wheelchair Powered - Stand up'),
                                       ('Walking Aid', 'Walking Aid'),
                                       ('Scooter-Boot', 'Scooter-Boot'),
                                       ('Scooter-Mid Size', 'Scooter-Mid Size'),
                                       ('Scooter-Large Size', 'Scooter-Large Size'),
                                       ('Powerhubs', 'Powerhubs'),
                                       ('Bath Lift-Portable', 'Bath Lift-Portable'),
                                       ('Bath Lift-Fixed', 'Bath Lift-Fixed'),
                                       ('Riser Recliner', 'Riser Recliner'),
                                       ('Wheeled Walker', 'Wheeled Walker'),
                                       ('Hoist-Portable', 'Hoist-Portable'),
                                       ('Hoist-Fixed', 'Hoist-Fixed'),
                                       ('Hoist-Overhead', 'Hoist-Overhead'),
                                       ('Bed-Manual', 'Bed-Manual'),
                                       ('Bed-Electric', 'Bed-Electric'),
                                       ('Vehicle', 'Vehicle'),
                                       ('Buggy','Buggy'),
                                       ('Other','Other')], 'Asset Type', required=True),
        'other_asset':fields.char('Other',size=100),
        'owner': fields.many2one('cmc.person', 'Owner'),
        'onwer_asset_no':fields.char('Owner Asset Number', size=255),
        'current_user_id': fields.many2one('cmc.person', 'Current User'),
        'cmc_onwer_history': fields.one2many('cmc.user.owner.equipment.history', 'name_owner_id', ''),
        'cmc_user_history': fields.one2many('cmc.user.owner.equipment.history', 'name_history_id', ''),
        'appointment_ids': fields.many2many('cmc.appointments', 'equipment_appointment_rel',
                    'equipment_id',
                    'appointment_id'),
        'appointment_reminder_ids':fields.one2many('cmc.appointments', 'reminder_id', 'Ids'),
        'attachments':fields.one2many('equipment.attachments',
                                 'equipment_id', 'Attachment'),
        'equipment_supply':fields.one2many('cmc.workshop.process', 'equipment_id', 'Id'),
        'price':fields.float('Price'),
        'color':fields.char('Color', size=255),
        'order_no':fields.char('Order Number', size=100),
        'is_external':fields.boolean('Is External', size=100),
        'equipment_parent_id':fields.char('Equipment Parent Id', size=10), #Dont use this name else where
        'year':fields.char('Year',size=100),
        'type':fields.selection([('Auto','Auto'),('Manual','Manual')],'Type'),
        'multiplex':fields.boolean('Multiplex'),
        'existing_adaptations':fields.text('Existing Adaptations'),
        'owner_cmc_pct':fields.boolean('Owner_cmc_pct'),
        'pdi_required':fields.boolean('PDI Required'),
        'pdi_completion_date':fields.date('PDI Completion Date'),
        'supplier_id':fields.many2one('cmc.person','Supplier'),
        'in_stock_filter':fields.function(_filter, method=True, type='boolean', string='In Stock Filter',store=True,multi="client_contact"),
        'in_se_filter':fields.function(_filter, method=True, type='boolean', string='In SearchFilter',store=True,multi="client_contact"),
        'in_app':fields.function(_filter, method=True, type='boolean', string='In Appointment',store=True,multi="client_contact"),
        'date_ordered':fields.date('Date Ordered'),
		'equipment_supply_process_id':fields.many2one('cmc.equipement.supply.process', 'Equipment Supply Id'),
     }
    
    _defaults = {
    'owner':_id_default,
    }
    def onchange_asset(self, cr, uid, ids, parent_id, context={}):
        values = {}
        debug(parent_id)
        values['value'] = {}
        if parent_id:
            values['value']['owner'] = parent_id
            values['value']['current_user_id'] = parent_id
        return values
cmc_equipment()

class cmc_onwer_history(osv.osv):
    _name = 'cmc.user.owner.equipment.history'
    _description = 'cmc.user.owner.equipment.history'
    _rec_name = 'name'
     
    _columns = {
       
       'name':fields.char('Name', size=100),
       'name_owner_id':fields.many2one('cmc.equipment', 'Ids'),
       'name_history_id':fields.many2one('cmc.equipment', 'Ids'),
       'person_id':fields.many2one('cmc.person', 'Ids'),
       'date_ownership':fields.date('Owner Ship Date'),
       }
cmc_onwer_history()


