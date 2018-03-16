# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Website Helpdesk Support Ticket for Customer",
    'version': "11.0.0.1",
    'author': "Browseinfo",
    'category': "Website",
    'summary': "This apps helps to Manage Customer Helpdesk Support Ticket from website inculding timesheet and invoice",
    'description': "A helpdesk / support ticket system for your website, support management from website, website support ticket, website helpdesk management, Support system for your website, website support management, submit support request, support form, Ticket support, website support ticket, website issue, website project issue, website crm management, website ticket handling,support management, project support, crm support, online support management, online support, support product, support services, issue support, fix issue, raise ticket by website, raise support ticket by website, view support request, display support on website, list support on website, helpdesk system for your website, website helpdesk management, submit helpdesk, helpdesk form, Ticket helpdesk, website support ticket, website issue, website project issue, website crm management, website ticket handling,support management, project support, crm support, online support management, online helpdesk, helpdesk product, helpdesk services, issue helpdesk, fix helpdesk, raise ticket by website, raise issue by website, view helpdesk, display helpdesk on website, list helpdesk on website, website customer support Ticket, website support Ticket with timesheet, website support Ticket invoice, website helpdesk Ticket invoice, website support helpdesk Ticket invoice, website helpdesk support Ticket with timesheet, website support tickit, website helpdesk tickit  "
,
    'license':'OPL-1',
    'price': '45',
    'currency': "EUR",
    'data': [
        'security/ir.model.access.csv',
        'data/website.menu.csv',
        'views/support_ticket.xml',
        'views/website_support_templates.xml',
        'views/support_ticket_stage.xml',
        'report/support_ticket_report_view.xml',
    ],
    'demo': [],
    'depends': ['base', 'sale_management', 'project', 'website', 'website_sale','bi_subtask','document','hr_timesheet_attendance'],
    'installable': True,
    "images":['static/description/banner.png'],
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
