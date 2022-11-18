# -*- coding: utf-8 -*-

import logging
import html2text

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools import html2plaintext


_logger = logging.getLogger(__name__)



class SendWhatsappInvoice(models.TransientModel):
    _name = 'send.whatsapp.invoice'
    _description = 'Send Whatsapp Invoice'

    partner_id = fields.Many2one('res.partner', domain="[('parent_id','=',partner_id)]")
    default_messege_id = fields.Many2one('whatsapp.template', domain="[('category', '=', 'invoice')]")

    name = fields.Char(related='partner_id.name', required=True, readonly=True)
    mobile = fields.Char(related='partner_id.mobile', help="use country mobile code without the + sign")

    message = fields.Text(string="Message")
    format_visible_context = fields.Boolean(default=False)

    @api.model
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.format_visible_context = self.env.context.get('format_invisible', False)
        self.mobile = self.partner_id.mobile

    @api.onchange('default_messege_id')
    def _onchange_message(self):
        invoice_id = self.env['account.move'].browse(self._context.get('active_id'))
        message = self.default_messege_id.template_messege
        url_preview = invoice_id.url_link_invoice()
        #TODO:
        items_products = html2plaintext(invoice_id.items_products())


        try:
            incluid_name = str(message).format(
                name=invoice_id.partner_id.name,
                sales_person=invoice_id.user_id.name,
                document_name=invoice_id.name,
                company=invoice_id.company_id.name,
                website=invoice_id.company_id.website,
                link_preview=url_preview,
                item_product=items_products, )

        except Exception:
            raise ValidationError('Quick replies: parameter not allowed in this template')

        if message:
            self.message = incluid_name

    @api.model
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}

    def sending_reset(self):
        invoice_id = self.env['account.move'].browse(self._context.get('active_id'))
        invoice_id.update({
            'send_whatsapp': 'without_sending',
            })
        self.close_dialog()

    def sending_confirmed(self):
        validation = self.env['whatsapp.mixin'].send_validation_broadcast(self.mobile, self.message, False)

        if validation:
            self.env['whatsapp.mixin'].sending_confirmed(self.message)
            self.close_dialog()

    def sending_error(self):
        validation = self.env['whatsapp.mixin'].send_validation_broadcast(self.mobile, self.message, False)

        if validation:
            self.env['whatsapp.mixin'].sending_error()
            self.close_dialog()

    def send_whatsapp(self):
        validation = self.env['whatsapp.mixin'].send_validation_broadcast(self.mobile, self.message, False)

        if validation:
            whatsapp_url = self.env['whatsapp.mixin'].send_whatsapp(self.mobile, self.message, False)

            return {'type': 'ir.actions.act_url',
                    'url': whatsapp_url,
                    'name': "whatsapp_action",
                    'target': 'new',
                    }
