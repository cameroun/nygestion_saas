# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _


class HrDocumentManagement(models.Model):
    _name = "hr.document.management"

    document = fields.Binary("Document", attachment=True)
    name = fields.Char(string="Name")
    employee_id = fields.Many2one('hr.employee', string='Employee')


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    doc_ids = fields.One2many(comodel_name='hr.document.management',
            inverse_name='employee_id', string='Document')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: