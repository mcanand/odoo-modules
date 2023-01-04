# Company: giordano.ch AG
# Copyright by: giordano.ch AG
# https://giordano.ch/

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    copyright_year = fields.Char(string="Copyright Year")
