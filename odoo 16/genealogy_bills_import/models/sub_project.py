# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class SubProjects(models.Model):
    _name = 'project.sub.project'

    partner_id = fields.Many2one('res.partner', string="Customer", )
    project_id = fields.Many2one('project.project')
    name = fields.Char(string="Name")
    label_tasks = fields.Char(string="Name of the tasks")
    tag_ids = fields.Many2many('project.tags', string="Tags")
    user_id = fields.Many2one('res.users', string="Project Manager")
    date_start = fields.Date(string="Planed_date")
    company_id = fields.Many2one('res.company', string="Company",
                                 required=True, default=lambda self: self.env.company)
    date = fields.Date(string="Planed_date")
