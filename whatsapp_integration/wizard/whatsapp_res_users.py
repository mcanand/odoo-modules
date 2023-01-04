# -*- coding: utf-8 -*-

import logging
import urllib
import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SendWhatsappResUsrs(models.TransientModel):
    _name = 'send.whatsapp.res.users'
    _description = 'Send Whatsapp res users'

    partner_id = fields.Many2one('res.partner', string="partner")
    default_messege_id = fields.Many2one('whatsapp.template', domain="[('category', '=', 'resuser')]")

    name = fields.Char(related='partner_id.name', required=True, readonly=True)
    mobile = fields.Char(related='partner_id.mobile', help="use country mobile code without the + sign")

    message = fields.Text(string="Message")
    format_visible_context = fields.Boolean(default=False)

    @api.model
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.format_visible_context = self.env.context.get('format_invisible', False)
        phone_code = self.partner_id.country_id.phone_code
        self.mobile = str(phone_code) + str(self.partner_id.mobile)

    @api.onchange('default_messege_id')
    def _onchange_message(self):
        res_id = self.env['res.users'].browse(self._context.get('active_id'))
        message = self.default_messege_id.template_messege

        try:
            incluid_name = str(message).format(
                name=res_id.partner_id.name,
                company=res_id.company_id.name,
                website=res_id.company_id.website,
                document_name=res_id.name,
                sign_up_url=res_id.partner_id.signup_url
            )
        except Exception:
            raise ValidationError('Quick replies: parameter not allowed in this template')

        if message:
            self.message = incluid_name

    @api.model
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}

    def send_whatsapp(self):
        partner = self.partner_id
        message = self.message
        message_id = self.default_messege_id
        if partner and message:
            response = self.env['whatsapp.send.message'].send_message(partner, message, message_id)
            # if response:
            #     self.close_dialog()
            # else:
            #     raise ValidationError(_('message send failed please try again'))
