# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class support_ticket(models.Model):

    _name = "support.ticket"
    _inherit = ['mail.thread']
    
    @api.multi
    def set_to_close(self):
        stage_obj = self.env['support.stage'].search([('name','=','Closed')])
        a = self.write({'stage_id':stage_obj.id,'is_ticket_closed':True,'is_ticket_closed':True,'date_close':datetime.now()})
        return a
        
    @api.multi
    def set_to_reset(self):
        stage_obj = self.env['support.stage'].search([('name','=','New')])
        a = self.write({'stage_id':stage_obj.id,'is_ticket_closed':False})
        return a        
        
    @api.model 
    def default_get(self, flds): 
        result = super(support_ticket, self).default_get(flds)
        stage_nxt1 = self.env['ir.model.data'].xmlid_to_object('bi_website_support_ticket.support_stage') 
        result['stage_id'] = stage_nxt1.id
        result['is_ticket_closed'] = False
        result['is_assign'] = False
        return result
        
    @api.multi
    def stage_find(self):
        return self.env['support.stage'].search([], limit=1).id
            
    @api.multi
    def _get_attachment_count(self):
        for ticket in self:
            attachment_ids = self.env['ir.attachment'].search([('support_ticket_id','=',ticket.id)])
            ticket.attachment_count = len(attachment_ids)
        
    @api.multi
    def attachment_on_support_ticket_button(self):
        self.ensure_one()
        return {
            'name': 'Attachment.Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'ir.attachment',
            'domain': [('support_ticket_id', '=', self.id)],
        }
    
    @api.multi
    def _get_invoice_count(self):
        for ticket in self:
            invoice_ids = self.env['account.invoice'].search([('invoice_support_ticket_id','=',ticket.id)])
            ticket.invoice_count = len(invoice_ids)
            
    @api.multi
    def invoice_button(self):
        self.ensure_one()
        return {
            'name': 'Invoice',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'domain': [('invoice_support_ticket_id', '=', self.id)],
        }
            
    @api.multi
    def _active_ticket(self):
        for s_id in self:
            ticket_ids = self.env['project.task'].search([('ticket_id','=',s_id.id)])
            count = len(ticket_ids)
            s_id.task_count = count
        return
        
    @api.multi
    def task(self):
        ticket = {}
        task_obj = self.env['project.task']
        ticket_ids = task_obj.search([('ticket_id','=',self.id)])
        ticket1 = []
        for ticket_id in ticket_ids:
            ticket1.append(ticket_id.id)
        if ticket_ids:
            ticket = self.env['ir.actions.act_window'].for_xml_id('project', 'action_view_task')
            ticket['domain'] = [('id', 'in', ticket1)]
        return ticket
        
    @api.multi
    def _get_avg_ticket_rating(self):
        for review_obj in self:
            avg_ticket_rating = 0.0
            total_messages = len( [x.id for x in review_obj.reviews_ids if x.message_rate > 0] )
            if total_messages > 0:
                total_rate = sum( [x.message_rate for x in review_obj.reviews_ids] )
                avg_ticket_rating = Decimal( total_rate ) / Decimal( total_messages )
            review_obj.avg_ticket_rating = avg_ticket_rating
            
    @api.onchange('support_team_id')
    def onchange_team_id(self):
        res = {}
        if self.support_team_id:
            res = {'user_id': self.support_team_id.user_id,'team_leader_id':self.support_team_id.team_leader}
        return {'value': res}
        
    @api.multi
    def change_level(self):
        val = {}
        healdesk_team_id = self.support_team_id
        if healdesk_team_id.parent_team_id:
            parent_team = healdesk_team_id.parent_team_id
            val = {
                    'user_id' : parent_team.user_id,
                    'level' : parent_team.level,
                    'parent_team_id' : parent_team.parent_team_id,
                    'team_leader' : parent_team.team_leader
            }
            healdesk_team_id.update(val)
            self.user_id = val['user_id']
            self.team_leader_id = val['team_leader']
        else:
            raise UserError(_('You are already in Parent Team...!!'))
        return 
        
    @api.multi
    def create_invoice(self):
        account_invoice_obj  = self.env['account.invoice']
        account_invoice_line_obj = self.env['account.invoice.line']
        support_invoice_obj = self.env['support.invoice']
        
        if not self.invoice_option:
            raise UserError(_('Please select Invoice Policy...'))
        else:
            res = account_invoice_obj.create({'partner_id': self.partner_id.id,
                                                  'date_invoice': datetime.now(),
                                                  'account_id':self.partner_id.property_account_receivable_id.id,
                                                  'invoice_support_ticket_id' : self.id,
                                             })
                                             
            if self.invoice_option == "manual":
                for inv_line in self.support_invoice_id:
                    res1 = account_invoice_line_obj.create({
                                                             'product_uom': inv_line.uom_id,
                                                             'name': inv_line.name,
                                                             'quantity':inv_line.quantity,
                                                             'price_unit':inv_line.price_unit,
                                                             'account_id': self.partner_id.property_account_receivable_id.id,
                                                             'invoice_id': res.id})
            elif self.invoice_option == "timesheet": 
                if not self.emp_timesheet_cost:
                    raise UserError(_('Please select Timesheet Cost...'))
                else:
                    if not self.timesheet_ids:
                        raise UserError(_('Please Add Employee Timesheet...'))
                    else:
                        if self.emp_timesheet_cost == "employee_cost":
                            for emp_timesheet_id in self.timesheet_ids:
                                res1 = account_invoice_line_obj.create({
                                                                     'product_uom': emp_timesheet_id.product_uom_id,
                                                                     'name': emp_timesheet_id.name,
                                                                     'quantity':emp_timesheet_id.unit_amount,
                                                                     'price_unit':emp_timesheet_id.employee_id.timesheet_cost,
                                                                     'account_id': self.partner_id.property_account_receivable_id.id,
                                                                     'invoice_id': res.id})
                        else:
                            for emp_timesheet_id in self.timesheet_ids:
                                res1 = account_invoice_line_obj.create({
                                                                     'product_uom': emp_timesheet_id.product_uom_id,
                                                                     'name': emp_timesheet_id.name,
                                                                     'quantity':emp_timesheet_id.unit_amount,
                                                                     'price_unit':self.manual_cost,
                                                                     'account_id': self.partner_id.property_account_receivable_id.id,
                                                                     'invoice_id': res.id})
                        
                                                                           
                                             
        return
    
    ''' Website support ticket Field '''
    partner_id = fields.Many2one('res.partner', string="Customer", readonly=True)
    sequence = fields.Char(string='Sequence', readonly=True, default=lambda self: self.env['ir.sequence'].get('support.ticket'))
    id = fields.Integer('ID', readonly=True)
    email_from = fields.Char('Email', size=128, help="Destination email for email gateway.")
    phone = fields.Char('Phone')
    category = fields.Many2one('support.ticket.type',string="Category")
    name = fields.Char('Subject', required=True)
    description = fields.Text('Description')
    priority = fields.Selection([('0','Low'), ('1','Normal'), ('2','High')], 'Priority')
    stage_id = fields.Many2one ('support.stage', 'Stage', track_visibility='onchange', index=True)
    user_id = fields.Many2one('res.users','Responsible')
    tag_ids = fields.Many2many('project.tags', string='Tags')
    support_team_id = fields.Many2one('support.team',string="Helpdesk Team")
    date_create = fields.Datetime(string="Create Date")
    date_close = fields.Datetime(string="Close Date")
    task_ids = fields.Many2one('project.task', string='Tasks')
    task_count =  fields.Integer(compute='_active_ticket',string="Tasks") 
    timesheet_ids = fields.One2many('account.analytic.line', 'ticket_id', 'Timesheets')
    project_id = fields.Many2one('project.project',string="Project")
    analytic_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    is_ticket_closed = fields.Boolean(string="Is Ticket Closed")
    attachment_count  =  fields.Integer('Attachments', compute='_get_attachment_count')
    is_assign = fields.Boolean(string="Is Assign")
    team_leader_id = fields.Many2one('res.users',string="Team Leader")
    customer_rating = fields.Selection([('1','Poor'), ('2','Average'), ('3','Good'),('4','Excellent')], 'Customer Rating')
    comment = fields.Text(string="Comment")
    invoice_option = fields.Selection([('timesheet','Timesheet'),('manual','Manual')],string="Invoice Policy",default="timesheet")
    emp_timesheet_cost = fields.Selection([('employee_cost','Employee Cost'),('manual_cost','Manual Employee Cost')],string="Timesheet Cost",default="employee_cost")
    support_invoice_id = fields.One2many('support.invoice','support_invoice_id',string="Invoice")
    company_id = fields.Many2one('res.company',string="Company")
    manual_cost = fields.Monetary(string="Manual Employee Cost",currency_field='currency_id', default=0.0)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    invoice_count  =  fields.Integer('Invoices', compute='_get_invoice_count')
    

