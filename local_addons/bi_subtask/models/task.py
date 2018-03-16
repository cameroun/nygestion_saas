# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from openerp.osv import osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import api, fields, models, _
from openerp.exceptions import UserError,Warning

class res_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    warning_child_task = fields.Many2one('project.task.type','Prevent stage to change untill all task on same stage')

    @api.model
    def default_get(self, fields_list):
        res = super(res_config_settings, self).default_get(fields_list)
        stage_id = self.search([], limit=1, order="id desc").warning_child_task
        res.update({'warning_child_task':stage_id.id,
                    })
            
        return res


#class project_task(models.Model):
#    _inherit = 'project.task'

#    @api.multi
#    def write(self, vals):
#        if vals.get('stage_id'):
#            task_type_search = self.env['project.config.settings'].search([], limit=1, order="id desc").warning_child_task
#            if task_type_search:
#                if vals.get('stage_id') == task_type_search.id:
#                    for task in  self.subtask_ids:
#                        if task.stage_id.id != task_type_search.id:
#                            raise Warning("You can not close parent task until all child tasks are closed.")
 #       return super(project_task, self).write(vals)

class subtask_wizard(models.Model):
    _name= 'subtask.wizard'

    subtask_lines = fields.One2many('project.task','wiz_id',string="Task Line")

    @api.multi
    def create_subtask(self):
        list_of_stage = [] 
        project_id = self.env['project.task'].browse(self._context.get('active_id'))
        for stage in project_id.project_id.type_ids:
            stage_ids = self.env['project.task.type'].search([('id','=',stage.id)])
            list_of_stage.append(stage_ids.id)
        for task in self.subtask_lines:
            task.task_parent_id = self._context.get('active_id') 
            task.description = task.des
            task.stage_id = list_of_stage[0]
            task.project_id = project_id.project_id.id
        return True
        
            
class ProjectTask(models.Model):
    _inherit = "project.task"

    wiz_id = fields.Many2one('subtask.wizard',string="Wiz Parent Id")
    task_parent_id = fields.Many2one('project.task',string="Parent Id")
    subtask_ids = fields.One2many('project.task','task_parent_id',string="Subtask")
    des = fields.Char('Description')
    
