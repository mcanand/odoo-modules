# -*- coding: utf-8 -*-

import logging
import urllib
import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)



class SendWhatsappPurchase(models.TransientModel):
    _name = 'send.whatsapp.purchase'
    _description = 'Send Whatsapp purchase'

    partner_id = fields.Many2one('res.partner', domain="[('parent_id','=',partner_id)]")
    default_messege_id = fields.Many2one('whatsapp.template', domain="['|', ('category', '=', 'purchase'), ('category', '=', 'provider')]")

    name = fields.Char(related='partner_id.name',required=True,readonly=True)
    mobile = fields.Char(related='partner_id.mobile',help="use country mobile code without the + sign")
    broadcast = fields.Boolean(help="Send a message to several of your contacts at once")

    message = fields.Text(string="Message")
    format_visible_context = fields.Boolean(default=False)

    @api.model
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.format_visible_context = self.env.context.get('format_invisible', False)
        self.mobile = self.partner_id.mobile


    @api.onchange('default_messege_id')
    def _onchange_message(self):
        purchase_order_id = self.env['purchase.order'].browse(self._context.get('active_id'))
        message = self.default_messege_id.template_messege
        url_preview = purchase_order_id.url_link_document()

        incluid_name = ''
        try:
            incluid_name = str(message).format(
                name=purchase_order_id.partner_id.name,
                sales_person=purchase_order_id.user_id.name,
                company=purchase_order_id.company_id.name,
                website=purchase_order_id.company_id.website,
                link_preview=url_preview,
                 )
        except Exception:
            raise ValidationError(
                'Quick replies: parameter not allowed in this template, {link_preview} {item_product}')


        if message:
            self.message = incluid_name

    @api.model
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def send_dialog(self,whatsapp_url):
        action = {'type': 'ir.actions.act_url','url': whatsapp_url,'target': 'new', 'res_id': self.id}

    def sending_reset(self):
        purchase_order_id = self.env['purchase.order'].browse(self._context.get('active_id'))
        purchase_order_id.update({
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
