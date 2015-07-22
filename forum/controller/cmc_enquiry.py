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
from osv.orm import except_orm

class cmc_enquiry(osv.osv):
    _name = 'cmc.enquiry'
    _description = 'cmc.enquiry'
    _rec_name = 'enquiry_id'
    _order = "enquiry_date desc"
    
    def create(self, cr, uid, vals, context={}):
        
        if 'indirect' not in context:
            enquiry_id=0
            seq_id = self.pool.get('ir.sequence').search(cr, uid, [('name', '=', 'CMC Action')])[0]
            new_id = self.pool.get('ir.sequence').get_id(cr, uid, seq_id)
            if context.get('person_id',False):
                person_id=context.get('person_id',False)
            else:
                person_id=vals['person_id']
            person_browse=pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, person_id)
            vals['enquiry_id'] = str(new_id)
            vals['user_id'] = uid
            vals['state'] = 'pending'
            vals['person_id'] = person_id
            if vals['type'] == 'client':
                vals['client_id'] = person_id
                
            else:
                vals['agent_id'] = person_id
                if person_browse.display_name==tools.config.options['organisation_name']:
                    vals['is_dvla']=True
                else:
                    vals['is_agent']=True
            vals['enquiry_date'] = datetime.datetime.now()
            if not vals['due_date']:
                vals['due_date'] = datetime.datetime.now()

            if vals['allocated_user_id'] and vals['allocated_user_group_id']:
                vals['allocated_user_id'] = False

            if not vals['allocated_user_id'] and not vals['allocated_user_group_id']:
                vals['allocated_user_id'] = uid

            if not vals['enquiry_details']:
                raise osv.except_osv('Action Details missing!',
                                     'You must provide action details while saving the action record!\n\n')
            enquiry_id = super(cmc_enquiry, self).create(cr, uid, vals, {'indirect':'check'})
            if enquiry_id > 0:
                pooler.get_pool(cr.dbname).get('cmc.user.activity').create(cr, uid, {
                     'date':datetime.datetime.now(),
                     'user_id': uid,
                     'activity':'New action ' + new_id + '  of type ' + vals['enquiry_type'] + ' created.',
                     'type':'Action',
                     'person_id':person_id,
                     'client_id':vals['client_id'] if vals['client_id'] else None,
                     'agent_id':None,
                     'enquiry_id': enquiry_id
                    })
                return True
        else:
            return super(cmc_enquiry, self).create(cr, uid, vals, {'indirect':'check'})
        
    
    def write(self, cr, uid, ids, vals, context=None):
        debug("ENQUIRY WRITE ")
        id = None
        if type(ids).__name__ == 'list':
            id = ids[0]
        else:
            id = ids
        enquiry = self.browse(cr, uid, id)
        if 'indirect' not in context and len(vals) > 1:
            if 'state' in vals:
                if vals['state'] == 'closed':
                    if 'comments' in vals:
                        vals['enquiry_details'] = 'Action CLOSED: ' + (vals['comments'] if vals['comments'] else "")  + '\n' + enquiry.enquiry_details
                if vals['state'] == 'Cancelled':
                    if 'comments' in vals:
                        vals['enquiry_details'] = 'Action Cancelled: ' + (vals['comments'] if vals['comments'] else "")  + '\n' + enquiry.enquiry_details
                    vals['complete_date'] = datetime.datetime.now()
        debug(vals)
        return super(cmc_enquiry, self).write(cr, uid, ids, vals, {'indirect':'check'})
    
    def btn_save(self, cr, uid, ids, context={}):
        cr.execute('select id from ir_ui_menu where name=\'Action Handling\'')
        view = cr.fetchone()
        debug(view)
        return    {
            'name': 'Actions Allocated To Me',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.enquiry',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': {'user_id':uid}
            }
    def btn_enquiry_completed(self, cr, uid, ids, context={}):
        enquiries = self.browse(cr, uid, ids)
        result = {}
        if len(enquiries) > 0 :
            enquiry = enquiries[0]
            pooler.get_pool(cr.dbname).get('cmc.user.activity').create(cr, uid, {
                 'date':datetime.datetime.now(),
                 'user_id': uid,
                 'activity':'Action ' + enquiry.enquiry_id+' of type '+str(enquiry.enquiry_type) + '  closed.',
                 'type':'Action',
                 'client_id':enquiry.client_id.id,
                 'agent_id':enquiry.agent_id.id,
                })
            self.write(cr, uid, ids, {'state':'closed'},context=context)
        
