# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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


{
    'name': 'Invoice on analytic lines',
    'version': '1.0',
    'category': 'Generic Modules/Accounting',
    'description': """
Module to generate invoices based on costs (human resources, expenses, ...).
You can define price lists in analytic account, make some theoretical revenue
reports, eso.""",
    'author': 'Tiny',
    'website': 'http://www.openerp.com',
    'depends': ['account', 'hr_timesheet'],
    'init_xml': [],
    'update_xml': [
        'security/ir.model.access.csv',
        'hr_timesheet_invoice_view.xml',
        'hr_timesheet_invoice_wizard.xml',
        'hr_timesheet_invoice_report.xml'
    ],
    'demo_xml': ['hr_timesheet_invoice_demo.xml'],
    'installable': True,
    'active': False,
    'certificate': '0056091842381',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
