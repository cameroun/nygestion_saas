# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Project And Task PDF Report',
    'version' : '1.0',
    'price' : 10.0,
    'currency': 'EUR',
    'category': 'Project Management',
    'summary' : 'Print Project and Task Report',
    'description': """
                Project Report:
                    - Creating Project Task Report
Tags: 
Project report
task report
project task report
            """,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'depends' : ['project','hr_timesheet'],
    'data' : ['report/report_reg.xml',
              'report/project_report.xml',
              'report/task_report.xml'],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
