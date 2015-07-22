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


class email_templates(osv.osv):
    _name = "cmc.email.templates"
    _description = "cmc.email.templates"
    _inherit = "ir.attachment"


    _columns = {
                
        'name': fields.selection([('New appointment letter to Client email','New appointment letter to Client (e-mail)'),
                                    ('New appointment letter to Client Agent paying email_quest','New appointment letter to Client Agent paying (e-mail)(Quest Received)'),
                                    ('New appointment letter to Client Agent paying email_not_quest','New appointment letter to Client Agent paying (e-mail)(Quest Not Received)'),
                                    ('New appointment letter to Referring Agent email','New appointment letter to Referring Agent (e-mail)'),
                                    ('Re-booked appointment after a cancellation letter to Client email','Re-booked appointment after a cancellation letter to Client (e-mail)'),
                                    ('Notification to DVLA of new appointment email','Notification to DVLA of new appointment (e-mail)'),
                                    ('Notification to DVLA of re-booked appointment following cancellation email','Notification to DVLA of re-booked appointment following cancellation (e-mail)'),
                                    ('Information Pack Chase Up Letter To Client','Information Pack Chase Up Letter To Client'),
                                    ('Information Pack Chase Up Letter To Agent','Information Pack Chase Up Letter To Agent'),
                                    ('Covering Letter To Client','Covering Letter To Client'),
                                    ('Covering Letter To Agent','Covering Letter To Agent'),
                                    ('Assessment Client Form','Assessment Client Form'),
                                    ('Assessment Agent Form','Assessment Agent Form'),
                                    ('Appointment letter to Current User email','Appointment letter to Current User (email)'),
                                    ('Appointment letter to Current Owner email','Appointment letter to Current Owner (email)'),
                                    ('Appointment letter to Agent Dealership email','Appointment letter to Agent Dealership (email)'),
                                    ('CMC Leaflet','CMC Leaflet'),
                                    ('Information Sheet','Information Sheet'),
                                    ('MoMap Questionnaire','MoMap Questionnaire'),
                                    ('CMC Map','CMC Map'),
                                    ('Invoice to Agent','Invoice to Agent')],'Template Name', required=True),
        'datas_fname': fields.char('Filename', size=64),
        'datas': fields.binary('File')
         }
email_templates()

class sxw_templates(osv.osv):
    _name = "cmc.sxw.templates"
    _description = "cmc.sxw.templates"
    _inherit = "ir.attachment"
    _rec_name='type_name'
    
    _columns = {
        'type_name':fields.selection([
                ('full_driving_assessment', 'Full Driving Assessment'),
                ('wheelchair_assessment', 'Wheelchair Assessment'),
                ('drive_from_wheelchair_assessment', 'Drive from Wheelchair Assessment'),
                ('passenger_adult','Passenger Adult'),('passenger_child','Passenger Child'),
                ('car_seat_harness_assessment', 'Car Seat/Harness Assessment'),
                ('driving_legal_assessment', 'Driving Legal Assessment'),
                            ('drive_safer_for_longer_assessment', 'Drive Safer For Longer Assessment'),
                            ('driving_adaptation_assessment', 'Driving Adaptation Assessment'),
                            ('mo_map_adapdation_assessment', 'MO MAP Adaptation Assessment'),
                            ('review_assessment', 'Review Assessment'),
                            ('wheel_walker', 'Wheeled Walker'),
                            ('chair_assessment', 'Chair Assessment'),
                            ('bathing_assessment', 'Bathing Assessment'),
                            ('other_ilme_equipment_assessment', 'Other ILME Equipment Assessment'),
                            ('buggy_assessment', 'Buggy Assessment'),
                            ('scooter_assessment', 'Scooter Assessment'),
                            ('pct_wheelchair_buggy', 'PCT Wheelchair/Buggy'),
                            ('hoist_demo', 'Hoist Demo'),
                            ('momap_access', 'MO MAP Access'),
                            ('pressure_mapping_assessment' , 'Pressure Mapping Assessment'),
                ], 
                'Action Type', required=True),
        'datas_fname': fields.char('Filename', size=64),
        'datas': fields.binary('File'),
        'name':fields.char('Report',size=100)
        }
    _defaults={
    'name': lambda * a: 'Report',
    }
sxw_templates()


class cmc_attachments(osv.osv):
    _name="cmc.attachments"
    _description="cmc.attachments"
    _inherit = "ir.attachment"
    
    _columns={
        'name': fields.selection([
        ('Assessment Form', 'Assessment Form')],
        'Template Name', required=True),
        'datas_fname': fields.char('Filename',
                                   size=64),

        'datas': fields.binary('Data')
              
              
              }
cmc_attachments()