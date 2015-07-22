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
# This is table of worksop process 
#===============================================================================
class cmc_workshop_process(osv.osv):
    _name = 'cmc.workshop.process'
    _description = 'cmc.workshop.process'
    _rec_name = 'job_no'
    
    
    def create(self, cr, uid, vals, context):
        debug(context)
        if 'state' in vals:
            if vals['job_type'] == 'Adaptations':
                seq_id = self.pool.get('ir.sequence').search(cr, uid, [('name', '=', 'CMC Adaptation Workshop')])[0]
            else:
                seq_id = self.pool.get('ir.sequence').search(cr, uid, [('name', '=', 'CMC Workshop')])[0]
            new_id = self.pool.get('ir.sequence').get_id(cr, uid, seq_id)
            vals['job_no'] = str(new_id)
        debug(vals)
        if 'paying_adaptation_repair' in vals:
            if vals['paying_adaptation_repair'] == 'other' and not vals['other_person_id']:
                raise except_orm('Warning', 'Please Select User for others to payment')
                
        id = super(cmc_workshop_process, self).create(cr, uid, vals, context)
        pooler.get_pool(cr.dbname).get('cmc.workshop.task.history').create(cr, uid, {
                                                                        'date_task':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                                        'title':'Task Created',
                                                                        'description':'Workshop Task has Been Created',
                                                                        'workshop_id':id    
                                                                                       })
        return id
    def title(self, title):
        t = {
            'dr': 'Dr',
            'mr':'Mr',
            'ms':'Miss',
            'Ms':'Ms',
            'mrs':'Mrs',
            'other':'Other'
            }
        return t.get(title, False)
    def _get_default_detail(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        debug("INTO WORKSHOP TASK")
        debug(ids)
        debug(field_name)
        debug(arg)
        debug(context)
        if len(ids) > 0 :
            for id in ids:
                prev_record = self.browse(cr, uid, id)
                equipment_record = prev_record.equipment_id
                debug(equipment_record)
                if equipment_record.make: 
                        result[id]= {
                                'make':equipment_record.make,
                                'model':equipment_record.model,
                                'serial_no':equipment_record.serial_no,
                                'size':equipment_record.size,
                                'manufacture_date':(datetime.datetime.strptime(equipment_record.manufacture_date,"%Y-%m-%d")).strftime("%d-%m-%Y") if equipment_record.manufacture_date else False,
                                'asset_type':equipment_record.asset_type if equipment_record.asset_type!='Other' else equipment_record.other_asset,
                                'owner':equipment_record.owner.id,
                                'onwer_asset_no':equipment_record.onwer_asset_no,
                                'current_user_id':equipment_record.current_user_id.id,
                                'year':equipment_record.year,
                            }
                else:
                        result[id] = {}
                debug(result)
        return result
    def btn_email_appointments(self, cr, uid, ids, context={}):
        
        title = display_name = address_line1 = address_line2 = curr_date = person_id = last_name = type = message = client_id = start_date = date_time = location = ""
        client_display_name = driver_number = date_of_birth = case_reference_no = date_assessment = ""
        client_name = client_address = ""
        client_add = ""
        appointment_letter = context.get('email_appointment_letter', False)
        if appointment_letter :
            prev_record = self.browse(cr, uid, ids[0])
            communication_message = ""
            debug(appointment_letter)
            apmt_temp_ids = pooler.get_pool(cr.dbname).get('cmc.email.templates').search(cr, uid, [("name", "=", appointment_letter)])
            debug(apmt_temp_ids)
            if len(apmt_temp_ids) == 0:
                raise except_orm('Template missing', 'Please upload valid templates.')
            cr.execute("select * from cmc_appointments where state='confirmed' and workshop_id=%d order by apmnt_start_date_time desc" % (prev_record.id))
            appt_ids = cr.fetchone()
            if appt_ids is None:
                raise except_orm('Warning', 'Please Confirm an Active Appointments')
            appt_record = pooler.get_pool(cr.dbname).get('cmc.appointments').browse(cr, uid, appt_ids[0])
            debug(appt_record)
            start_date_time = appt_record.apmnt_start_date_time.split(" ")
            start_date = datetime.datetime.strptime(start_date_time[0], '%Y-%m-%d').strftime('%d-%B-%Y')
            date_start = start_date if appt_record else ""
            date_time = start_date_time[1] if appt_record else ""
            location = appt_record.location if appt_record.location else ""
            apmt_temp_browse = pooler.get_pool(cr.dbname).get('cmc.email.templates').browse(cr, uid, apmt_temp_ids[0])
            template_string = base64.decodestring(apmt_temp_browse.datas)
            person_id_id = False
            type = 'client'
            communication_message = """Appointment Date:""" + start_date + "\n" + "Time:" + date_time + "\n" + "Location:" + location
            if appointment_letter == 'Appointment letter to Current User email':
                person_id_id = prev_record.current_user_id
                email_address = prev_record.current_user_id.email_address
                
                message = """
                    Please let me know as soon as possible if this date will be convenient for you.<br />
<br />
We may need to change your appointment date at short notice if we have ordered parts and they do not arrive in time for your appointment.  If we need to change your appointment date we will let you know as soon as possible.<br />
                    """
                communication_message += """
                 Please let me know as soon as possible if this date will be convenient for you.<br />
<br />
We may need to change your appointment date at short notice if we have ordered parts and they do not arrive in time for your appointment.  If we need to change your appointment date we will let you know as soon as possible.<br />"""
                
            elif appointment_letter == 'Appointment letter to Current Owner email':
                person_id_id = prev_record.owner
                owner = prev_record.owner.display_name
#                agent_name = agent_id
                email_address = prev_record.owner.email_address
                message = """
                Please let me know as soon as possible if this date will be convenient for you.<br />
<br />
We may need to change your appointment date at short notice if we have ordered parts and they do not arrive in time for your appointment.  If we need to change your appointment date we will let you know as soon as possible.<br />
                """
                communication_message += """
                    Please let me know as soon as possible if this date will be convenient for you.
We may need to change your appointment date at short notice if we have ordered parts and they do not arrive in time for your appointment.  If we need to change your appointment date we will let you know as soon as possible. """
            elif appointment_letter == 'Appointment letter to Agent Dealership email':
                person_id_id = prev_record.agent_id
                client_name = prev_record.current_user_id.display_name
                c_address = []
                if person_id_id.address_line_1:
                    c_address.append(person_id_id.address_line_1)
                if person_id_id.address_line_2:
                    c_address.append(person_id_id.address_line_2)
                if person_id_id.city:
                    c_address.append(person_id_id.city)
                if person_id_id.county:
                    c_address.append(person_id_id.county)
                if len(c_address) > 0 :
                    client_add = ','.join(c_address)
                else:
                    client_add = "" 
                client_address = client_add
                email_address = prev_record.agent_id.email_address
                message = """
                Please let me know as soon as possible if this date will be convenient for you.
                """
                communication_message += """
                Please let me know as soon as possible if this date will be convenient for you.
                """
            debug(person_id_id)
            if person_id_id:  
                address_line1 = person_id_id.address_line_1 if person_id_id.address_line_1 else "" 
                address_line2 = person_id_id.address_line_2 if person_id_id.address_line_2 else ""
                address_line3 = (person_id_id.city if person_id_id.city else "") + (',' + (person_id_id.county) if person_id_id.county else "")
                display_name = person_id_id.display_name
                curr_date = datetime.datetime.now().strftime("%d %B %Y")
                person_id = person_id_id.person_id
                last_name = person_id_id.last_name
                title = self.title(person_id_id.title) if person_id_id.title != 'other' else person_id_id.title_other
            if template_string:
                template_string = unicode(template_string, errors='ignore')
                t = Template(template_string).substitute(title=title,
                                                             display_name=display_name,
                                                             address_line1=address_line1,
                                                             address_line2=address_line2,
                                                             address_line3=address_line3,
                                                             curr_date=curr_date,
                                                             person_id=person_id,
                                                             last_name=last_name,
                                                             message=message,
                                                             client_name=client_name,
                                                             client_address=client_address,
                                                             start_date=date_start,
                                                             date_time=date_time,
                                                             location=location,
                                                             date_of_birth=date_of_birth,
                                                             case_reference_no=case_reference_no,
                                                             date_assessment=date_assessment,
                                                             )
                tools.email_send(tools.config.options['email_from'],
                    [email_address],
                   'Appointment Letter',
                    t,
                    subtype='html_with_image'
                )
                pooler.get_pool(cr.dbname).get('cmc.workshop.task.history').create(cr, uid, {
                                                                        'date_task':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                                        'title':'Appointment',
                                                                        'description':'Appoinment Letter Posted',
                                                                        'workshop_id':prev_record.id   
                                                                                       })    
                    
        else:
            raise except_orm('Invalid Error', 'Please Select The Valid Option')
        return
        return 
    def write(self, cr, uid, ids, vals, context={}):
        debug(vals)
        prev_record = self.browse(cr, uid, ids[0])
        if 'state' in vals:
            if vals['state'] == 'Quote Approved' and prev_record.state != 'Quote Approved':
                if prev_record.job_type == 'Adaptations':
                    seq_id = self.pool.get('ir.sequence').search(cr, uid, [('name', '=', 'CMC Adaptation Workshop')])[0]
                elif prev_record.job_type == 'Workshop':
                    seq_id = self.pool.get('ir.sequence').search(cr, uid, [('name', '=', 'CMC Workshop')])[0]
                new_id = self.pool.get('ir.sequence').get_id(cr, uid, seq_id)
                vals['job_no'] = str(new_id)
            prev_record = self.browse(cr, uid, ids[0])
            debug(prev_record)
            debug(prev_record.state)
            if vals['review_date']:
                #===============================================================
                # Create Appointment With type Reminder
                #===============================================================
                cr.execute('SELECT name FROM res_users WHERE id=%s', (str(uid)))
                owner_name = cr.fetchone()
                apmnt_start_date_time = datetime.datetime.now().strftime("%Y-%m-%d")
                start_time_hour = datetime.datetime.now().strftime("%H:%M")
                apmnt_end_date_time = vals['review_date'].split(" ")[0]
                minutes = (int(start_time_hour.split(":")[1]) / 5) * 5
                debug(apmnt_end_date_time)
                pooler.get_pool(cr.dbname).get('cmc.appointments').create(cr, uid, {
                                                                                    
                     'title':(prev_record.owner.display_name) + '-' + (owner_name[0]) + '- Review',
                     'assessment_id':prev_record.id,
                     'type':'reminder',
                     'location':prev_record.where,
                     'apmnt_start_date':apmnt_start_date_time,
                     'apmnt_date_end':apmnt_end_date_time.split(" ")[0],
                     'start_time_hour':start_time_hour.split(":")[0],
                     'start_time_minutes':str(minutes),
                     'end_time_hour':"00",
                     'end_time_minutes':"00",
                     'state':'active',
                     'owner':uid
                    })
            if prev_record.state != vals['state']:
                #===============================================================
                # CREATE ENTRY INTO THE TASK HISTORY
                #===============================================================
                pooler.get_pool(cr.dbname).get('cmc.workshop.task.history').create(cr, uid, {
                                                                            'date_task':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                                            'title':'State Changed',
                                                                            'description':'State Changed from ' + prev_record.state + ' to ' + vals['state'],
                                                                            'workshop_id':prev_record.id    
                                                                                           })
        return super(cmc_workshop_process, self).write(cr, uid, ids, vals, context)
    _columns = {
        'make': fields.function(_get_default_detail, method=True, type='char', string='Make', multi="client_contact"),
        'model': fields.function(_get_default_detail, method=True, type='char', string='Model', multi="client_contact"),
        'serial_no': fields.function(_get_default_detail, method=True, type='char', string='Serial Number', multi="client_contact"),
        'size': fields.function(_get_default_detail, method=True, type='char', string='Size', multi="client_contact"),
        'manufacture_date': fields.function(_get_default_detail, method=True, type='char', string='Date Received', multi="client_contact"),
        'asset_type': fields.function(_get_default_detail, method=True, type='char', string='Asset Type', multi="client_contact"),
        'owner': fields.function(_get_default_detail, method=True, type='many2one', string='Owner', relation='cmc.person', multi="client_contact"),
        'onwer_asset_no': fields.function(_get_default_detail, method=True, type='char', string='Owner Asset Number', multi="client_contact"),
        'current_user_id': fields.function(_get_default_detail, method=True, type='many2one', relation='cmc.person', string='Current User', multi="client_contact"),
        'year':fields.function(_get_default_detail, method=True, type='char', string='Year', multi="client_contact"),
        'state':fields.selection([('New Proposal', 'New Proposal'),
                                  ('Quote Sent', 'Quote Sent'),
                                  ('Quote Approved', 'Quote Approved'),
                                  ('Awaiting Parts', 'Awaiting Parts'),
                                  ('Appointment Booked', 'Appointment(s) Booked'),
                                  ('Adaptation Repair in process', 'Adaptation Repair in process'),
                                  ('Awaiting Delivery Collection', 'Awaiting Delivery/Collection'),
                                  ('Ready For Invoicing', 'Ready For Invoicing'),
                                  ('Complete', 'Complete'),
                                  ('Cancel', 'Cancel')], 'Status', required=True),
        'job_no':fields.char('Job Number', size=255),
        'nature_job':fields.selection([('Repair', 'Repair'), ('Service', 'Service'), ('Modifications', 'Modifications'), ('PDI', 'PDI'), ('Refurb', 'Refurb')], 'What is the nature of the job/task?'),
        'paying_adaptation_repair':fields.selection([('Equipment Owner', 'Equipment Owner'), ('Equipment User', 'Equipment User'), ('Other', 'Other')], 'Who will be paying for the adaptation/repair?'),
        'invoice_adaptation':fields.char('Invoice this adaptation/repair to', size=100),
        'requirement':fields.text('Requirement'),
        'equipment_collect':fields.selection([('Yes', 'Yes'), ('No', 'No')], 'Does the equipment need to be collected?', required=True),
        'collect_from':fields.char('Where should the item be collected from?', size=100),
        'work_off_site':fields.boolean('Work should be carried out off-site'),
        'work_where':fields.char('Where should the work be carried out?', size=100),
        'equipment_return':fields.selection([('Yes', 'Yes'), ('No', 'No')], 'Does the equipment need to be returned?', required=True),
        'item_returned':fields.char('Where should the item be returned to?', size=100),
        'appointment_id':fields.one2many('cmc.appointments', 'workshop_id', ''),
        'attachments_id':fields.one2many('workshop.attachments', 'workshop_id', ''),
        'task_id':fields.one2many('cmc.workshop.task.history', 'workshop_id', ''),
        'equipment_id':fields.many2one('cmc.equipment', 'Equipment'),
        'part_ordered':fields.one2many('cmc.workshop.part.ordered', 'workshop_id', ''),
        'apadatation_quote':fields.selection([('Adaptation Quote Client Paying Dep Required', 'Adaptation Quote Client Paying Dep Required'),
                                              ('Adaptation Quote Client Paying Dep Not Required', 'Adaptation Quote Client Paying Dep Not Required'),
                                              ('Adaptation Quote Agent Paying Dep Required', 'Adaptation Quote Agent Paying Dep Required'),
                                              ('Adaptation Quote Agent Paying Dep Not Required', 'Adaptation Quote Agent Paying Dep Not Required')], 'Adaptation Quote'),
        'outcome':fields.text('Outcome'),
        'review_later_date':fields.selection([('6', '6 Months'),
                                              ('12', '12 Months'),
                                              ('18', '18 Months'),
                                              ('24', '24 Months')], 'Review at a later date'),
        'review_date':fields.date('Date'),
        'other_person_id':fields.many2many('cmc.person','workshop_cmc_other_person_paying','other_id','workshop_id','Person'),
        'job_type':fields.selection([('Workshop', 'Workshop'),
                                     ('Adaptations', 'Adaptations')], 'Job Type'),
        'agent_id':fields.many2one('cmc.person', 'Agent'),
        'delear_id':fields.many2one('cmc.person', 'Dealership'),
        'appointment_letters':fields.selection([('Appointment letter to Current User print', 'Appointment letter to Current User (print)'),
                                                ('Appointment letter to Current User email', 'Appointment letter to Current User (email)'),
                                                ('Appointment letter to Current Owner print', 'Appointment letter to Current Owner (print)'),
                                                ('Appointment letter to Current Owner email', 'Appointment letter to Current Owner (email)'),
                                                ('Appointment letter to Agent Dealership print', 'Appointment letter to Agent Dealership (print)'),
                                                ('Appointment letter to Agent Dealership email', 'Appointment letter to Agent Dealership (email)')], 'Appointment Letters', required=True),
        'collect_option':fields.selection([('Current User Address', 'Current User Address'),
                                           ('Owner Address', 'Owner Address'),
                                         ('Other Address', 'Other Address')], 'Collect From'),
        'work_option':fields.selection([('Current User Address', 'Current User Address'),
                                           ('Owner Address', 'Owner Address'),
                                         ('Other Address', 'Other Address')], 'Collect From'),
        'item_option':fields.selection([('Current User Address', 'Current User Address'),
                                           ('Owner Address', 'Owner Address'),
                                         ('Other Address', 'Other Address')], 'Collect From')
        
}
    def onchange_review_date(self, cr, uid, ids, time, context={}):
        values = {}
        values['value'] = {}
        time = int(time)
        debug(time)
        values['value']['review_date'] = (datetime.datetime.now() + datetime.timedelta(time * 365 / 12)).strftime("%Y-%m-%d")
        debug(values['value']['review_date'])
        return values
    
    def onchange_address(self, cr, uid, ids, collect_option,title, context={}):
        values = {}
        values['value'] = {}
        debug(ids)
        debug(collect_option)
        add=""
        prev_record=self.browse(cr,uid,ids[0])
        if collect_option == 'Current User Address':
            if prev_record.current_user_id:
                person_id=prev_record.current_user_id
                address=[]
                if person_id.address_line_1:
                    address.append(person_id.address_line_1)
                if person_id.address_line_2:
                    address.append(person_id.address_line_2)
                if person_id.city:
                    address.append(person_id.city)
                if person_id.county:
                    address.append(person_id.county)
                if len(address) >0 :
                    add=','.join(address)
                else:
                    add = ""
            else:
                add
           
        elif collect_option == 'Owner Address':
            if prev_record.owner:
                person_id=prev_record.owner
                address=[]
                if person_id.address_line_1:
                    address.append(person_id.address_line_1)
                if person_id.address_line_2:
                    address.append(person_id.address_line_2)
                if person_id.city:
                    address.append(person_id.city)
                if person_id.county:
                    address.append(person_id.county)
                if len(address) >0 :
                    add=','.join(address)
                else:
                    add = ""
            else:
                add
        else:
            add=""
        values['value'][title]=add
        debug(title)
        
        return values
cmc_workshop_process()

class cmc_workshop_task_history(osv.osv):
    _name = 'cmc.workshop.task.history'
    _description = 'cmc.workshop.task.history'
    _rec_name = 'title'
    
    _columns = {
    'date_task':fields.datetime('Date'),
    'title':fields.char('Title', size=100),
    'description':fields.text('Description'),
    'workshop_id':fields.many2one('cmc.workshop.process', 'Workshop')
    }
cmc_workshop_task_history()

class cmc_workshop_part_ordered(osv.osv):
    _name = 'cmc.workshop.part.ordered'
    _description = 'cmc.workshop.part.ordered'
    _rec_name = 'ordered_from'
    
    def create(self, cr, uid, vals, context):
        debug(vals)
        if 'workshop_id' in vals:
            pooler.get_pool(cr.dbname).get('cmc.workshop.task.history').create(cr, uid, {
                                                                        'date_task':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                                        'title':'Part Order',
                                                                        'description':'Part ' + str(vals['part_no'] if vals['part_no'] > 0  else "") + 'Has Been Ordered on ' + (vals['date_order'] if vals['date_order'] else ""),
                                                                        'workshop_id':vals['workshop_id']   
                                                                                       })
        return super(cmc_workshop_part_ordered, self).create(cr, uid, vals, context)
    _columns = {
    'date_order':fields.date('Order Date'),
    'part_no':fields.char('Part No', size=100),
    'quantity':fields.integer('Quantity'),
    'description':fields.text('Description'),
    'price':fields.float('Price'),
    'ordered_from':fields.many2one('cmc.person', 'Order From'),
    'workshop_id':fields.many2one('cmc.workshop.process', 'Workshop')
    }
cmc_workshop_part_ordered()
