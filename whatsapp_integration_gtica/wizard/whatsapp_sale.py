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

    partner_id = fields.Many2one('res.partner', domain="[('parent_id','=',partner_id)]")
    default_messege_id = fields.Many2one('whatsapp.template', domain="[('category', '=', 'sale')]")

    name = fields.Char(related='partner_id.name', required=True, readonly=True)
    mobile = fields.Char(related='partner_id.mobile', help="use country mobile code without the + sign")
    broadcast = fields.Boolean(help="Send a message to several of your contacts at once")

    message = fields.Text(string="Message")
    format_visible_context = fields.Boolean(default=False)

    pricelist_active = fields.Boolean("Activate PriceList", default=False)
    price_list = fields.Many2one('product.pricelist', 'PriceList', )

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
            sale_order_id = self.env['sale.order'].browse(self._context.get('active_id'))
            qty = [self.qty1, self.qty2, self.qty3]

            product_categories_ids = self.product_categories_ids

            if not product_categories_ids:
                self.price_list = False
                raise ValidationError('You must have selected product categories')

            data = self.env['sale.order'].price_list_report(self.price_list, qty, product_categories_ids)

            list_price = data.replace('\-', '-')
            message = self.env.ref('whatsapp_integration_gtica.data_whatsapp_default_price_list').template_messege

            try:
                incluid_name = str(message).format(
                    name=sale_order_id.partner_id.name,
                    sales_person=sale_order_id.user_id.name,
                    company=sale_order_id.company_id.name,
                    website=sale_order_id.company_id.website,
                    price_list=list_price
                )
            except Exception:
                raise ValidationError('Quick replies: parameter not allowed in this template')

            if message:
                self.message = incluid_name

    @api.model
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.format_visible_context = self.env.context.get('format_invisible', False)
        self.mobile = self.partner_id.mobile

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

    def sending_reset(self):
        sale_order_id = self.env['sale.order'].browse(self._context.get('active_id'))
        sale_order_id.update({
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
