# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import werkzeug
import json
import base64

import odoo.http as http
from odoo.http import request
from odoo import SUPERUSER_ID
from datetime import datetime, timedelta, time
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import odoo.http as http

class SupportTicket(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(SupportTicket, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        support_ticket = request.env['support.ticket']
        ticket_count = support_ticket.search_count([])

        values.update({
            'ticket_count': ticket_count,
        })
        return values
        
    @http.route(['/my/ticket', '/my/ticket/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_ticket(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        support_ticket = request.env['support.ticket']

        domain = []
        archive_groups = self._get_archive_groups('support.ticket', domain)
        # count for pager
        ticket_count = support_ticket.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/ticket",
            total=ticket_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        supports = support_ticket.search(domain,offset=pager['offset'])
        request.session['my_ticket_history'] = supports.ids[:100]

        values.update({
            'supports': supports.sudo(),
            'page_name': 'ticket',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/ticket',
        })
        return request.render("bi_website_support_ticket.portal_my_ticket", values)
        
        
    @http.route('/support_ticket', type="http", auth="public", website=True)
    def submit_support_ticket(self, **kw):
        """Let's public and registered user submit a support ticket"""
        name = ""
        if http.request.env.user.name != "Public user":
            name = http.request.env.user.name
            
        return http.request.render('bi_website_support_ticket.submit_support_ticket', {'user_ids': name})
    
    @http.route('/support_ticket/thanks', type="http", auth="public", website=True)
    def support_ticket_thanks(self, **post):
        """Displays a thank you page after the user submits a support ticket"""
        
        partner_brw = request.env['res.users'].sudo().browse(request._uid)
        Attachments = request.env['ir.attachment']
        upload_file = post['upload']
        data = upload_file.read()
        
        support_team_obj = request.env['support.team'].sudo().browse(int(post['support_team_id']))
        user_id = support_team_obj.user_id
        team_leader_id = support_team_obj.team_leader
        
        name = post['name']
        description = post['description']
        email_from = post['email_from']
        phone = post['phone']
        category = post['ticket_id']
        priority = post['priority']
        date_create = datetime.now()
        support_team_id = post['support_team_id']
        
        vals = {
                'name':name,
                'description':description,
                'email_from': email_from,
                'phone': phone,
                'category': category,
                'priority' : priority,
                'partner_id': partner_brw.partner_id.id,
                'state' : 'new',
                'date_create' : date_create,
                'support_team_id' : support_team_id,
                'user_id' : support_team_obj.user_id.id,
                'team_leader_id' : support_team_obj.team_leader.id,
                }

        support_ticket_obj = request.env['support.ticket'].sudo().create(vals)
        if upload_file:
            attachment_id = Attachments.sudo().create({
                'name': upload_file.filename,
                'type': 'binary',
                'datas': data.encode('base64'),
                'datas_fname': upload_file.filename,
                'public': True,
                'res_model': 'ir.ui.view',
                'support_ticket_id' : support_ticket_obj.id,
            }) 

        user = request.env['res.users'].sudo().browse(SUPERUSER_ID)
        template_id = request.env['ir.model.data'].get_object_reference(
                                              'bi_website_support_ticket',
                                              'email_template_support_ticket')[1]
        email_template_obj = request.env['mail.template'].sudo().browse(template_id)
        if template_id:
            values = email_template_obj.generate_email(support_ticket_obj.id, fields=None)
            values['email_from'] = user.email
            values['email_to'] = email_from
            values['res_id'] = False
            mail_mail_obj = request.env['mail.mail']
            request.env.uid = 1
            msg_id = mail_mail_obj.sudo().create(values)
            if msg_id:
                mail_mail_obj.send([msg_id])
                
        return request.render("bi_website_support_ticket.support_thank_you")
    
    @http.route('/ticket/view', type="http", auth="user", website=True)
    def ticket_view_list(self, **kw):
        """Displays a list of ticket owned by the logged in user"""
        return http.request.render('bi_website_support_ticket.ticket_view_list')
    
    
    @http.route(['/ticket/view/detail/<model("support.ticket"):ticket>'],type='http',auth="public",website=True)
    def support_ticket_view(self, ticket, category='', search='', **kwargs):
        
        context = dict(request.env.context or {})
        ticket_obj = request.env['support.ticket']
        context.update(active_id=ticket.id)
        ticket_data_list = []
        ticket_data = ticket_obj.browse(int(ticket))
        
        for items in ticket_data:
            ticket_data_list.append(items)
            
        return http.request.render('bi_website_support_ticket.support_ticket_view',{
            'ticket_data_list': ticket
        }) 

    @http.route(['/ticket/message'],type='http',auth="public",website=True)
    def ticket_message(self, **post):
        
        Attachments = request.env['ir.attachment']
        upload_file = post['upload']
        data = upload_file.read()
        
        if ',' in post.get('ticket_id'):
            bcd = post.get('ticket_id').split(',')
        else : 
            bcd = [post.get('ticket_id')]
            
        support_obj = request.env['support.ticket'].sudo().search([('id','=',bcd)])            
            
        if upload_file:
            attachment_id = Attachments.sudo().create({
                'name': upload_file.filename,
                'type': 'binary',
                'datas': data.encode('base64'),
                'datas_fname': upload_file.filename,
                'public': True,
                'res_model': 'ir.ui.view',
                'support_ticket_id' : support_obj.id,
            }) 
        
        context = dict(request.env.context or {})
        ticket_obj = request.env['support.ticket']
        if post.get( 'message' ):
            message_id1 = request.env['support.ticket'].message_post(
                post.get( 'ticket_id' ),
                post.get( 'message' ),
                type='comment',
                subtype='mt_comment') 
                
            message_id1.body = post.get( 'message' )
            message_id1.type = 'comment'
            message_id1.subtype = 'mt_comment'
            message_id1.model = 'support.ticket'
            message_id1.res_id = post.get( 'ticket_id' )
                    
        return http.request.render('bi_website_support_ticket.support_message_thank_you') 
        
    @http.route(['/ticket/comment/<model("support.ticket"):ticket>'],type='http',auth="public",website=True)
    def ticket_comment_page(self, ticket,**post):  
        
        return http.request.render('bi_website_support_ticket.support_ticket_comment',{'ticket': ticket}) 
     
    @http.route(['/support_ticket/comment/send'],type='http',auth="public",website=True)
    def ticket_comment(self, **post):
        
        context = dict(request.env.context or {})
        ticket_obj = request.env['support.ticket'].browse(int(post['ticket_id']))
        ticket_obj.update({
                'customer_rating' : post['customer_rating'],            
                'comment' : post['comment'],
        })
        return http.request.render('bi_website_support_ticket.support_rating_thank_you')         
              
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
