# -*- coding: utf-8 -*-

import logging
import urllib
import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)

class SendWhatsappCRM(models.TransientModel):
    _name = 'send.whatsapp.crm'
    _description = 'Send Whatsapp CRM'

    crm_id = fields.Many2one('crm.lead')
    contact_name = fields.Char()
    default_messege_id = fields.Many2one('whatsapp.template', domain="[('category', '=', 'lead')]")

    name = fields.Char(related="crm_id.name", required=True,readonly=True)
    type = fields.Selection(related="crm_id.type", )

    mobile = fields.Char(default=False,help="use country mobile code without the + sign")
    broadcast = fields.Boolean(help="Send a message to several of your contacts at once")

    message = fields.Text(string="Message")
    format_visible_context = fields.Boolean(default=False)

    pricelist_active = fields.Boolean("Activate PriceList", default=False)
    price_list = fields.Many2one('product.pricelist', 'PriceList')

    product_categories_ids = fields.Many2many('product.category')

    qty1 = fields.Integer('Quantity-1', default=1)
    qty2 = fields.Integer('Quantity-2', default=0)
    qty3 = fields.Integer('Quantity-3', default=0)

    @api.onchange('product_categories_ids')
    def _onchange_product_categories_ids(self):
        self.price_list = False
        self.message = False

    @api.onchange('price_list')
    def _onchange_price_list(self):
        if self.price_list:
            crm_id = self.env['crm.lead'].browse(self._context.get('active_id'))
            qty = [self.qty1, self.qty2, self.qty3]

            product_categories_ids = self.product_categories_ids

            if not product_categories_ids:
                self.price_list = False
                raise ValidationError('You must have selected product categories')

            data = self.env['crm.lead'].price_list_report(self.price_list, qty, product_categories_ids)
            list_price = data.replace('\-', '-')
            message = self.env.ref('whatsapp_integration_gtica.data_whatsapp_default_price_list').template_messege

            try:
                incluid_name = str(message).format(
                    name=crm_id.partner_id.name,
                    sales_person=crm_id.user_id.name,
                    company=crm_id.company_id.name,
                    website=crm_id.company_id.website,
                    price_list=list_price
                )
            except Exception:
                raise ValidationError('Quick replies: parameter not allowed in this template')

            if message:
                self.message = incluid_name

    @api.model
    def default_get(self, fields):
        res = super(SendWhatsappCRM, self).default_get(fields)
        active_id = self._context.get('active_id')
        crm_lead = self.env['crm.lead'].browse(active_id)
        mobile = ''

        if crm_lead.type == 'opportunity':
            mobile = crm_lead.partner_id.mobile if crm_lead.partner_id.mobile else crm_lead.partner_id.phone or crm_lead.phone
        if crm_lead.type == 'lead':
            mobile = crm_lead.mobile if crm_lead.mobile else crm_lead.phone

        res.update({
            'crm_id': crm_lead.id,
            'name': crm_lead.name,
            'mobile': mobile,
            'contact_name': crm_lead.partner_id.name if crm_lead.partner_id.name else crm_lead.contact_name,
            })

        return res

    @api.model
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}


    @api.onchange('default_messege_id')
    def _onchange_message(self):

        message = self.default_messege_id.template_messege
        crm_id = self.crm_id
        incluid_name = ''
        try:
            incluid_name = str(message).format(
                name=self.contact_name,
                sales_person=crm_id.user_id.name,
                company=crm_id.company_id.name,
                website=crm_id.company_id.website)
        except Exception:
            raise ValidationError(
                'Quick replies: parameter not allowed in this template, {link_preview} {item_product}')

        if message:
            self.message = incluid_name

    def sending_reset(self):
        crm_lead_id = self.env['crm.lead'].browse(self._context.get('active_id'))
        crm_lead_id.update({
            'send_whatsapp': 'without_sending',
            })
        self.close_dialog()

    def sending_confirmed(self):
        validation = self.env['whatsapp.mixin'].send_validation_broadcast(self.mobile, self.message, self.broadcast)

        if validation:
            self.env['whatsapp.mixin'].sending_confirmed(self.message)
            self.close_dialog()

    def sending_error(self):
        validation = self.env['whatsapp.mixin'].send_validation_broadcast(self.mobile, self.message, self.broadcast)

        if validation:
            self.env['whatsapp.mixin'].sending_error()
            self.close_dialog()

    def send_whatsapp(self):
        validation = self.env['whatsapp.mixin'].send_validation_broadcast(self.mobile, self.message, self.broadcast)

        if validation:
            whatsapp_url = self.env['whatsapp.mixin'].send_whatsapp(self.mobile, self.message, self.broadcast)

            return {'type': 'ir.actions.act_url',
                    'url': whatsapp_url,
                    'name': "whatsapp_action",
                    'target': 'new',
                    }