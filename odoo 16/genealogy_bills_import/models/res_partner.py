# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    psn = fields.Char(string="PSN", required=True)
