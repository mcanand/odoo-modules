# Company: giordano.ch AG
# Copyright by: giordano.ch AG
# https://giordano.ch/

from odoo import fields, models


class MailingContact(models.Model):
    _inherit = "mailing.contact"

    cargo_bike = fields.Boolean(string="Cargo Bikes")
    performance = fields.Boolean(string="Performance")
