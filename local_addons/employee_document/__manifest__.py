# -*- encoding: utf-8 -*-
###########################################################################
#    Copyright (C) 2016 - Turkesh Patel. <http://www.almightycs.com>
#
#    @author Turkesh Patel <info@almightycs.com>
###########################################################################

{
    'name': 'Manage Employee Documents',
    'version': '1.0.1',
    'category': 'Human Resource',
    'author': 'Almighty Consulting Services',
    'support': 'info@almightycs.com',
    'summary': """Document Management System to manage your employee documents and employee will be able to access own documents.
    """,
    'description': """Document Management System to manage your employee documents and employee will be able to access own documents.
    Employee Documents
    Employee Management
    Employee Hiring
    """,
    'website': 'http://www.almightycs.com',
    'depends': ['hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/employee_document_view.xml',
    ],
    'images': [
        'static/description/employee_document_kanban_odoo_almightycs_turkeshpatel.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 22,
    'currency': 'EUR',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