#        return  {
#            'domain': "[('allocated_user_id','=',%d), ('state', 'in', ['pending','awaiting'])]" % (uid),
#            'name': 'Actions Allocated To Me',
#            'view_type': 'form',
#            'view_mode': 'tree,form',
#            'res_model': 'cmc.enquiry',
#            'view_id': False,
#            'target': '_parent',
#            'type': 'ir.actions.act_window',
#            'context': {'user_id':uid}
#            }
    def btn_enquiry_cancelled(self, cr, uid, ids, context={}):
        context['indirect'] = 'check'
        self.write(cr, uid, ids, {'state':'Cancelled'}, context=context)
        enquiries = self.browse(cr, uid, ids)
        result = {}
        if len(enquiries) > 0 :
            enquiry = enquiries[0]
            pooler.get_pool(cr.dbname).get('cmc.user.activity').create(cr, uid, {
                 'date':datetime.datetime.now(),
                 'user_id': uid,
                 'activity':'Action ' + enquiry.enquiry_id+' of type '+str(enquiry.enquiry_type)+ ' cancelled.',
                 'type':'Action',
                 'client_id':enquiry.client_id.id,
                 'agent_id':enquiry.agent_id.id,
                 'call_id':enquiry.call_id.id,
                })
#        return  {
#            'domain': "[('allocated_user_id','=',%d), ('state', 'in', ['pending','awaiting'])]" % (uid),
#            'name': 'Actions Allocated To Me',
#            'view_type': 'form',
#            'view_mode': 'tree,form',
#            'res_model': 'cmc.enquiry',
#            'view_id': False,
#            'type': 'ir.actions.act_window',
#            'context': {'user_id':uid}
#            }

    def drving_name(self, type):
        t = {
            'general':'GENERAL',
            'full_driving_assessment': 'FULL DRIVING ASSESSMENT',
            'wheelchair_assessment':'WHEELCHAIR ASSESSMENT',
            'drive_from_wheelchair_assessment':'DRIVE FROM WHEELCHAIR ASSESSMENT',
            'passenger_adult':'Passenger Adult','passenger_child':'Passenger Child',
            'car_seat_harness_assessment':'CAR SEAT HARNESS ASSESSMENT',
            'driving_legal_assessment':'Driving Legal Assessment',
            'drive_safer_for_longer_assessment':'Drive Safer For Longer Assessment',
            'driving_adaptation_assessment':'Driving Adaptation Assessment',
            'mo_map_adapdation_assessment':'MO MAP Adaptation Assessment',
            'review_assessment':'Review Assessment',
            'wheel_walker':'Wheeled Walker',
            'chair_assessment':'Chair Assessment',
            'bathing_assessment':'Bathing Assessment',
            'other_ilme_equipment_assessment':'Other ILME Equipment Assessment',
            'buggy_assessment':'Buggy Assessment',
            'scooter_assessment':'Scooter Assessment',
            'pct_wheelchair_buggy':'PCT Wheelchair/Buggy',
            'hoist_demo':'Hoist Demo',
            'momap_access':'MO MAP Access',
            'pressure_mapping_assessment':'Pressure Mapping Assessment',
            'Equipment Supply Process':'Equipment Supply Process'
            }
        return t.get(type, '')
    
    _columns = {
        'enquiry_id':fields.char('Action Id', size=64),
        'enquiry_date': fields.datetime('Action Date', readonly=True),
        'user_id': fields.many2one('res.users', 'Created By'),
        'client_id':fields.many2one('cmc.person', 'Client'),
        'agent_id':fields.many2one('cmc.person', 'Agent'),
        'person_id':fields.many2one('cmc.person', 'Person'),
        'call_id':fields.many2one('cmc.call.history', 'Call'),
        'assessment_id':fields.one2many('cmc.assessment', 'enquiry_id', ''),
        'due_date': fields.datetime('Due Date'),
        'type':fields.selection([('client', 'Client'),
                                 ('agent', 'Agent')], 'Is The Following Person is', required=True),
        'enquiry_type':fields.selection([
                ('General', 'General'),
                ('Return Call','Return Call'),
                ('Equipment Supply Process','Equipment Supply Process'),
                ('Adaptation Process','Adaptation Process'),
                ('Workshop Process','Workshop Process'),
                ('Accounting Process','Accounting Process')
                ], 'Action Type', required=True),
        'enquiry_details': fields.text('Action Details', readonly=True),
        'comments': fields.text('Comments'),
        'allocated_user_id': fields.many2one('res.users', 'User Allocated'),
        'allocated_user_group_id': fields.many2one('res.groups', 'Group Allocated'),
        'send_date': fields.datetime('Post Sent on'),
        'documents': fields.many2many('emobility.information.documents',
                                        'cmc_enquiry_information_documents_rel',
                                        'enquiry_id', 'id', 'Send Documents',
                                        states={'complete':[('readonly', True)]}),
        'paying':fields.selection([('client_paying', 'Client'),
                                   ('agent_paying', 'Agent')],
                                    'Who is paying?'),
                                        
        'state': fields.selection([
                           ('none', 'None'),
                           ('pending', 'Pending Action'),
                           ('awaiting', 'Awaiting Client Response'),
                           ('closed', 'Closed'),
                           ('Cancelled','Cancelled')],
                           'State', required=True),
        'complete_date': fields.datetime('Completion Date', change_default=True, readonly=True),
        'dummy': fields.char('Dummy', size=64),
        'email_check':fields.boolean('Email'),
        'is_client':fields.boolean('Is Client'),
        'is_agent':fields.boolean('Is Agent'),
        'is_dvla':fields.boolean('Is DVLA')
    }
    _default = {
        'state': lambda * a: 'none',
        'email_check':lambda *a:False,
        'user_id': lambda self, cr, uid, ctx : uid,
        'allocated_user_id': lambda self, cr, uid, ctx : uid,
        'enquiry_date': lambda * a: datetime.datetime.now(),
        'due_date': lambda * a: datetime.datetime.now(),
    }
    
    def onchange_allocated_user_id(self, cr, uid, ids, allocated_user_id, context={}):
        enquiries = self.browse(cr, uid, ids)
        result = {}
        if len(enquiries) > 0 :
            enquiry = enquiries[0] 
            result['allocated_user_group_id'] = ''
            if allocated_user_id:
                if enquiry.allocated_user_id.id != allocated_user_id:
                    result['dummy'] = 'allocated_user_id_changed'
                else:
                    result['dummy'] = ''
            else:
                result['dummy'] = 'allocated_open'
        else:
            result['allocated_user_group_id'] = ''
            if allocated_user_id:
                result['dummy'] = 'allocated_user_id_changed'
            else:
                result['dummy'] = 'allocate_open'
            
        return {'value': result}
    
    def onchange_allocated_user_group_id(self, cr, uid, ids, allocated_user_group_id, context={}):
        enquiries = self.browse(cr, uid, ids)
        result = {}
        if len(enquiries) > 0:
            enquiry = enquiries[0] 
            result['allocated_user_id'] = ''
            if allocated_user_group_id:
                if enquiry.allocated_user_group_id.id != allocated_user_group_id:
                    result['dummy'] = 'allocated_user_group_id_changed'
                else:
                    result['dummy'] = ''
            else:
                result['dummy'] = 'allocated_open'
        else:
            result['allocated_user_id'] = ''
            if allocated_user_group_id:
                result['dummy'] = 'allocated_user_group_id_changed'
            else:
                result['dummy'] = 'allocated_open'
            
        return {'value': result}

cmc_enquiry()
