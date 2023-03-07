# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ProjectProjectInherit(models.Model):
    _inherit = 'project.project'

    sub_project_ids = fields.One2many('project.sub.project', 'project_id',
                                      string='Sub Project')
