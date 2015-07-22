# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenOffice Reports
#    Copyright (C) 2009 Pexego Sistemas Informáticos. All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""
OpenOffice Reports - Reporting Engine based on Relatorio and OpenOffice.
"""
__author__ = "Borja López Soilán (Pexego)"

from oo_template import OOTemplate, OOTemplateException
from operator import itemgetter
from os.path import splitext
from osv import fields, osv
from osv.orm import except_orm
from tools.translate import _
import base64
import datetime
import datetime
import netsvc
import os
import pooler
import report
import tempfile
from collections import OrderedDict


class OOReportException(Exception):
    """
    OpenERP report exception
    """
    def __init__(self, message):
        # pylint: disable-msg=W0231
        self.message = message
    def __str__(self):
        return self.message


class OOReport:
    """
    OpenOffice/Relatorio based report.
    """

    def log(self, message, level=netsvc.LOG_DEBUG):
        """
        Helper method used print debug messages
        """
        netsvc.Logger().notifyChannel('pxgo_openffice_reports', level, message)


    def __init__(self, name, cr, uid, ids, data, context):
        self.name = name
        self.cr = cr
        self.uid = uid
        self.ids = ids
        self.data = data
        self.model = self.data['model']
        self.context = context or {}
        self.dbname = self.cr.dbname
        self.pool = pooler.get_pool(self.cr.dbname)
        self.openoffice_port = '8100'
        self.autostart_openoffice = True


    def execute(self, output_format='pdf', report_file_name=None):
        """
        Generate the report.
        """

        def _base64_to_string(field_value):
            """
            Helper method to decode a binary field
            """
            return base64.decodestring(field_value)

        def _get_attachments():
            """
            Helper function that returns a function that
            gets the attachments for one object using the current database
            connection (cr) and user (uid).
            """
            def get_attachments_func(browse_object):
                """
                Returns the attachments for one browse_object
                """
                db, pool = pooler.get_db_and_pool(self.dbname)
                cr = db.cursor()
                att_facade = pool.get('ir.attachment')
                # pylint: disable-msg=W0212
                attachment_ids = att_facade.search(cr, self.uid, [
                        ('res_model', '=', browse_object._name),
                        ('res_id', '=', browse_object.id)
                    ])
                return att_facade.browse(cr, self.uid, attachment_ids)
            return get_attachments_func

        def _field_to_image(field_value, rotate=None):
            """
            Helper function that decodes and converts a binary field
            into a png image and returns a tuple like the ones Relatorio
            "image:" directive wants.
            """
            from PIL import Image
            data = base64.decodestring(field_value)
            dummy_fd, temp_file_name = tempfile.mkstemp(prefix='openerp_oor_f2i_')
            temp_file = open(temp_file_name, 'wb')
            try:
                temp_file.write(data)
            finally:
                temp_file.close()
            image = Image.open(temp_file_name)
            if rotate:
                image = image.rotate(rotate)
            image.save(temp_file_name, 'png')
            return (open(temp_file_name, 'rb'), 'image/png')


        def _chart_template_to_image(field=None, filename=None, source=None, filepath=None, source_format=None, encoding=None, context=None):
            """
            Method that can be referenced from the template to include
            charts as images.
            When called it will process the file as a chart template,
            generate a png image, and return the data plus the mime type.
            """
            # Field is a binary field with a base64 encoded file that we will
            # use as source if it is specified
            source = field and base64.decodestring(field) or source

            filepath = filepath or filename
            filename = None
            assert filepath

            #
            # Search for the file on the addons folder of OpenERP if the
            # filepath does not exist.
            #
            if not os.path.exists(filepath):
                search_paths = ['./bin/addons/%s' % filepath, './addons/%s' % filepath]
                for path in search_paths:
                    if os.path.exists(path):
                        filepath = path
                        break

            #
            # Genshi Base Template nor it's subclases
            # (NewTextTemplate and chart.Template)
            # seem to load the filepath/filename automatically;
            # so we will read the file here if needed.
            #
            if not source:
                file = open(filepath, 'rb')
                try:
                    source = file.read()
                finally:
                    file.close()

            #
            # Process the chart subreport file
            #
            self.log("Generating chart subreport...")
            from relatorio.templates.chart import Template
            chart_subreport_template = Template(source=source, encoding=encoding)
            data = chart_subreport_template #.generate(**context)
            self.log("...done, chart generated.")

            return (data, 'image/png')




        def _gettext(lang):
            """
            Helper function that returns a function to enable translation
            using the using the current database connection, and language.
            """
            def gettext(text):
                """
                Returns the translation of one string
                """
                cr = pooler.get_db(self.dbname).cursor()
                context = { 'lang': lang }
                return _(text)
            return gettext


        assert output_format

        #
        # Get the report path
        #
        if not report_file_name:
            reports = self.pool.get('ir.actions.report.xml')
            report_ids = reports.search(self.cr, self.uid, [('report_name', '=', self.name[7:])], context=self.context)
            report_file_name = reports.read(self.cr, self.uid, report_ids[0], ['report_rml'])['report_rml']
            path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
            report_file_name = os.path.join(path, report_file_name)
            
        #
        # Set the variables that the report must see
        #
        client_id = agent_id = client_name = agent_name_client_add = agent_add = ""
        context = self.context
        object = (self.pool.get(self.model).browse(self.cr, self.uid, self.ids, self.context))[0]
        context['objects'] = self.pool.get(self.model).browse(self.cr, self.uid, self.ids, self.context)
        context['ids'] = self.ids
        context['model'] = self.model
        self.log(object)
        if self.model == 'cmc.assessment' :
            #===================================================================
            # Person Information
            #===================================================================
            client_id = object.client_person_id 
            agent_id = object.agent_person_id 
            context.update(self.person_information(client_id, 'client')) #Client Information 
            context.update(self.person_information(agent_id, 'agent'))   #Agent Information
            #===================================================================
            # Appointment Information
            #===================================================================
            context.update(self.appointment_timing(self.ids, 'active', 'assessment'))
            context.update(self.appointment_timing(self.ids, 'complete', 'assessment'))
            self.log("Person Information")
            #===================================================================
            # Other Information
            #===================================================================
            context['diagnosis'] = object.diagnosis_code if object.diagnosis_code else ""
            context['assessment_name'] = self.driving_name(object.driving_assessment_type)
            context['height'] = object.height if object.height else ""
            context['weight'] = object.weight if object.weight else ""
            context['dvla_medical_advisor'] = object.dvla_medical_advisor if object.dvla_medical_advisor else ""
            context['invoice_no'] = object.invoice_no if object.invoice_no else ""
            context['total_cost'] = "%.2f " % (object.total_cost if object.total_cost else 0)
            context['amount_debit'] = "%.2f " % (object.amount_debit if object.amount_debit else 0)
            context['payment_date'] = datetime.datetime.strptime(object.payment_date, "%Y-%m-%d").strftime("%d-%B-%Y") if object.payment_date else "",
            context['card_type'] = object.card_type if object.card_type else ""
            context['driver_number'] = object.driver_number if object.driver_number else ""
            context['expires'] = datetime.datetime.strptime(object.license_expiry_date, "%Y-%m-%d").strftime("%d-%B-%Y") if object.license_expiry_date else "",
            context['assessment_details'] = object.enquiry_details if object.enquiry_details else ""
            context['referrer_type'] = self.referer_name((object.referrer_type))
            context['reference_no'] = object.agency_reference_id if object.agency_reference_id else ""
        
        elif self.model == 'cmc.person':
            context.update(self.person_information(self.ids[0], 'client'))
        elif self.model == 'cmc.workshop.process':
            #===================================================================
            # #Person and Equipment information in workshop
            #===================================================================
            self.log(object)
            context.update(self.equipment_information(object.equipment_id if object.equipment_id else False))
            context.update(self.person_information(object.agent_id, 'agent'))
            context.update(self.person_information(object.dealer_id, 'dealer'))
            #===================================================================
            # Appointment Information
            #===================================================================
            context.update(self.appointment_timing(self.ids, 'active', 'workshop'))
            context.update(self.appointment_timing(self.ids, 'complete', 'workshop'))
            context.update(self.appointment_timing(self.ids, 'confirmed', 'workshop'))
            #===================================================================
            # Parts Ordered
            #===================================================================
            context['part'] = (self.part_ordered_information(self.ids))
            #===================================================================
            # Other Information
            #===================================================================
            context['nature'] = object.nature_status
            context['state'] = object.state
            context['job_no'] = object.job_no if object.job_no else ""
            context['requirement'] = object.requirement if object.requirement else ""
            context['collect_from'] = object.collect_from if object.collect_from else ""
            context['work_where'] = object.work_where if object.work_where else ""
            context['item_returned'] = object.item_returned if object.item_returned else ""
            #===================================================================
            # Who is Paying
            #===================================================================
            
            if object.paying_adaptation_repair == 'Equipment Owner':
                context.update(self.person_information(object.equipment_id.owner, 'paying'))
            elif object.paying_adaptation_repair == 'Equipment User':
                context.update(self.person_information(object.equipment_id.current_user_id, 'paying'))
            elif object.paying_adaptation_repair == 'Other':
                context.update(self.person_information(object.other_person_id[0], 'paying'))
            else:
                context.update(person_information(False, 'paying'))
            
        elif self.model == 'cmc.equipement.supply.process':
            context.update(self.person_information(object.client_id, 'client'))
            context.update(self.appointment_timing(self.ids, 'active', 'equipment_supply'))
            context.update(self.appointment_timing(self.ids, 'complete', 'equipment_supply'))
            context['reserved_equipment'] = self.reserved_equipment_information(self.ids)
        elif (self.name == 'report.MOMAP Management Report'):
            #statistics report
            date_from = self.data['form']['date_from']
            date_to = self.data['form']['date_to']
            context.update({'momap_report_period': datetime.datetime.strftime(datetime.datetime.strptime(date_from, '%Y-%m-%d'), '%d/%m/%Y') + ' to ' +datetime.datetime.strftime(datetime.datetime.strptime(date_to, '%Y-%m-%d'), '%d/%m/%Y')})
            context.update(self.momap_management_statistics_report(date_from, date_to))
            
        elif (self.name == 'report.MOMAP Mobility Centre Report'):
            #mobility centre report
            self.log("-------------------------------------------------------------------------------------------------")
            self.log(self.name)
            date_from = self.data['form']['date_from']
            date_to = self.data['form']['date_to']
            mc_id = self.data['form']['mc_name']
            self.cr.execute("SELECT name as name FROM mobility_mobility_centre WHERE id = '" + str(mc_id) + "'")
            context.update({'momap_report_mc_name': self.cr.dictfetchone()['name']})
            context.update({'momap_report_period': datetime.datetime.strftime(datetime.datetime.strptime(date_from, '%Y-%m-%d'), '%d/%m/%Y') + ' to ' +datetime.datetime.strftime(datetime.datetime.strptime(date_to, '%Y-%m-%d'), '%d/%m/%Y')})
            context.update(self.momap_mobility_centre_report(date_from, date_to, mc_id))
            self.log('context :' + str(self.context))
            self.log("-------------------------------------------------------------------------------------------------")

            
        context['data'] = self.data
        self.log("CHECKING DATA IN REPORTS")
        #
        # Some aliases used on standard OpenERP reports
        #
        user = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, self.context)
        context['user'] = user
        context['company'] = user.company_id
        context['logo'] = user.company_id and user.company_id.logo
        context['lang'] = context.get('lang') or (user.company_id and user.company_id.partner_id and user.company_id.partner_id.lang)
        
        # TODO: add a translate helper like the one rml reports use,
        #
        # Add some helper function aliases
        #
        context['base64_to_string'] = context.get('base64_to_string') or _base64_to_string
        context['b2s'] = context.get('b2s') or _base64_to_string
        context['get_attachments'] = context.get('get_attachments') or _get_attachments()
        context['field_to_image'] = context.get('field_to_image') or _field_to_image
        context['f2i'] = context.get('f2i') or _field_to_image
        context['chart_template_to_image'] = context.get('chart_template_to_image') or _chart_template_to_image
        context['chart'] = context.get('chart') or _chart_template_to_image
        context['gettext'] = context.get('gettext') or _gettext(context.get('lang'))
        context['_'] = context.get('_') or _gettext(context.get('lang'))
		
		# - print assessment paper work 
        context['time'] = datetime.datetime.now().strftime("%d %B %Y")
        #
        # Process the template using the OpenOffice/Relatorio engine
        #
        data = self.process_template(report_file_name, output_format, context)
        self.log(context)
        return data
    
    def momap_management_statistics_report(self, date_from, date_to):
        data = {}

        total_referral = 0
        client_call = 0 
        total_booked = 0
        complete = 0 
        cancel_before = 0
        cancel_after = 0
        cancel_after_sixweeks = 0
        p_total_referral = 0
        p_client_call = 0 
        p_total_booked = 0
        p_complete = 0 
        p_cancel_before = 0
        p_cancel_after = 0
        p_cancel_after_sixweeks = 0 
        total = {
            'referral':0,
            'booked':0,
            'complete': 0,
            'client_call':0,
            'cancel_before':0,
            'cancel_after':0,
            'cancel_after_six':0,
            'p_referral':0,
            'p_booked':0,
            'p_complete': 0,
            'p_client_call':0,
            'p_cancel_before':0,
            'p_cancel_after':0,
            'p_cancel_after_six':0,
            
            'sum_referral':total_referral + p_total_referral,
            'sum_booked':total_booked + p_total_booked,
            'sum_complete':complete + p_complete,
            'sum_client_call':client_call + p_client_call,
            'sum_cancel_before':cancel_before + p_cancel_after,
            'sum_cancel_after':cancel_after + p_cancel_after,
            'sum_cancel_after_six':cancel_after_sixweeks + p_cancel_after_sixweeks
        }
        
        list = []
        mc_list = {}
        
        self.cr.execute('select name from mobility_mobility_centre order by name')
        for mc in self.cr.dictfetchall():
            mc_list[mc['name']] = {'name':mc['name'],
                                   'number_recieved':0,
                                   'previous_recieved':0,
                                   'number_booked':0,
                                   'previous_booked':0,
                                   'number_client_call':0,
                                   'previous_client_call':0,
                                   'number_complete':0,
                                   'previous_complete':0,
                                   'number_cancel_before':0,
                                   'previous_cancel_before':0,
                                   'number_cancel_after':0,
                                   'previous_cancel_after':0,
                                   'number_cancel_after_six':0,
                                   'previous_cancel_after_six':0,
								   'sum_referral':0,
                                   'sum_booked':0,
                                   'sum_client_call':0,
                                   'sum_complete':0,
                                   'sum_cancel_before':0,
                                   'sum_cancel_after':0,
                                   'sum_cancel_after_six':0}
        mc_list=OrderedDict(sorted(mc_list.iteritems(), key=lambda x: x[0]))
        self.log(mc_list)
        self.cr.execute("select name,count(*) as count from (select mc.name as name, m.id as id from momap_referral m\
             inner join mobility_mobility_centre mc on mc.id = m.mobility_centre_referred where m.referral_date >= '" + date_from + " 00:00:00'\
              and m.referral_date <= '" + date_to + " 23:59:59') as sql group by name order by name")
        records = self.cr.dictfetchall()
        for record in records:
            list.append(record['name'])
            mc_list[record['name']]['number_recieved'] = record['count']

        self.cr.execute("select name, count(*) as count from (select mc.name, m.id from momap_referral m inner join\
             momap_appointments a on a.appointment_id = m.id inner join mobility_mobility_centre mc on\
              mc.id = m.mobility_centre_referred where m.referral_date <= '" + date_from + " 00:00:00' and\
               a.booking_date >= '" + date_from + " 00:00:00' and (a.state = 'active' or m.state in\
                ('notify_mc', 'remind_notify_mc'))) as rec group by name")

        records = self.cr.dictfetchall()
        for record in records:
            list.append(record['name'])
            mc_list[record['name']]['previous_recieved'] = record['count']

        self.cr.execute("select name, count(*) from (select mc.name, m.id from momap_referral m\
             inner join momap_appointments a on a.appointment_id = m.id inner join mobility_mobility_centre mc\
              on mc.id = m.mobility_centre_referred where m.referral_date >= '" + date_from + " 00:00:00' and\
               m.referral_date <= '" + date_to + " 23:59:59' and a.state = 'active') as rec group by name")
        records = self.cr.dictfetchall()
        for record in records:
            list.append(record['name'])
            mc_list[record['name']]['number_booked'] = record['count']

        self.cr.execute("select name, count(*) from (select mc.name, m.id from momap_referral m inner join\
             momap_appointments a on a.appointment_id = m.id inner join mobility_mobility_centre mc on\
             mc.id = m.mobility_centre_referred where m.referral_date <= '" + date_from + " 00:00:00' and\
              a.state = 'active') as rec group by name")

        records = self.cr.dictfetchall()
        for record in records:
            list.append(record['name'])
            mc_list[record['name']]['previous_booked'] = record['count']

        self.cr.execute("select name, count(*) from (select mc.name, m.id from momap_referral m inner join\
             mobility_mobility_centre mc on mc.id = m.mobility_centre_referred where m.referral_date >= '" + date_from + " 00:00:00'\
              and m.referral_date <= '" + date_to + " 23:59:59' and m.state in ('notify_mc', 'remind_notify_mc')) as rec group by name")
        records = self.cr.dictfetchall()
        for record in records:
            list.append(record['name'])
            mc_list[record['name']]['number_client_call'] = record['count']

        self.cr.execute("select name, count(*) from (select mc.name, m.id from momap_referral m inner join\
          mobility_mobility_centre mc on mc.id = m.mobility_centre_referred where m.referral_date <= '" + date_from + " 00:00:00'\
           and m.state in ('notify_mc', 'remind_notify_mc')) as rec group by name")

        records = self.cr.dictfetchall()
        for record in records:
            list.append(record['name'])
            mc_list[record['name']]['previous_client_call'] = record['count']
            
        self.cr.execute("select name, count(*) from (select mc.name, m.id from momap_referral m inner join\
         momap_appointments a on a.appointment_id = m.id inner join  mobility_mobility_centre mc on\
          mc.id = m.mobility_centre_referred where m.referral_date >= '" + date_from + " 00:00:00' and\
           m.referral_date <= '" + date_to + " 23:59:59' and a.state = 'completed' and a.logical_date <= '" + date_to + " 23:59:59')\
            as rec group by name")
        records = self.cr.dictfetchall()
        for record in records:
            list.append(record['name'])
            mc_list[record['name']]['number_complete'] = record['count']

        self.cr.execute("select name, count(*) from (select mc.name, m.id from momap_referral m inner join momap_appointments a \
            on a.appointment_id = m.id inner join  mobility_mobility_centre mc on mc.id = m.mobility_centre_referred where \
            m.referral_date <= '" + date_from + " 00:00:00' and a.state = 'completed' and a.logical_date >= '" + date_from + " 00:00:00'\
             and a.logical_date <= '" + date_to + " 23:59:59') as rec group by name")

        records = self.cr.dictfetchall()
        for record in records:
            list.append(record['name'])
            mc_list[record['name']]['previous_complete'] = record['count']

        self.cr.execute("select name, count(*) from (select mc.name, m.id from momap_referral m\
         inner join  mobility_mobility_centre mc on mc.id = m.mobility_centre_referred where\
          m.referral_date >= '" + date_from + " 00:00:00' and m.referral_date <= '" + date_to + " 23:59:59'\
           and m.state = 'cancelled' and  m.cancellation_date >= '" + date_from + " 00:00:00' and\
            m.cancellation_date <= '" + date_to + " 23:59:59' and m.cancel_active = False) as rec group by name")
        records = self.cr.dictfetchall()
        for record in records:
            list.append(record['name'])
            mc_list[record['name']]['number_cancel_before'] = record['count']

        self.cr.execute("select name, count(*) from (select mc.name, m.id from momap_referral m\
         inner join  mobility_mobility_centre mc on mc.id = m.mobility_centre_referred where\
          m.referral_date <= '" + date_from + " 00:00:00' and m.state = 'cancelled' and m.cancellation_date >= '" + date_from + " 00:00:00'\
           and m.cancellation_date <= '" + date_to + " 23:59:59' and m.cancel_active = False) as rec group by name")

        records = self.cr.dictfetchall()
        for record in records:
            list.append(record['name'])
            mc_list[record['name']]['previous_cancel_before'] = record['count']

        self.cr.execute("select name, count(*) from (select mc.name, m.id from momap_referral m\
         inner join  mobility_mobility_centre mc on mc.id = m.mobility_centre_referred where\
          m.referral_date >= '" + date_from + " 00:00:00' and m.referral_date <= '" + date_to + " 23:59:59'\
           and m.state = 'cancelled' and  m.cancellation_date >= '" + date_from + " 00:00:00' and\
            m.cancellation_date <= '" + date_to + " 23:59:59' and m.cancel_active = True) as rec group by name")
        records = self.cr.dictfetchall()
        for record in records:
            list.append(record['name'])
            mc_list[record['name']]['number_cancel_after'] = record['count']

        self.cr.execute("select name, count(*) from (select mc.name, m.id from momap_referral m\
         inner join  mobility_mobility_centre mc on mc.id = m.mobility_centre_referred where\
          m.referral_date <= '" + date_from + " 00:00:00' and m.state = 'cancelled' and m.cancellation_date >= '" + date_from + " 00:00:00'\
           and m.cancellation_date <= '" + date_to + " 23:59:59' and m.cancel_active = True) as rec group by name")

        records = self.cr.dictfetchall()
        for record in records:
            list.append(record['name'])
            mc_list[record['name']]['previous_cancel_after'] = record['count']

        self.cr.execute("select name, count(*) from (select mc.name, m.id from momap_referral m\
         inner join  mobility_mobility_centre mc on mc.id = m.mobility_centre_referred where\
          m.referral_date >= '" + date_from + " 00:00:00' and m.referral_date <= '" + date_to + " 23:59:59'\
           and m.state = 'cancel_6week' and  m.cancellation_date >= '" + date_from + " 00:00:00' and\
            m.cancellation_date <= '" + date_to + " 23:59:59') as rec group by name")
        records = self.cr.dictfetchall()
        for record in records:
            list.append(record['name'])
            mc_list[record['name']]['number_cancel_after_six'] = record['count']

        self.cr.execute("select name, count(*) from (select mc.name, m.id from momap_referral m\
         inner join  mobility_mobility_centre mc on mc.id = m.mobility_centre_referred where\
          m.referral_date <= '" + date_from + " 00:00:00' and m.state = 'cancelled' and m.cancellation_date >= '" + date_from + " 00:00:00'\
           and m.cancellation_date <= '" + date_to + " 23:59:59') as rec group by name")

        records = self.cr.dictfetchall()
        for record in records:
            list.append(record['name'])
            mc_list[record['name']]['previous_cancel_after_six'] = record['count']
        
        self.log(list)
        for rlist in set(list):
            mc_list[rlist]
            mc_list[rlist]['sum_referral'] = (mc_list[rlist]['previous_recieved'] + mc_list[rlist]['number_recieved'])
            mc_list[rlist]['sum_booked'] = (mc_list[rlist]['previous_booked'] + mc_list[rlist]['number_booked'])
            mc_list[rlist]['sum_client_call'] = (mc_list[rlist]['previous_client_call'] + mc_list[rlist]['number_client_call'])
            mc_list[rlist]['sum_complete'] = (mc_list[rlist]['previous_complete'] + mc_list[rlist]['number_complete'])
            mc_list[rlist]['sum_cancel_before'] = (mc_list[rlist]['previous_cancel_before'] + mc_list[rlist]['number_cancel_before'])
            mc_list[rlist]['sum_cancel_after'] = (mc_list[rlist]['previous_cancel_after'] + mc_list[rlist]['number_cancel_after'])
            mc_list[rlist]['sum_cancel_after_six'] = (mc_list[rlist]['previous_cancel_after_six'] + mc_list[rlist]['number_cancel_after_six'])
        # self.log(mc_list)
        newlist = []
        for rlist in set(list):
            temp = mc_list[rlist]
            total['referral'] += mc_list[rlist]['number_recieved']
            total['p_referral'] += mc_list[rlist]['previous_recieved']
            mc_list[rlist]['sum_referral'] = (mc_list[rlist]['previous_recieved'] + mc_list[rlist]['number_recieved'])
            total['sum_referral'] += mc_list[rlist]['sum_referral']
            
            total['booked'] += mc_list[rlist]['number_booked']
            total['p_booked'] += mc_list[rlist]['previous_booked']
            mc_list[rlist]['sum_booked'] = (mc_list[rlist]['previous_booked'] + mc_list[rlist]['number_booked'])
            total['sum_booked'] += mc_list[rlist]['sum_booked']
            
            total['client_call'] += mc_list[rlist]['number_client_call']
            total['p_client_call'] += mc_list[rlist]['previous_client_call']
            mc_list[rlist]['sum_client_call'] = (mc_list[rlist]['previous_client_call'] + mc_list[rlist]['number_client_call'])
            total['sum_client_call'] += mc_list[rlist]['sum_client_call']
            
            total['complete'] += mc_list[rlist]['number_complete']
            total['p_complete'] += mc_list[rlist]['previous_complete']
            mc_list[rlist]['sum_complete'] = (mc_list[rlist]['previous_complete'] + mc_list[rlist]['number_complete'])
            total['sum_complete'] += mc_list[rlist]['sum_complete']
            
            total['cancel_before'] += mc_list[rlist]['number_cancel_before']
            total['p_cancel_before'] += mc_list[rlist]['previous_cancel_before']
            mc_list[rlist]['sum_cancel_before'] = (mc_list[rlist]['previous_cancel_before'] + mc_list[rlist]['number_cancel_before'])
            total['sum_cancel_before'] += mc_list[rlist]['sum_cancel_before']
            
            total['cancel_after'] += mc_list[rlist]['number_cancel_after']
            total['p_cancel_after'] += mc_list[rlist]['previous_cancel_after']
            mc_list[rlist]['sum_cancel_after'] = (mc_list[rlist]['previous_cancel_after'] + mc_list[rlist]['number_cancel_after'])
            total['sum_cancel_after'] += mc_list[rlist]['sum_cancel_after']
            
            total['cancel_after_six'] += mc_list[rlist]['number_cancel_after_six']
            total['p_cancel_after_six'] += mc_list[rlist]['previous_cancel_after_six']
            mc_list[rlist]['sum_cancel_after_six'] = (mc_list[rlist]['previous_cancel_after_six'] + mc_list[rlist]['number_cancel_after_six'])
            total['sum_cancel_after_six'] += mc_list[rlist]['sum_cancel_after_six']
        # self.log(mc_list)
        data.update({
            'momap_report_data': mc_list,
            'momap_report_total': total
        })
        return data


    def momap_mobility_centre_report(self, date_from, date_to, mc_id):
        data = {}
        data.update({
            'momap_adaptations': self._get_adaptations_list_lines(date_from, date_to, mc_id),
            'momap_familiarisations': self._get_familiarization_list_lines(date_from, date_to, mc_id),
        })
        return data

    def _get_adaptations_list_lines(self, date_from, date_to, mc_id):
        
        temp_res = []
        
        self.cr.execute("select forum_referrence_no as ref, a.apmnt_date as date, (case when a.state = 'active' then 'Booked' else a.state end ) as status, \
            (case when date_part('day',a.apmnt_date-a.cancellation_date) > 2 then 'No' else (case when a.cancellation_date is not null then 'Yes' else '' end) end) as can_status, \
            a.cancellation_information as reason, mc.name as mc, \
            m.motability_crn as crn, m.client_post_code as post_code, m.date_of_birth as dob, \
            m.client_first_name as fname, m.client_last_name as lname, '...' as notes \
            from momap_referral m \
            inner join mobility_mobility_centre mc on mc.id = m.mobility_centre_referred \
            left outer join momap_appointments a on a.appointment_id = m.id \
            where a.apmnt_date >= %s \
            and a.apmnt_date <= %s\
            and mc.id = %s \
            and m.referral_type = 'adaptation' order by a.apmnt_date", (date_from + ' 00:00:00', date_to + ' 23:59:59', str(mc_id)))
            
        res = self.cr.dictfetchall()
        if (len(res) > 0):
            cnt = 0
            for r in res:
                res[cnt]['crn']=res[cnt]['crn']
                res[cnt]['ref'] = res[cnt]['ref'][0:5] + ' ' + res[cnt]['ref'][5:]
                res[cnt]['status'] = res[cnt]['status'][0:1].upper() + res[cnt]['status'][1:]
                res[cnt]['reason'] = (res[cnt]['reason'][0:1].upper() + res[cnt]['reason'][1:]) if res[cnt]['reason'] else ''
                res[cnt]['date'] = str(datetime.datetime.strptime(res[cnt]['date'], '%Y-%m-%d').strftime('%d/%m/%Y')) if res[cnt]['date'] else ''
                res[cnt]['dob'] = str(datetime.datetime.strptime(res[cnt]['dob'], '%Y-%m-%d').strftime('%d/%m/%Y')) if res[cnt]['dob'] else ''
                temp_res.append(res[cnt])
                cnt += 1

        self.cr.execute("select forum_referrence_no as ref, a.logical_date as date, m.state,\
            mc.name as mc, m.motability_crn as crn, m.client_post_code as post_code, m.date_of_birth as dob,\
             m.client_first_name as fname, m.client_last_name as lname\
            from momap_referral m inner join mobility_mobility_centre mc on mc.id = m.mobility_centre_referred \
            left outer join momap_appointments a on a.appointment_id = m.id where \
            a.logical_date < '" + date_from + " 00:00:00' and mc.id = " + str(mc_id) + " and m.referral_type = 'adaptation'\
            and a.state='active' order by a.apmnt_date")
        res = self.cr.dictfetchall()
        
        if (len(res) > 0):
            cnt = 0
            for r in res:
                res[cnt]['ref'] = res[cnt]['ref'][0:5] + ' ' + res[cnt]['ref'][5:]
                res[cnt]['status'] = 'Booked'
                res[cnt]['reason'] = ''
                res[cnt]['date'] = str(datetime.datetime.strptime(res[cnt]['date'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y'))
                res[cnt]['can_status'] = 'No'
                res[cnt]['notes'] = ''
                res[cnt]['dob'] = str(datetime.datetime.strptime(res[cnt]['dob'], '%Y-%m-%d').strftime('%d/%m/%Y')) if res[cnt]['dob'] else ''
                temp_res.append(res[cnt])
                cnt += 1
        
        self.cr.execute("select forum_referrence_no as ref, mc.name as mc, motability_crn as crn, client_post_code as post_code,\
            client_first_name as fname, client_last_name as lname, date_of_birth as dob from momap_referral m inner join \
            mobility_mobility_centre mc on mc.id = m.mobility_centre_referred where referral_type = 'adaptation'\
             and state in ('notify_mc','remind_notify_mc') and mc.id = " + str(mc_id))
        res = self.cr.dictfetchall()
        
        if (len(res) > 0):
            cnt = 0
            for r in res:
                res[cnt]['ref'] = res[cnt]['ref'][0:5] + ' ' + res[cnt]['ref'][5:]
                res[cnt]['status'] = ''
                res[cnt]['reason'] = ''
                res[cnt]['date'] = ''
                res[cnt]['can_status'] = ''
                res[cnt]['notes'] = ''
                res[cnt]['dob'] = str(datetime.datetime.strptime(res[cnt]['dob'], '%Y-%m-%d').strftime('%d/%m/%Y')) if res[cnt]['dob'] else ''
                temp_res.append(res[cnt])
                cnt += 1
        
        if len(temp_res) > 0:
            return temp_res
        else:
            dummy = [{'can_status': None,
                      'crn': None,
                      'date': None,
                      'dob': None,
                      'mc': 'test',
                      'fname': None,
                      'lname': None,
                      'notes': None,
                      'post_code': None,
                      'reason': None,
                      'ref': None,
                      'status': None}]
            return dummy

    def _get_familiarization_list_lines(self, date_from, date_to, mc_id):
        temp_res = []
        
        self.cr.execute("select forum_referrence_no as ref, a.apmnt_date as date, (case when a.state = 'active' then 'Booked' else a.state end ) as status, \
            (case when date_part('day',a.apmnt_date-a.cancellation_date) > 2 then 'No' else (case when a.cancellation_date is not null then 'Yes' else '' end) end ) as can_status, \
            a.cancellation_information as reason, mc.name as mc, \
            m.motability_crn as crn, m.client_post_code as post_code, m.date_of_birth as dob, \
            m.client_first_name as fname, m.client_last_name as lname, '...' as notes, (a.total_minutes / 60) as noh \
            from momap_referral m \
            inner join mobility_mobility_centre mc on mc.id = m.mobility_centre_referred \
            left outer join momap_appointments a on a.appointment_id = m.id \
            where a.apmnt_date >= %s \
            and a.apmnt_date <= %s\
            and mc.id = %s \
            and m.referral_type = 'familiarisation' order by a.apmnt_date", (date_from + ' 00:00:00', date_to + ' 23:59:59', str(mc_id)))

        res = self.cr.dictfetchall()
        if (len(res) > 0):
            cnt = 0
            for r in res:
                res[cnt]['ref'] = res[cnt]['ref'][0:5] + ' ' + res[cnt]['ref'][5:]
                res[cnt]['noh'] = int(res[cnt]['noh'] if res[cnt]['noh'] else '0')
                res[cnt]['status'] = res[cnt]['status'][0:1].upper() + res[cnt]['status'][1:]
                res[cnt]['reason'] = (res[cnt]['reason'][0:1].upper() + res[cnt]['reason'][1:]) if res[cnt]['reason'] else ''
                res[cnt]['date'] = str(datetime.datetime.strptime(res[cnt]['date'], '%Y-%m-%d').strftime('%d/%m/%Y')) if res[cnt]['date'] else ''
                res[cnt]['dob'] = str(datetime.datetime.strptime(res[cnt]['dob'], '%Y-%m-%d').strftime('%d/%m/%Y')) if res[cnt]['dob'] else ''
                temp_res.append(res[cnt])
                cnt += 1

        # self.cr.execute("select forum_referrence_no as ref, a.logical_date as date, m.state,\
            # mc.name as mc, m.motability_crn as crn, m.client_post_code as post_code, m.date_of_birth as dob,\
             # m.client_first_name as fname, m.client_last_name as lname, (a.total_minutes / 60) as noh\
            # from momap_referral m inner join mobility_mobility_centre mc on mc.id = m.mobility_centre_referred \
            # left outer join momap_appointments a on a.appointment_id = m.id where \
            # a.logical_date > '" + date_from + " 00:00:00' and mc.id = " + str(mc_id) + " \
            # and m.referral_type = 'familiarisation' and a.state='active' and m.referral_date < '" + date_from + " 00:00:00'")

        # self.log("select forum_referrence_no as ref, a.logical_date as date, m.state, mc.name as mc, m.motability_crn as crn, m.client_post_code as post_code, m.date_of_birth as dob, m.client_first_name as fname, m.client_last_name as lname, (a.total_minutes / 60) as noh from momap_referral m inner join mobility_mobility_centre mc on mc.id = m.mobility_centre_referred  left outer join momap_appointments a on a.appointment_id = m.id where  a.logical_date > '" + date_from + " 00:00:00' and mc.id = " + str(mc_id) + "  and m.referral_type = 'familiarisation' and a.state='active' and m.referral_date < '" + date_from + " 00:00:00'")

        # res = self.cr.dictfetchall()
        # self.log(res)
        # if (len(res) > 0):
            # cnt = 0
            # for r in res:
                # res[cnt]['ref'] = res[cnt]['ref'][0:5] + ' ' + res[cnt]['ref'][5:]
                # res[cnt]['status'] = 'Booked'
                # res[cnt]['reason'] = ''
                # res[cnt]['noh'] = int(res[cnt]['noh'] if res[cnt]['noh'] else '0')
                # res[cnt]['date'] = str(datetime.datetime.strptime(res[cnt]['date'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y'))
                # res[cnt]['can_status'] = 'No'
                # res[cnt]['notes'] = ''
                # res[cnt]['dob'] = str(datetime.datetime.strptime(res[cnt]['dob'], '%Y-%m-%d').strftime('%d/%m/%Y')) if res[cnt]['dob'] else ''
                # temp_res.append(res[cnt])
                # cnt += 1

        self.cr.execute("select forum_referrence_no as ref, a.logical_date as date, m.state,\
            mc.name as mc, m.motability_crn as crn, m.client_post_code as post_code, m.date_of_birth as dob,\
             m.client_first_name as fname, m.client_last_name as lname, (a.total_minutes / 60) as noh\
            from momap_referral m inner join mobility_mobility_centre mc on mc.id = m.mobility_centre_referred \
            left outer join momap_appointments a on a.appointment_id = m.id where \
            a.logical_date < '" + date_from + " 00:00:00' and mc.id = " + str(mc_id) + "\
             and m.referral_type = 'familiarisation' and a.state='active'")
        res = self.cr.dictfetchall()
        self.log(res)

        if (len(res) > 0):
            cnt = 0
            for r in res:
                res[cnt]['ref'] = res[cnt]['ref'][0:5] + ' ' + res[cnt]['ref'][5:]
                res[cnt]['status'] = 'Booked'
                res[cnt]['reason'] = ''
                res[cnt]['date'] = str(datetime.datetime.strptime(res[cnt]['date'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y'))
                res[cnt]['can_status'] = 'No'
                res[cnt]['notes'] = ''
                res[cnt]['noh'] = int(res[cnt]['noh'] if res[cnt]['noh'] else '0')
                res[cnt]['dob'] = str(datetime.datetime.strptime(res[cnt]['dob'], '%Y-%m-%d').strftime('%d/%m/%Y')) if res[cnt]['dob'] else ''
                temp_res.append(res[cnt])
                cnt += 1
        self.log('6')
        
        if len(temp_res) > 0:
            self.log(temp_res)
            return temp_res
        else:
            dummy = [{'can_status': None,
                      'crn': None,
                      'date': None,
                      'dob': None,
                      'mc': None,
                      'fname': None,
                      'lname': None,
                      'notes': None,
                      'noh': None,
                      'post_code': None,
                      'reason': None,
                      'ref': None,
                      'status': None}]
            return dummy

        
    def equipment_information(self, e_id):
        data = {}
        if e_id :
            data = {'make':e_id.make,
                  'model':e_id.make,
                  'serial':e_id.serial_no if e_id.serial_no else "",
                  'size':e_id.size if e_id.size else "",
                  'received_date':datetime.datetime.strptime(e_id.manufacture_date, "%Y-%m-%d").strftime("%d-%B-%Y") if e_id.manufacture_date else "",
                  'asset_type':e_id.asset_type if e_id.asset_type != 'Other' else e_id.other_asset,
                  'asset_no': e_id.onwer_asset_no if e_id.onwer_asset_no else "",
                  'year':e_id.year if e_id.year else "",
                  'type':e_id.type if e_id.type else "",
                  'multiplex':'Y' if e_id.multiplex else 'N'
                  }
            data.update(self.person_information(e_id.owner, 'owner'))
            data.update(self.person_information(e_id.current_user_id, 'current_user'))
        else :
            data = {'make':"",
                  'model':"",
                  'serial':"",
                  'size':"",
                  'received_date':"",
                  'asset_type':"",
                  'asset_no': "",
                  'year':"",
                  'type':"",
                  'multiplex':""
                  }
        return data
    def part_ordered_information(self, o_id):
        data = []
        part = {}
        ordered_ids = self.pool.get('cmc.workshop.part.ordered').search(self.cr, self.uid, [('workshop_id', '=', int(o_id[0]))])
        if len(ordered_ids) > 0:
            for id in ordered_ids:
                br = self.pool.get('cmc.workshop.part.ordered').browse(self.cr, self.uid, id)
                vals = {
                      'part_no':br.part_no,
                      'description':br.description if br.description else "",
                      'quantity':br.quantity if br.quantity else 0,
                      'quote_price':"%.2f " % (br.quote_price if br.quote_price else 0),
                      'trade_price':"%.2f " % (br.price if br.price else 0),
                      'amount':"%.2f " % (int(br.quantity if br.quantity else 0.00) * br.quote_price)
                      }
                vals.update(self.person_information(br.ordered_from,'supplier'))
                data.append(vals)
        part = data
        return part
    def reserved_equipment_information(self, e_id):
        data = []
        part = {}
        self.cr.execute('select equipment_id from equipment_equipment_rel where supply_id=%d' % (int(e_id[0])))
        e_ids = self.cr.fetchall()
        if e_ids is not None and len(e_ids) > 0:
            e = [ee[0] for ee in e_ids]
            if len(e) > 0:
                for id in e:
                    br = self.pool.get('cmc.equipment').browse(self.cr, self.uid, id)
                    vals = {'make':br.make,
                          'model':br.model,
                          'serial_no':br.serial_no if br.serial_no else "",
                          'year':br.year if br.year else "",
                          'price':br.price if br.price else '0.00'
                          }
                    data.append(vals)
        return data   
    def person_information(self, p_id, prefix):
        data = {}
        if p_id :
            data[prefix + '_id'] = p_id.person_id if p_id.person_id else "" 
            data[prefix + '_title'] = (self.title(p_id.title)if p_id.title != 'other' else p_id.title_other) if not p_id.is_organisation else ""
            data[prefix + '_first_name'] = p_id.first_name if p_id.first_name else ""
            data[prefix + '_last_name'] = p_id.last_name if p_id.last_name else "" 
            data[prefix + '_display_name'] = p_id.display_name
            address = []
            if p_id.address_line_1:
                address.append(p_id.address_line_1)
            if p_id.address_line_2:
                address.append(p_id.address_line_2)
            if p_id.city:
                address.append(p_id.city)
            if p_id.county:
                address.append(p_id.county)
            if p_id.postcode:
                address.append(p_id.postcode)
            if len(address) > 0 :
                data[prefix + '_address'] = ','.join(address)
            else:
                data[prefix + '_address'] = ""
            data[prefix + '_telephone'] = p_id.telephone if p_id.telephone else ""
            data[prefix + '_city'] = p_id.city if p_id.city else ""
            data[prefix + '_county'] = p_id.county if p_id.county else ""
            data[prefix + '_postcode'] = p_id.postcode if p_id.postcode else ""
            data[prefix + '_email_address'] = p_id.email_address if p_id.email_address else ""
            data[prefix + '_dob'] = datetime.datetime.strptime(p_id.birth_date, "%Y-%m-%d").strftime("%d-%B-%Y") if p_id.birth_date else ""
            data[prefix + '_ethnicity'] = p_id.ethnicity if p_id.ethnicity else ""
            data[prefix + '_eligible'] = p_id.eligible if p_id.eligible else ""
        else:
            data[prefix + '_id'] = ""
            data[prefix + '_title'] = ""
            data[prefix + '_first_name'] = ""
            data[prefix + '_last_name'] = "" 
            data[prefix + '_display_name'] = ""
            data[prefix + '_address'] = ""
            data[prefix + '_city'] = ""
            data[prefix + '_county'] = ""
            data[prefix + '_postcode'] = ""
            data[prefix + '_telephone'] = ""
            data[prefix + '_email_address'] = ""
            data[prefix + '_dob'] = ""
            data[prefix + '_ethnicity'] = ""
            data[prefix + '_eligible'] = ""
        return data
    def appointment_timing(self, ids, prefix, type):
        app_ids = False
        appt_active_record = False
        start_date_time = start_date = start_time = p_attendees = location = owner = ""
        result = {}
        self.log(prefix)
        type_name = ""
        if type == 'workshop':
            type_name = 'workshop_id'
        elif type == 'assessment':
            type_name = 'assessment_id'
        elif type == 'equipment_supply':
            type_name = 'equipment_supply_process_id'
        if type_name != "":
            if prefix == 'active':
                self.cr.execute('select * from cmc_appointments where (state = \'active\' or state = \'active_clash\') and ' + type_name + '=%d order by apmnt_start_date_time desc' % (int(ids[0])))
            elif prefix == 'complete':
                self.cr.execute('select * from cmc_appointments where (state = \'completed\') and ' + type_name + '=%d order by apmnt_start_date_time desc' % (int(ids[0])))
            elif prefix == 'confirmed':
                self.cr.execute('select * from cmc_appointments where (state = \'confirmed\') and ' + type_name + '=%d order by apmnt_start_date_time desc' % (int(ids[0])))
            else:
                raise except_orm('Warning', 'Wrong prefix')
            appt_ids = map(itemgetter(0), self.cr.fetchall())
            if len(appt_ids) > 0:
                appt_active_record = self.pool.get('cmc.appointments').browse(self.cr, self.uid, appt_ids[0])
                start_date_time = appt_active_record.apmnt_start_date_time.split(" ")
                start_date = datetime.datetime.strptime(start_date_time[0], '%Y-%m-%d').strftime('%d-%B-%Y')
                start_time = start_date_time[1][:5]
                location = appt_active_record.location if appt_active_record.location else ""
                owner = appt_active_record.owner.name if appt_active_record.owner else "" 
                persons = []
                self.cr.execute('select name from res_users where id in (select user_id from user_appointment_rel where appointment_id=%d)' % (int(appt_ids[0])))
                p_ids = self.cr.fetchall()
                if p_ids is not None:
                    persons = [name[0] for name in p_ids]
                if len(persons) > 0:
                    p_attendees = ','.join(persons)
                else:
                    p_attendees = ""
        return {
                prefix + '_date':start_date,
                prefix + '_time':start_time,
                prefix + '_attendees':p_attendees,
                prefix + '_location':location,
                prefix + '_owner':owner
                }
        
    def title(self, title):
        t = {
            'dr': 'Dr',
            'mr':'Mr',
            'ms':'Miss',
            'Ms':'Ms',
            'mrs':'Mrs',
            'other':'Other',
			'Master':'Master'
            }
        return t.get(title, False)
    def driving_name(self, type):
        t = {
            'general':'GENERAL',
            'full_driving_assessment': 'FULL DRIVING ASSESSMENT',
            'wheelchair_assessment':'WHEELCHAIR ASSESSMENT',
            'drive_from_wheelchair_assessment':'DRIVE FROM WHEELCHAIR ASSESSMENT',
            'passenger_assessment':'PASSENGER ASSESSMENT',
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
            'pressure_mapping_assessment':'Pressure Mapping Assessment', 'Driving Tution':'Driving Tution', 'MoMap Familiarisation':'MoMap Familiarisation',
            }
        return t.get(type, False)
    def referer_name(self, type):
        t = {'charity': 'Charity',
           'client_family':'Client/Family',
           'dvla': 'DVLA',
           'employer': 'Employer',
           'employment_agency':'Employment Agency(PACT -Access to Work',
           'health_professional': 'Health Professional',
           'insurance_company': 'Insurance Company',
           'motability_grants':'Motability Grants',
           'motability_operations': 'Motability Operations',
           'nhs': 'NHS',
           'other':'Other',
           'other_centre':'Other Assessment Centre',
           'review':'Review following a previous assessment',
           'social_services':'Social Services',
           'solicitors':'Solitcitors',
           }
        return t.get(type, False)
    def process_template(self, template_file, output_format, context=None):
        """
        Will process a relatorio template and return the name
        of the temp output file.
        """
        if context is None: context = {}
        #
        # Get the template
        #
        self.log("Loading template %s from %s" % (self.name, template_file))
        try:
            template = OOTemplate(source=None,
                            filepath=template_file,
                            output_format=output_format,
                            openoffice_port=self.openoffice_port,
                            autostart_openoffice=self.autostart_openoffice,
                            logger=self.log)
        except OOTemplateException, ex:
            raise OOReportException(_("Error loading the OpenOffice template: %s") % ex)

        #
        # Process the template
        #
        self.log("Rendering template %s as %s" % (self.name, output_format))
        try:
            data = template.oo_render(context=context)
        except OOTemplateException, ex:
            raise OOReportException(_("Error processing the OpenOffice template: %s") % ex)

        return data



class openoffice_report(report.interface.report_int):
    """
    Registers an OpenOffice/Relatorio report.
    """

    def __init__(self, name, model, parser=None, context=None):
        if context is None: context = {}
        # Remove report name from list of services if it already
        # exists to avoid report_int's assert. We want to keep the
        # automatic registration at login, but at the same time we
        # need modules to be able to use a parser for certain reports.
        if name in netsvc.SERVICES:
            del netsvc.SERVICES[name]
        super(openoffice_report, self).__init__(name)
        self.model = model
        self.parser = parser
        self._context = context

    def create(self, cr, uid, ids, datas, context=None):
        """
        Register the report with this handler.
        """
        name = self.name

        if self.parser:
            options = self.parser(cr, uid, ids, datas, context)
            ids = options.get('ids', ids)
            name = options.get('name', self.name)
            # Use model defined in openoffice_report definition. Necesary for menu entries.
            datas['model'] = options.get('model', self.model)
            datas['records'] = options.get('records', [])

        self._context.update(context)

        #
        # Find the output format
        #
        reports = pooler.get_pool(cr.dbname).get('ir.actions.report.xml')
        report_ids = reports.search(cr, uid, [('report_name', '=', name[7:])], context=context)
        report_type = reports.read(cr, uid, report_ids[0], ['report_type'])['report_type']
        if report_type.startswith('oo-'):
            output_format = report_type.split('-')[1]
        else:
            output_format = 'pdf'

        #
        # Get the report
        #
        rpt = OOReport(name, cr, uid, ids, datas, self._context)
        return (rpt.execute(output_format=output_format), output_format)






#
# Ugly hack to avoid developers the need to register reports. ------------------
# Based on NaN jasper_reports module.
#

def register_openoffice_report(name, model):
    """
    Registers a report to use the OpenOffice reporting engine.
    """
    name = 'report.%s' % name
    # Register only if it didn't exist another report with the same name
    # given that developers might prefer/need to register the reports themselves.
    # For example, if they need their own parser.
    if netsvc.service_exist(name):
        if isinstance(netsvc.SERVICES[name], openoffice_report):
            return
        del netsvc.SERVICES[name]
    openoffice_report(name, model)

#
# This hack allows automatic registration of OpenOffice files without
# the need for developers to register them programatically.
#
OLD_REGISTER_ALL = report.interface.register_all
def new_register_all(db):
    """
    Wrapper around the register_all method of report.interface
    that registers 'automagically' OpenOffice reports.
    """
    # Call the original register_all
    value = OLD_REGISTER_ALL(db)

    #
    # Search for reports with 'oo-<something>' type
    # and register them
    #
    cr = db.cursor()
    cr.execute("SELECT * FROM ir_act_report_xml WHERE report_type LIKE 'oo-%' ORDER BY id")
    records = cr.dictfetchall()
    cr.close()
    for record in records:
        register_openoffice_report(record['report_name'], record['model'])

    return value

# Chain our method into report.interface:
report.interface.register_all = new_register_all



