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


class cmc_person(osv.osv):
    _name = "cmc.person"
    _description = "cmc.person"
    _rec_name = 'display_name'
    
    def btn_save(self, cr, uid, ids, context):
        return
    
    def write(self, cr, uid, ids, vals, context=None):
        debug('<<<WRITE MODE IN person OBJECT>>')
        person = self.browse(cr, uid, ids[0])
        activity = []
        #if person.is_deceased:
           # raise except_orm('Warning','This person has been marked as deceased ensure you are in the correct record')
        if 'display_name' in vals and not vals['display_name']:
            if vals['first_name'] and vals['last_name']:
                vals['display_name'] = (vals['first_name']) + ' ' + (vals['last_name'])
            else:
                vals['display_name'] = vals['organisation_name'] if vals['organisation_name'] else False
        if 'indirect' not in context or person.address_line_1 and 'address_line_1' in vals:
            if 'address_line_1' in vals:
                if vals['address_line_1'] and not vals['postcode']:
                        raise except_orm('Warning','Please Enter Postcode')
            address_changed = False
            if person.address_type == 'home' and not person.address_line_1 and not person.address_line_2 and not person.city and not person.county: 
                    address_changed = False
            else:
                if 'address_type' in vals:
                    if person.address_type != vals['address_type']:
                        address_changed = True
                    elif (person.address_line_1 != vals['address_line_1'] and person.address_line_1 is not None):
                        address_changed = True
                    elif (person.address_line_2 != vals['address_line_2'] and person.address_line_2 is not None):
                        address_changed = True
                    elif (person.city != vals['city'] and person.city is not None):
                        address_changed = True
                    elif (person.county != vals['county'] and person.county is not None):
                        address_changed = True
                    elif (person.postcode != vals['postcode'] and person.postcode is not None):
                        address_changed = True
            if address_changed:
                address_table = pooler.get_pool(cr.dbname).get('cmc.person.address')
                address_table.create(cr, uid, {
                                   'address_type':'previous',
                                   'address_line_1': person.address_line_1,
                                   'address_line_2': person.address_line_2,
                                   'city':person.city,
                                   'county':person.county,
                                   'postcode': person.postcode,
                                   'person_id': ids[0]})
                activity.append('Address Changed')
            
            telephone_changed = False
            if person.telephone_type  == 'home' and not person.extension and not person.telephone_description and not person.telephone: 
                    telephone_changed = False
            else:
				if 'telephone' in vals:
					if (person.telephone != vals['telephone'] and person.telephone is not None):
						telephone_changed = True
					elif (person.extension != vals['extension'] and person.extension is not None):
						telephone_changed = True
					elif (person.telephone_description != vals['telephone_description']):
						telephone_changed = True
					elif person.telephone_type != vals['telephone_type'] :
						telephone_changed = True
            if telephone_changed:
                telephone_table = pooler.get_pool(cr.dbname).get('cmc.person.telephone')
                telephone_table.create(cr, uid, {
                                   'telephone_type':'previous',
                                   'telephone': person.telephone,
                                   'extension': person.extension,
                                   'description':person.telephone_description,
                                   'person_id': ids[0]})
                activity.append('Telephone Changed')
            email_changed = False
            if person.email_type =='home' and not person.email_address and not person.email_description:
                email_changed = False
            else:
				if 'email_address' in vals:
					if (person.email_address != vals['email_address'] and person.email_address is not None):
						email_changed = True
					elif person.email_type != vals['email_type']:
						email_changed = True
            if email_changed:
                debug("<<EMAIL CHANGED>>")
                email_table = pooler.get_pool(cr.dbname).get('cmc.person.email')
                email_table.create(cr, uid, {
                                   'email_type':'previous',
                                   'email_address': person.email_address,
                                   'person_id': ids[0]})
                activity.append('Email Address Changed')

        return super(cmc_person, self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context={}):
        self.validate(vals)
        seq_id = self.pool.get('ir.sequence').search(cr, uid, [('name',
                                                                '=',
                                                                'CMC Person')])[0]
        new_id = self.pool.get('ir.sequence').get_id(cr,
                                                     uid,
                                                     seq_id)
        if vals['is_organisation']:
            vals['is_agent'] = True
            if vals['organisation_name']==tools.config.options['organisation_name']:
                vals['is_dvla']=True
        vals['person_id'] = str(new_id)
        vals['state'] = 'created'
        if not vals['display_name']:
            if vals['first_name'] and vals['last_name']:
                vals['display_name'] = (vals['first_name']) + ' ' + (vals['last_name'])
            elif vals['is_organisation']:
                vals['display_name'] = vals['organisation_name'] if vals['organisation_name'] else False
        address_line_1 = vals['address_line_1']
        address_line_2 = vals['address_line_2']
        city = vals['city']
        county = vals['county']
        postcode = vals['postcode']
        if address_line_1 and not postcode:
            raise except_orm('Warning','Please Enter Postcode')
        address_type = vals['address_type'] 
        telephone_type = vals['telephone_type'] 
        telephone = vals['telephone']
        extension = vals['extension']
        telephone_description = vals['telephone_description'] 
        email_type = vals['email_type'] 
        email_address = vals['email_address']
        id = super(cmc_person, self).create(cr, uid, vals, context)
        activity_table = pooler.get_pool(cr.dbname).get('cmc.user.activity')
        if not vals['is_organisation']:
            activity_table.create(cr, uid, {
                               'date': datetime.datetime.now(),
                               'user_id': uid,
                               'type': 'Person Record',
                               'activity':'New Person Created',
                               'person_id':int(id)})
        else:
            activity_table.create(cr, uid, {
                               'date': datetime.datetime.now(),
                               'user_id': uid,
                               'type': 'Organisation Record',
                               'activity':'New Organisation Created',
                               'person_id':id})
            debug(vals)
        return id
    
    def btn_add_new_address(self, cr, uid, ids, context):
        person = self.browse(cr, uid, ids[0])
        debug('Address I have come here')
        if person.address_line_1 or person.address_line_2 or person.city :
            address_table = pooler.get_pool(cr.dbname).get('cmc.person.address')
            address_table.create(cr, uid, {
                                           'address_line_1': person.address_line_1,
                                           'address_line_2': person.address_line_2,
                                           'city':person.city,
                                           'county':person.county,
                                           'postcode': person.postcode,
                                           'person_id': ids[0]})
            pooler.get_pool(cr.dbname).get('cmc.user.activity').create(cr, uid, {
                                   'date': datetime.datetime.now(),
                                   'user_id': uid,
                                   'type': 'Address Changed',
                                   'activity':'Previous Address Added to Directory',
                                   'person_id':ids[0]})
        return 
    
    def btn_add_new_email(self, cr, uid, ids, context):
        person = self.browse(cr, uid, ids[0])
        debug('I have come here')
        if person.email_address or person.email_description:
            debug('I have come here')
            email_table = pooler.get_pool(cr.dbname).get('cmc.person.email')
            email_table.create(cr, uid, {
                                           'email_address': person.email_address,
                                           'email_description': person.email_description,
                                           'person_id': ids[0]})
            pooler.get_pool(cr.dbname).get('cmc.user.activity').create(cr, uid, {
                                   'date': datetime.datetime.now(),
                                   'user_id': uid,
                                   'type': 'Email Changed',
                                   'activity':'Previous Email Added to Directory',
                                   'person_id':ids[0]})
        return 
    
    def btn_add_new_telephone(self, cr, uid, ids, context):
        person = self.browse(cr, uid, ids[0])
        telephone_table = pooler.get_pool(cr.dbname).get('cmc.person.telephone')
        telephone_table.create(cr, uid, {
                                           'telephone': person.telephone,
                                           'extension': person.extension,
                                           'description': person.telephone_description,
                                           'person_id': ids[0]})
        pooler.get_pool(cr.dbname).get('cmc.user.activity').create(cr, uid, {
                                   'date': datetime.datetime.now(),
                                   'user_id': uid,
                                   'type': 'Telephone Changed',
                                   'activity':'Previous Telephone Added to Directory',
                                   'person_id':ids[0]})
        return 
    
    def validate(self, vals):
        #=======================================================================
        # Validation of Organisation and Person details
        #=======================================================================
        valid = []
        if vals['is_organisation'] and not vals['organisation_name']:
            raise except_orm('_Information is missing!', 'Please provide Organisation Name')
        elif not vals['is_organisation']:
            if not vals['title'] or (vals['title'] == 'other' and not vals['title_other']) or (vals['title'].strip()==""):
                    valid.append('Title or Other Title')
            if not vals['first_name'] or (vals['first_name'].strip()==""):
                valid.append('First Name')
            if not vals['last_name'] or (vals['last_name'].strip()==""):
                valid.append('Last Name')
            error = ''
            if valid is not None and len(valid) > 0:
                error = '\n\t'.join(valid)
                raise osv.except_osv('_Information is missing!', 'Please provide valid \n\t' + error)
                debug(error)
        return 

    def _get_display_name(self, first_name, last_name):
        return 

    def onchange_field_change(self, cr, uid, ids, name, last_name=''):
        values = {}
        values['value'] = {}
        values['value']['display_name'] = (name if name else '') + ' ' + (last_name if last_name else '')
        return values

    def onchange_show_display_name(self, cr, uid, ids, is_org, org_name, name, last_name=''):
        values = {}
        values['value'] = {}
        values['value']['display_name'] = (org_name if org_name else '') if is_org else ((name if name else '') + ' ' + (last_name if last_name else ''))
        return values
    
    def _get_call_ids(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for id in ids:
            cr.execute('SELECT c.id '\
                   'FROM cmc_call_history c '\
                   'WHERE c.client_id=%s '\
                   'OR c.agent_id=%s',
                   (id, id))
            calls = cr.fetchall()
            if not calls:
                res[id] = []
                continue
            else: 
                res[id] = [x for x in calls]
        return res

    def _get_activity_ids(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for id in ids:
            cr.execute('SELECT a.id '\
                   'FROM cmc_user_activity a '\
                   'WHERE a.client_id=%s '\
                   'OR a.agent_id=%s'  \
                   'OR a.person_id=%s',
                   (id, id, id))
            calls = cr.fetchall()
            if not calls:
                res[id] = []
                continue
            else: 
                res[id] = [x for x in calls]
        return res

    def _get_enquiry_ids(self, cr, uid, ids, field_name, arg, context={}):
        debug('Check I am here')
        res = {}
        for id in ids:
            cr.execute('SELECT e.id FROM cmc_enquiry e WHERE e.client_id=%s OR e.agent_id=%s',
                   (str(id), str(id)))
            calls = cr.fetchall()
            if not calls:
                res[id] = []
                continue
            else: 
                res[id] = [x[0] for x in calls]
        debug(res)
        return res
    
    def _get_assessment_ids(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for id in ids:
            cr.execute('SELECT a.id FROM cmc_assessment a WHERE a.client_person_id=%s OR a.agent_person_id=%s',
                   (str(id), str(id)))
            calls = cr.fetchall()
            if not calls:
                res[id] = []
                continue
            else: 
                res[id] = [x[0] for x in calls]
        return res

    _columns = {
        'person_id':fields.char('Reference Number',
                            size=255, readonly=True),
        'title':fields.selection([
            ('mr', 'Mr'),
            ('ms', 'Miss'),
            ('Ms','Ms'),
            ('mrs', 'Mrs'),
            ('dr', 'Dr'),
            ('Master','Master'),
            ('other', 'Other')],
            'Title'),
        'eligible':fields.selection([('Yes','Yes'),
                                     ('No','No')],'Eligible for VAT exemption'),
        'alert':fields.text('ALERTS'),
        'allergies':fields.text('Allergies'),
        'title_other':fields.char('Other Title', size=255),
        'first_name':fields.char('First Name', size=255),
        'last_name':fields.char('Last Name', size=255),
        'suffix':fields.char('Suffix', size=255),
        'display_name':fields.char('Display Name', size=255,help="The Name of the User must be Unique"),
        'gender': fields.selection([
            ('male', 'Male'),
            ('female', 'Female')],
            'Gender'),
        'birth_date':fields.date('Date of Birth'),
        'nhs_number':fields.char(' NHS Number', size=255),
        'driver_number':fields.char('Driver Number', size=255),
        'ethnicity':fields.selection([('Asian Bangladeshi','Asian Bangladeshi'),
                                      ('Asian Indian','Asian Indian'),
                                      ('Asian Pakistani','Asian Pakistani'),
                                      ('Black African','Black African'),
                                      ('Black Caribbean','Black Caribbean'),
                                      ('Black Other','Black Other'),
                                      ('Chinese','Chinese'),
                                      ('Declined to comment Not Stated','Declined to comment/Not Stated'),
                                      ('Ethnic Other','Ethnic Other'),
                                      ('Mixed Other','Mixed Other'),
                                      ('Mixed White + Asian','Mixed White + Asian'),
                                      ('Mixed White + Black African','Mixed White + Black African'),
                                      ('Mixed White + Black Caribbean','Mixed White + Black Caribbean'),
                                      ('Not specified','Not specified'),
                                      ('White British','White British'),
                                      ('White Irish','White Irish'),
                                      ('White Other','White Other')],'Ethnicity', size=255),
        'is_client':fields.boolean('Client'),
        'file_reference_number':fields.char('File Reference Number',size=100),
        'is_agent':fields.boolean('Agent'),
        'address_type':fields.selection([('home', 'Home'),
                                         ('work', 'Work'),
                                         ], 'Type', required=True),
        'address_line_1':fields.char('Address Line 1', size=255),
        'address_line_2':fields.char('Address Line 2', size=255),
        'city':fields.char(' City', size=255),
        'county':fields.char(' County', size=255),
        'postcode':fields.char('PostCode', size=255),
        'address_ids':fields.one2many('cmc.person.address', 'person_id', ''),
        'email_type':fields.selection([('home', 'Home'),
                                         ('work', 'Work'),
                                         ], 'Type', required=True),
        'email_address':fields.char('Email', size=255),
        'email_description':fields.char('Email Description', size=255),
        'email_address_ids':fields.one2many('cmc.person.email', 'person_id', ''),
        'telephone_type':fields.selection([('home', 'Home'),
                                         ('work', 'Work'),
                                         ('mobile','Mobile'),
                                         ], 'Type', required=True),
        'telephone':fields.char('Default Telephone', size=255),
        'extension':fields.char('Extension', size=255),
        'telephone_description':fields.char(' Description', size=255),
        'telephone_ids':fields.one2many('cmc.person.telephone', 'person_id', ''),
        'call_history_ids': fields.function(_get_call_ids, method=True, type='many2many', relation="cmc.call.history", string="Client/Agent Calls"),
        'assessment_ids':fields.function(_get_assessment_ids, method=True, type='many2many', relation="cmc.assessment", string="Assessments"),
        'assessment_id':fields.one2many('cmc.assessment', 'person_id', ''),
        'assessment_client_id':fields.one2many('cmc.assessment', 'client_person_id', ''),
        'assessment_agent_id':fields.one2many('cmc.assessment', 'agent_person_id', ''),
        'agent_ids':fields.many2many('cmc.person', 'cmc_client_agent_rel_id', 'client_id', 'agent_id', ''),
        'client_ids':fields.many2many('cmc.person', 'cmc_client_agent_rel_id', 'agent_id', 'client_id', ''),
        'communication_ids':fields.one2many('cmc.communication', 'person_id', 'Communication'),
        'activity_ids': fields.function(_get_activity_ids, method=True, type='many2many', relation="cmc.user.activity", string="User Actions"),
        'client_enquiry_id':fields.one2many('cmc.enquiry', 'client_id', 'Person'),
        'agent_enquiry_id':fields.one2many('cmc.enquiry', 'agent_id', 'Person'),
        'enquiry_ids':fields.one2many('cmc.enquiry', 'person_id', 'Person'),
        'state': fields.selection([
            ('none', 'None'),
            ('created', 'Created'),
            ('cancel','Cancel')],
             'State', required=True),
        'is_organisation':fields.boolean('Is It An Organisation'),
        'organisation_name':fields.char('Organisation Name', size=255),
        'is_deceased':fields.boolean('Deceased'),
        'communication_assessment_id':fields.one2many('cmc.assessment.communication', 'client_name', ''),
        'is_dvla':fields.boolean('DVLA'),
        'cmc_user_equipment':fields.one2many('cmc.equipment','current_user_id','Equipment'),
        'cmc_owner_equipment':fields.one2many('cmc.equipment','owner','Equipment'),
        'cmc_user_workshop':fields.one2many('cmc.workshop.process','current_user_id','Workshop'),
        'cmc_equipment_suply':fields.one2many('cmc.equipement.supply.process','client_id','Equipment Supply Process'),
        'gp_doctor_name':fields.char('Doctor\'s Name',size=100),
        'gp_surgery_name':fields.char('Surgery Name',size=100),
        'gp_address_line_1':fields.char('Address Line 1',size=100),
        'gp_address_line_2':fields.char('Address Line 2',size=100),
        'gp_city':fields.char('City',size=100),
        'gp_county':fields.char('County',size=100),
        'gp_postcode':fields.char('Postcode',size=100),
        'gp_telephone':fields.char('Telephone',size=100),
        'gp_consent_contact':fields.boolean('Consent given to contact GP'),
        'gp_consent_assessment':fields.boolean('Consent given to Send Assessment report/letters to GP'),
        'kin_contact_name':fields.char('Contact Name',size=100),
        'kin_telephone':fields.char('Telephone',size=100),
        'kin_relationship':fields.char('Relationship',size=100),
        'cmc_account_reference':fields.char('EAD Account Reference',size=100),
        'attachment_id':fields.one2many('person.attachments','person_id','Attachments'),
		'client_not_wish':fields.boolean('Client does not wish to receive copies of reports/correspondence'),
        'filter_user_id':fields.char('Filter User ID',size=100)
}

        
cmc_person()