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



#===============================================================================
# This is for equipment supply process through every equipement process and enquiry create.
#===============================================================================



class cmc_equipment_supply_process(osv.osv):
    _name = 'cmc.equipement.supply.process'
    _description = 'cmc.equipement.supply.process'
    _rec_name = 'equipment_supply_id'
    
    
    def create(self, cr, uid, vals, context):
        seq_id = self.pool.get('ir.sequence').search(cr, uid, [('name', '=', 'CMC Equipment')])[0]
        new_id = self.pool.get('ir.sequence').get_id(cr, uid, seq_id)
        vals['equipment_supply_id'] = str(new_id)
        return super(cmc_equipment_supply_process, self).create(cr, uid, vals, context)
    def write(self,cr,uid,ids,vals,context={}):
        prev_record=self.browse(cr,uid,ids[0])
        if 'equipment_parent_id' in vals:
            prev_recrd_e_id=[]
            new_add=[]
            remove_li=[]
            for e_id in prev_record.equipment_parent_id:
                    prev_recrd_e_id.append(e_id.id)
            new_add=vals['equipment_parent_id'][0][2]
            remove_li=prev_recrd_e_id
            if len(remove_li) >0:
                    debug(remove_li)
                    update_eq_remove_query="update cmc_equipment set state='in_stock' where id in("+','.join([str(u) for u in remove_li])+")"
                    cr.execute(update_eq_remove_query)
                    debug(update_eq_remove_query)
            if len(new_add) >0:
                    debug(new_add)
                    update_eq_new_query="update cmc_equipment set state='booked' where id in("+','.join([str(u) for u in new_add])+")"
                    debug(update_eq_new_query)
                    cr.execute(update_eq_new_query)
        return super(cmc_equipment_supply_process, self).write(cr, uid, ids,vals, context)
    def btn_equipment_supplied(self,cr,uid,ids,context={}):
        debug(ids)
        e=self.browse(cr,uid,ids[0])
        debug(e.client_id.id)
        query="update cmc_equipment set state='supplied',owner='"+str(e.client_id.id)+"',current_user_id='"+str(e.client_id.id)+"' where (state='in_stock' or state='booked') and id in (select supply_id from equipment_equipment_rel where equipment_id="+str(ids[0])+")"
        debug(query)
        try:
            query="update cmc_equipment set state='supplied',owner='"+str(e.client_id.id)+"',current_user_id='"+str(e.client_id.id)+"' where (state='in_stock' or state='booked') and id in (select supply_id from equipment_equipment_rel where equipment_id="+str(ids[0])+")"
            debug(query)
            cr.execute(query)
            pooler.get_pool(cr.dbname).get('cmc.user.activity').create(cr, uid, {
                                   'date': datetime.datetime.now(),
                                   'user_id': uid,
                                   'type': 'Equipment',
                                   'activity':'Equipment Ordered',
                                   'person_id':e.client_id.id})
        except:
            raise except_orm('Warning','No Equipment Record')
        return
    def _client_id_default(self,cr,uid,context={}):
        debug(context)
        person_id=context.get('person_id',False)
        return person_id
    _columns = {
    'equipment_supply_id':fields.char('Id', size=255),
    'create_date_equipment':fields.date('Created on'),
    'client_id': fields.many2one('cmc.person', 'User'),
    'equipment_parent_id':fields.many2many('cmc.equipment', 'equipment_equipment_rel', 'supply_id', 'equipment_id', 'Enquipment in Stock', domain=[('state', '=', 'in_stock')]),
    'equipment_details':fields.text('Equipment Details'),
    'allocated_user_id': fields.many2one('res.users', 'User Allocated'),
    'allocated_user_group_id': fields.many2one('res.groups', 'Group Allocated'),
    'state':fields.selection([('pending_equipment_indentification', 'Pending Equipment Indentification'),
                               ('pending_equipment_ordered', 'Pending Equipment Ordered'),
                               ('pending_equipment_receipt_from_supplier', 'Pending Equipment Receipt From supplier'),
                               ('pending_equipment_delivery', 'Pending Equipment Delivery'),
                               ('pending_closure', 'Pending Closure'),
                               ('Cancel','Cancel')
                               ], 'States', required=True),
    'appointment_ids':fields.one2many('cmc.appointments', 'equipment_supply_process_id', 'Appointment'),
    'equipment_ordered':fields.one2many('cmc.ordered.equipment.master', 'equipment_supply_process_id', 'Equipments'),
    }
    _defaults = {
        'create_date_equipment': lambda *a: datetime.datetime.now().strftime("%d/%m/%Y"),
        'client_id': _client_id_default,
    }
cmc_equipment_supply_process()

class cmc_appointments(osv.osv):
    _name = 'cmc.appointments'
    _description = 'cmc.appointments'
    _rec_name = 'apmnt_start_date'
    _inherit = 'cmc.appointments'
    
    _columns = {
     'equipment_ids': fields.many2many('cmc.equipment', 'equipment_appointment_rel',
                                'appointment_id',
                                'equipment_id'),
     'reminder_id':fields.many2one('cmc.equipment', 'Equipment Reminder'),
     'equipment_supply_process_id':fields.many2one('cmc.equipement.supply.process', 'Equipment Supply Process'),
     'workshop_id':fields.many2one('cmc.workshop.process', 'Workshop'),
        }
cmc_appointments()

class cmc_ordered_equipment_master(osv.osv):
    _name='cmc.ordered.equipment.master'
    _description='cmc.ordered.equipment.master'
    _rec_name='model'
    
    def create(self, cr, uid, vals, context):
        seq_id = self.pool.get('ir.sequence').search(cr, uid, [('name', '=', 'CMC Equipment Master')])[0]
        new_id = self.pool.get('ir.sequence').get_id(cr, uid, seq_id)
        vals['order_no'] = str(new_id)
        return super(cmc_ordered_equipment_master, self).create(cr, uid, vals, context)
    
    def btn_cancel(self,cr,uid,ids,context={}):
        debug(context)
        debug(ids)
        pooler.get_pool(cr.dbname).get('cmc.ordered.equipment.master').write(cr,uid,ids[0],{'state':'Cancel'},context)
        return 
    
    _columns ={
    'order_no':fields.char('Order Number',size=100),
    'date_ordered':fields.date('Date Ordered'),
    'make':fields.char('Make',size=100),
    'model':fields.char('Model',size=100),
    'state':fields.selection([('Ordered','Ordered'),('Recieved','Recieved'),('Cancel','Cancel')],'Status'),
    'price':fields.float('Price'),
    'equipment_supply_process_id':fields.many2one('cmc.equipement.supply.process', 'Reminder',domain="[('state','=','Ordered')]"),
    'manufacture_date':fields.date('Date Received'),
    'color':fields.char('Color',size=255),
    'serial_no':fields.char('Serial Number', size=255),
    'owner':fields.many2one('cmc.person','Owner')
    
    }
cmc_ordered_equipment_master()