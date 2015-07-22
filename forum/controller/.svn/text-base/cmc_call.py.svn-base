from osv import fields, osv
from osv.orm import except_orm
from string import Template
from tools.misc import debug
from tools.translate import _
import tools
import datetime
import string
import pooler
import base64


class cmc_call_history(osv.osv):
    _name = "cmc.call.history"
    _rec_name = 'call_summary'
    _order = 'call_date_time desc'    

    #===========================================================================
    # this method may be called by wizard or direct form submission.
    # in case of wizard agent, client, inbound and outbound is known hence appropriate messages are saved.
    #===========================================================================
    def create(self, cr, uid, vals, context={}):
        debug("IN CALL HISTORY")
        person = None
        
        if vals['call_person_type'] == 'client':
            if not vals['client_id']:
                raise osv.except_osv('Client Not Specified!', 'Client calls must have an Client Selected!\n\nPlease select Client from the list\n')
            vals['person_id'] = vals['client_id'] 
            person = pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, vals['client_id'])
            pooler.get_pool(cr.dbname).get('cmc.person').write(cr, uid, [person.id], {'is_client':True}, context={'indirect':True})
        elif vals['call_person_type'] == 'agent':
            if not vals['agent_id']:
                raise osv.except_osv('Agent Not Specified!', 'Agent calls must have an Agent Selected!\n\nPlease select Agent from the list\n')
            vals['person_id'] = vals['agent_id']
            person = pooler.get_pool(cr.dbname).get('cmc.person').browse(cr, uid, vals['agent_id'])
            pooler.get_pool(cr.dbname).get('cmc.person').write(cr, uid, [person.id], {'is_agent':True}, context={'indirect':True})
             #==================================================================
             # if client is selected then make reverse entry into client record
             #==================================================================
            if vals['client_id']:
                 if vals['agent_id'] == vals['client_id']:
                    raise osv.except_osv('Agent & Client cannot be same!', 'Agent calls must have different client selected!\n\nPlease remove the client name or select another client from the list.')
                 pooler.get_pool(cr.dbname).get('cmc.person').write(cr, uid, [vals['client_id']], {'is_client':True}, context={'indirect':True})
                 check_q = """select * from cmc_client_agent_rel_id where agent_id = %d and client_id =%d
                             """ % (person.id, vals['client_id'])
                 cr.execute(check_q)
                 res = cr.fetchall()
                 if len(res) == 0:
                     query = """ insert into cmc_client_agent_rel_id(agent_id,client_id) values(%d,%d)
                      """ % (person.id, vals['client_id'])
                     cr.execute(query)
        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid)
        if vals['call_type'] == 'inbound':
            vals['from'] = person.display_name
            vals['to'] = user.name
        else:
            vals['from'] = user.name
            vals['to'] = person.display_name
        #is the call re-allocated?
        allocated_group = False
        allocated_user = False
        allocated_open = False
        activity = vals['call_type'] + ' call via ' + vals['call_channel'] + ' received'
        if vals['allocated_user_group_id']:
            allocated_group = True
            vals['allocated_user_id'] = None
        elif vals['allocated_user_id']:
            if vals['allocated_user_id'] != uid: 
                allocated_user = True
        else:
            allocated_open = True
        if 'state' in vals :
            if  vals['state'] != 'closed':
                    vals['state'] = 'allocated'
            else:
                    vals['state'] = 'closed'
        else:
            vals['state'] = 'allocated'

        seq_id = self.pool.get('ir.sequence').search(cr, uid, [('name', '=', 'CMC History')])[0]
        new_id = self.pool.get('ir.sequence').get_id(cr, uid, seq_id)
        vals['call_id'] = str(new_id)
        call_id = super(cmc_call_history, self).create(cr, uid, vals, context)
        debug(vals)
        if (allocated_group):
            allocated_user_group = pooler.get_pool(cr.dbname).get('res.groups').browse(cr, uid, vals['allocated_user_group_id'])
            pooler.get_pool(cr.dbname).get('cmc.call.comments').create(cr, uid, {
                     'date_time':datetime.datetime.now(),
                     'user_id': vals['user_id'],
                     'comments': 'Allocated to - ' + allocated_user_group.name + ' by ' + user.name ,
                     'call_id':call_id,
                     })
            activity = activity + ' and allocated to - ' + allocated_user_group.name + ' by ' + user.name
        elif (allocated_user):
            allocated_user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, vals['allocated_user_id'])
            pooler.get_pool(cr.dbname).get('cmc.call.comments').create(cr, uid, {
                     'date_time':datetime.datetime.now(),
                     'user_id': vals['user_id'],
                     'comments': 'Allocated to - ' + allocated_user.name + ' by ' + user.name ,
                     'call_id':call_id,
                     })
        elif (allocated_open):
            pooler.get_pool(cr.dbname).get('cmc.call.comments').create(cr, uid, {
                     'date_time':datetime.datetime.now(),
                     'user_id': vals['user_id'],
                     'comments': 'Allocated to All Users - by ' + user.name,
                     'call_id':call_id,
            })
        else:
            pooler.get_pool(cr.dbname).get('cmc.call.comments').create(cr, uid, {
                     'date_time':datetime.datetime.now(),
                     'user_id': uid,
                     'comments': 'Call logged - by ' + user.name,
                     'call_id':call_id,
            })
            activity = activity + ' by ' + user.name
        communication_id = pooler.get_pool(cr.dbname).get('cmc.communication').create(cr, uid, {
                     'date':datetime.datetime.now(),
                     'user_id': vals['user_id'],
                     'from': person.display_name,
                     'to':user.name,
                     'type':vals['call_channel'],
                     'subject':'New ' + vals['call_person_type'] + ' ' + vals['call_type'] + ' ' + vals['call_channel'] + ' - by ' + user.name,
                     'message':'Check',
                     'person_id':person.id,
                     'call_id':call_id,
                })
        if 'datas_fname' in vals and vals['datas_fname']:
            pooler.get_pool(cr.dbname).get('cmc.attachment').create(cr, uid, {
                     'date': datetime.datetime.now(),
                     'user_id': vals['user_id'],
                     'name': 'Attachment - ' + vals['datas_fname'],
                     'datas':vals['datas'],
                     'datas_fname':vals['datas_fname'],
                     'description':'This attachment was uploaded during the creation of the call by ' + user.name,
                     'person_id':person.id,
                     'communication_id':communication_id,
                     'call_id':call_id,
                     })
        if context.get('log',False):
            activity=context.get('log')+' '+user.name
        pooler.get_pool(cr.dbname).get('cmc.user.activity').create(cr, uid, {
                     'date':datetime.datetime.now(),
                     'user_id': uid,
                     'activity':activity,
                     'type':vals['call_channel'],
                     'client_id':vals['client_id'],
                     'agent_id':vals['agent_id'],
                     'call_id':call_id,
                    })
        debug("CALL CREATION AFTER CREATE")
        debug(vals)
        return call_id

    def write(self, cr, uid, ids, vals, context={}):
        debug("I AM CALL HISTORY WRITE MODE")
        debug(vals)
        if 'call_details' in vals:
            if not vals['call_details']:
                vals['call_details']=""
            id = None
            if type(ids).__name__ == 'list':
                id = ids[0]
            else:
                id = ids
            call = self.browse(cr, uid, id)
            if call.state == 'closed':
               return True
            user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid) 
            allocated_group = False
            allocated_user = False
            activity = ''
            if call.user_id.id != uid :
                    msg_added="\n\nCall Allocated By "+call.user_id.name
            else:
                    msg_added="" 
            if (vals['allocated_user_group_id'] != call.allocated_user_group_id.id):
                vals['allocated_user_id'] = None
                if (vals['allocated_user_group_id']):
                    allocated_user_group = pooler.get_pool(cr.dbname).get('res.groups').browse(cr, uid, vals['allocated_user_group_id'])
                    msg = 'Transferred to user group - ' + allocated_user_group.name + ' by ' + user.name + ' : \n\n' + call.call_details
                else:
                    msg = 'Call user group allocation removed by ' + user.name + ' : \n\n' + call.call_details
                pooler.get_pool(cr.dbname).get('cmc.call.comments').create(cr, uid, {
                         'date_time':datetime.datetime.now(),
                         'user_id': uid,
                         'comments': msg,
                         'call_id':call.id,
                         })
                activity = msg
            elif (vals['allocated_user_id'] != call.allocated_user_id.id):
                
                if (vals['allocated_user_id']):
                    allocated_user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, vals['allocated_user_id'])
                    msg = 'Transferred to user - ' + allocated_user.name + ' by ' + user.name + ' : \n\n' + vals['call_details']
                else:
                    msg = 'Call user allocation removed by ' + user.name + ' : \n\n' + vals['call_details']
                pooler.get_pool(cr.dbname).get('cmc.call.comments').create(cr, uid, {
                         'date_time':datetime.datetime.now(),
                         'user_id': uid,
                         'comments': msg+"\n "+msg_added,
                         'call_id':call.id,
                         })
                activity = msg    
            else:
                pooler.get_pool(cr.dbname).get('cmc.call.comments').create(cr, uid, {
                         'date_time':datetime.datetime.now(),
                         'user_id': uid,
                         'comments': user.name + ' : ' + vals['call_details'] +"\n "+msg_added,
                         'call_id':call.id,
                         })    
                activity = 'Call comment added by - ' + user.name
            
            pooler.get_pool(cr.dbname).get('cmc.user.activity').create(cr, uid, {
                 'date':datetime.datetime.now(),
                 'user_id': uid,
                 'activity':activity,
                 'type':'internal',
                 'client_id':call.client_id.id,
                 'agent_id':call.agent_id.id,
                 'call_id':call.id,
                })
    #            vals['comments'] = ''
            vals['dummy'] = ''
            
        return super(cmc_call_history, self).write(cr, uid, ids, vals, context=context)
    
    def onchange_allocated_user_id(self, cr, uid, ids, allocated_user_id, context={}):
        calls = self.browse(cr, uid, ids)
        result = {}
        if len(calls) > 0 :
            call = calls[0] 
            result['allocated_user_group_id'] = ''
            if allocated_user_id:
                if call.allocated_user_id.id != allocated_user_id:
                    result['dummy'] = 'allocated_user_id_changed'
                else:
                    result['dummy'] = ''
            else:
                result['dummy'] = 'allocated_open'
        return {'value': result}
    
    def onchange_allocated_user_group_id(self, cr, uid, ids, allocated_user_group_id, context={}):
        calls = self.browse(cr, uid, ids)
        result = {}
        if len(calls) > 0:
            call = calls[0] 
            result['allocated_user_id'] = ''
            if allocated_user_group_id:
                if call.allocated_user_group_id.id != allocated_user_group_id:
                    result['dummy'] = 'allocated_user_group_id_changed'
                else:
                    result['dummy'] = ''
            else:
                result['dummy'] = 'allocated_open'
        return {'value': result}

    def btn_call_complete(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'closed'}, context=context)
        return  {
            'domain': "[('allocated_user_id','=',%d), ('state', '=', 'allocated')]" % (uid),
            'name': 'Calls Allocated to Me',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cmc.call.history',
            'view_id': view_res,
            'type': 'ir.actions.act_window',
            'context': {'user_id':uid}
            }

    _columns = {
        'call_id':fields.char('Call Id', size=64),
        'call_date_time': fields.datetime('Call Time', size=64),
        'user_id':fields.many2one('res.users', 'Created By'),
        'call_channel': fields.selection([
              ('Telephone', 'Telephone'),
              ('Email', 'Email'),
              ('Fax', 'Fax'),
              ('Letter', 'Letter'),
              ('In Person', 'In Person'),
              ('Other', 'Other')
              ], 'Channel', required=True),
        'call_type': fields.selection([
            ('inbound', 'Inbound'),
            ('outbound', 'Outbound')],
            'Type', required=True),
        'call_person_type': fields.selection([
            ('client', 'Client'),
            ('agent', 'Agent')],
            'Client/Agent', required=True),
        'from':fields.char('From', size=64),
        'to':fields.char('To', size=64),
        'call_summary': fields.char('Call Summary', size=64),
        'call_details': fields.text('Call Details'),
        'person_id':fields.many2one('cmc.person', 'Person Name'),
        'client_id':fields.many2one('cmc.person', 'Client'),
        'agent_id':fields.many2one('cmc.person', 'Agent'),
        'reference':fields.char('Client/Agent\'s Reference', size=255),
        'allocated_user_id':fields.many2one('res.users', 'Allocated To'),
        'allocated_user_group_id':fields.many2one('res.groups', 'Allocated To'),
        'comments': fields.text('Comments'),
        'comment_ids':fields.one2many('cmc.call.comments', 'call_id', ''),
        'activity_ids':fields.one2many('cmc.user.activity', 'call_id', 'User Actions'),
        'history_assessment_ids':fields.one2many('cmc.assessment', 'call_id', ''),
        'communication_ids': fields.one2many('cmc.communication', 'call_id', 'Communication'),
        'attachment_ids': fields.one2many('cmc.attachment', 'call_id', 'Call Attachments'),
        'enquiry_ids': fields.one2many('cmc.enquiry', 'call_id', 'Actions and Requests during the Call'),
        'datas': fields.binary('Attached File'),
        'datas_fname':fields.char('File Name', size=255),
        'state': fields.selection([
            ('none', 'None'),
            ('allocated', 'Allocated'),
            ('closed', 'Closed')],
            'Status', required=True),
        'dummy': fields.char('Dummy', size=64),
        'call_reason':fields.selection([('all_assessment', 'All Assessments'),
                                        ('driving_tution', 'Driving Tution'),
                                    ('Driving Ax','Driving Ax'),
                                    ('Passenger Ax','Passenger Ax'),
                                    ('Drive from wheelchair Ax','Drive from wheelchair Ax'),
                                    ('Wheelchair Scooter Ax','Wheelchair/Scooter Ax'),
                                    ('Childrens Service','Childrens Service'),
                                    ('Motorbike Ax','Motorbike Ax'),
                                ('all_other_enquiries', 'All Other Enquiries'),
                                ('forum_calls','Forum Calls'),
                                ('Imported Data','Imported Data')], 'Reason'),
        'calling_about':fields.char('Calling About',size=255)
       }
    _default = {
        'state': lambda * a : 'none',
        'user_id': lambda self, cr, uid, ctx : uid,
        'call_date_time':lambda * a : datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
        
cmc_call_history()

class cmc_call_comments(osv.osv):
    _name = "cmc.call.comments"
    _rec_name = 'comments'
    _order = "date_time desc"
    def create(self, cr, uid, vals, context={}):
        return super(cmc_call_comments, self).create(cr, uid, vals, context)
    
    _columns = {
        'call_id':fields.many2one('cmc.call.history', 'Call'),
        'comments': fields.text('Comments', size=255),
        'date_time': fields.datetime('Date'),
        'user_id': fields.many2one('res.users', 'User'),
       }
cmc_call_comments()