class SupportInvoice(models.Model):
    _name = 'support.invoice'
    
    support_invoice_id = fields.Many2one('support.ticket',string="Support Ticket Invoice")
    #product_id = fields.Char(string="Support Ticket")
    name = fields.Text(string='Description', required=True)
    uom_id = fields.Many2one('product.uom', string='Unit of Measure',ondelete='set null', index=True)
    price_unit = fields.Float(string='Unit Price', required=True)
    quantity = fields.Float(string='Quantity',required=True, default=1)
    invoice_line_tax_ids = fields.Many2many('account.tax',string="Taxes")
    
        
class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    
    ticket_id = fields.Many2one('support.ticket','Support Ticket')
    
class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    ticket_id = fields.Many2one('support.ticket',
        string='Support Ticket',track_visibility='onchange',change_default=True)
        
class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'
    
    ticket_stage = fields.Boolean("Support Ticket Stage")
    
class CrmTeam(models.Model):
    _inherit = 'crm.team'
    
    support_ticket = fields.Boolean("Support Ticket")

class SupportTeam(models.Model):

    _name = "support.team"    
    _rec_name = 'team_id'
    
    team_id = fields.Many2one('crm.team', domain="[('support_ticket', '=', True)]", string="Name")
    user_id = fields.Many2one('res.users',string="Responsible")
    parent_team_id = fields.Many2one('support.team',string="Parent Team")
    team_member = fields.Many2many('res.users','res_user_rel','support_team_id','user_id',string="Team Member")
    #is_team = fields.Boolean(string="Is Default Team")
    level = fields.Selection([('s_level_1','Level 1'),('s_level_2','Level 2'),('s_level_3','Level 3')])
    team_leader = fields.Many2one('res.users',string="Team Leader")

