# -*- coding: utf-8 -*-

import logging
import urllib
import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SendWhatsappSale(models.TransientModel):
    _name = 'send.whatsapp.sale'
    _description = 'Send Whatsapp Sale'

    partner_id = fields.Many2one('res.partner', string="partner")
    default_messege_id = fields.Many2one('whatsapp.template', domain="[('category', '=', 'sale')]")

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
        sale_order_id = self.env['sale.order'].browse(self._context.get('active_id'))
        message = self.default_messege_id.template_messege
        url_preview = sale_order_id.url_link_document()
        items_products = sale_order_id.items_products()

        try:
            incluid_name = str(message).format(
                name=sale_order_id.partner_id.name,
                sales_person=sale_order_id.user_id.name,
                company=sale_order_id.company_id.name,
                website=sale_order_id.company_id.website,
                document_name=sale_order_id.name,
                link_preview=url_preview,
                item_product=items_products,
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
            if response:
                self.close_dialog()
            else:
                raise ValidationError(_('message send failed please try again'))