class SupportStage(models.Model):

    _name = "support.stage"    
    
    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', help="Used to order stages. Lower is better.",default=lambda *args: 1)
    fold = fields.Boolean(string="Folded in Form")

    _defaults = {
        'sequence': lambda *args: 1
    }       

class account_invoice(models.Model):
    _inherit='account.invoice'

    invoice_support_ticket_id  =  fields.Many2one('support.ticket', 'Support Ticket')
    
class ir_attachment(models.Model):
    _inherit='ir.attachment'

    support_ticket_id  =  fields.Many2one('support.ticket', 'Support Ticket')

class support_ticket_stage(models.Model):
    _name = "support.ticket.stage"
    _rec_name = 'name'
    _order = "sequence"

    name = fields.Char('Stage Name', required=True)
    sequence = fields.Integer('Sequence', help="Used to order stages. Lower is better.",default=lambda *args: 1)
    team_ids = fields.Many2many('crm.team', 'crm_team_claim_stage_rel', 'stage_id', 'team_id', string='Teams')
    case_default = fields.Boolean('Common to All Teams')

    _defaults = {
        'sequence': lambda *args: 1
    }  

class support_ticket_type(models.Model):
    _name='support.ticket.type'

    name  =  fields.Char('Ticket Name')

class wizard_assign_ticket(models.TransientModel):
    _name = 'wizard.assign.ticket'
    
    user_id = fields.Many2one('res.users', string='Support User', required=True)

    @api.multi
    def assign_ticket(self):
        if self._context.get('active_id'):
            ticket = self.env['support.ticket'].browse(self._context.get('active_id'))
            stage_obj = self.env['support.stage'].search([('name','=','Assigned')])
            ticket.write({'stage_id':stage_obj.id,'is_assign':True})#, 'state_id': 'confirm'
        return {'type': 'ir.actions.act_window_close'}

class Website(models.Model):

    _inherit = "website"
    
    def get_support_team_list(self):            
        support_team_ids=self.env['support.team'].search([])
        return support_team_ids
        
    def get_ticket_details(self):            
        partner_brw = self.env['res.users'].browse(self._uid)
        ticket_ids = self.env['support.ticket'].search([('partner_id','=',partner_brw.partner_id.id)])
        return ticket_ids
        
    def get_ticket_type(self):            
        ticket_type_ids = self.env['support.ticket.type'].search([])
        return ticket_type_ids      

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
