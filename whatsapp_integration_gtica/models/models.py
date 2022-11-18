# -*- coding: utf-8 -*-

import logging

from odoo import http, models, fields, api, _
from odoo.http import request
from odoo.tools import html2plaintext

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    send_whatsapp = fields.Selection([
        ('without_sending', 'without sending'),
        ('sent', 'sent'), ('not_sent', 'no sent'),
        ], default='without_sending')

    def send_whatsapp_step(self):

        return {'type': 'ir.actions.act_window',
                'name': _('Send Whatsapp'),
                'res_model': 'send.whatsapp.purchase',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_partner_id': self.partner_id.id},
                }

    def _action_whatsapp_confirmed(self, message=None):
        self.ensure_one()
        lang = self.env.context.get('lang')

        ctx = {
            'default_model': 'purchase.order',
            'default_res_id': self.ids[0],
            'default_composition_mode': 'comment',
            'mark_so_as_sent': False,
            'mark_whatsapp_sent': True,
            'custom_layout': False,
            'proforma': self.env.context.get('proforma', False),
            'force_email': False,
            }

        subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail_mt_note')
        self.with_context(ctx).message_post(attachment_ids=[], body=message, canned_response_ids=[], channel_ids=[], message_type='notification', partner_ids=[], subtype_xmlid=None, subtype_id=subtype_id)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):

        res = super(PurchaseOrder, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)
        if self.env.context.get('mark_whatsapp_sent'):
           pass

        return res


    def url_link_document(self):

        dominio = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url_preview = self.get_portal_url()
        format_url = '{}{}'.format(dominio, url_preview)

        return format_url

class StockPickig(models.Model):
    _inherit = 'stock.picking'

    send_whatsapp = fields.Selection([
        ('without_sending', 'without sending'),
        ('sent', 'sent'), ('not_sent', 'no sent'),
        ], default='without_sending')

    def send_whatsapp_step(self):

        record = self.with_context(proforma=True)

        result_txt = request.env['ir.ui.view']._render_template("whatsapp_integration_gtica.template_stock_picking", {
            'doc_ids': self.ids,
            'doc_model': 'stock.picking',
            'docs': record,
        })

        message_txt = html2plaintext(result_txt)

        return {'type': 'ir.actions.act_window',
                'name': _('Send Whatsapp'),
                'res_model': 'send.whatsapp.stock',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_partner_id': self.partner_id.id, 'message_txt': message_txt, 'format_invisible': True},
                }

    def _action_whatsapp_confirmed(self, message=None):
        self.ensure_one()
        lang = self.env.context.get('lang')

        ctx = {
            'default_model': 'stock.picking',
            'default_res_id': self.ids[0],
            'default_composition_mode': 'comment',
            'mark_so_as_sent': False,
            'mark_whatsapp_sent': True,
            'force_email': False,
            }

        subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail_mt_note')
        self.with_context(ctx).message_post(attachment_ids=[], body=message, canned_response_ids=[], channel_ids=[],
                                            message_type='notification', partner_ids=[], subtype_xmlid=None,
                                            subtype_id=subtype_id)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):

        res = super(StockPickig, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)
        if self.env.context.get('mark_whatsapp_sent'):
           pass

        return res

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    send_whatsapp = fields.Selection([
        ('without_sending', 'without sending'),
        ('sent', 'sent'), ('not_sent', 'no sent'),
        ], default='without_sending')

    def items_products(self):
        record = self.with_context(proforma=True)
        data = request.env['ir.ui.view']._render_template("whatsapp_integration_gtica.template_products_sale", {
            'doc_ids': self.ids,
            'doc_model': 'sale.order',
            'docs': record,
        })
        pre_format = html2plaintext(data)
        return pre_format

    def url_link_document(self):

        dominio = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url_preview = self.get_portal_url()
        format_url = '{}{}'.format(dominio, url_preview)

        return format_url

    def send_whatsapp_step(self):

        return {'type': 'ir.actions.act_window',
                'name': _('Send Whatsapp'),
                'res_model': 'send.whatsapp.sale',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_partner_id': self.partner_id.id},
                }

    def _action_whatsapp_confirmed(self, message=None):
        self.ensure_one()
        lang = self.env.context.get('lang')

        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_composition_mode': 'comment',
            'mark_so_as_sent': False,
            'mark_whatsapp_sent': True,
            'custom_layout': False,
            'proforma': self.env.context.get('proforma', False),
            'force_email': False,
            'model_description': self.with_context(lang=lang).type_name,
            }

        subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail_mt_note')
        self.with_context(ctx).message_post(attachment_ids=[], body=message, canned_response_ids=[], channel_ids=[],
                                            message_type='notification', partner_ids=[], subtype_xmlid=None,
                                            subtype_id=subtype_id)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):

        res = super(SaleOrder, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)
        if self.env.context.get('mark_whatsapp_sent'):
           pass

        return res

    def price_list_report(self, price_list, qty, product_categories_ids):

        values = self.env['report.whatsapp_product_list'].get_report_values(price_list, qty, product_categories_ids)
        result_pricelist = request.env['ir.ui.view']._render_template("whatsapp_integration_gtica.report_pricelist",
                                                                     values)
        message_price_list = html2plaintext(result_pricelist)
        return message_price_list

class Lead(models.Model):
    _inherit = 'crm.lead'

    send_whatsapp = fields.Selection([
        ('without_sending', 'without sending'),
        ('sent', 'sent'), ('not_sent', 'no sent'),
    ], default='without_sending')

    def send_whatsapp_step(self):

        return {'type': 'ir.actions.act_window',
                'name': _('Send Whatsapp'),
                'res_model': 'send.whatsapp.crm',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {},
                }

    def _action_whatsapp_confirmed(self, message=None):
        self.ensure_one()
        lang = self.env.context.get('lang')

        ctx = {
            'default_model': 'crm.lead',
            'default_res_id': self.ids[0],
            'default_composition_mode': 'comment',
            'mark_so_as_sent': False,
            'mark_whatsapp_sent': True,
            'force_email': False,
            }

        subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail_mt_note')
        self.with_context(ctx).message_post(attachment_ids=[], body=message, canned_response_ids=[], channel_ids=[],
                                            message_type='notification', partner_ids=[], subtype_xmlid=None,
                                            subtype_id=subtype_id)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):

        res = super(Lead, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)
        if self.env.context.get('mark_whatsapp_sent'):
            pass

        return res

    def price_list_report(self, price_list, qty, product_categories_ids):
        values = self.env['report.whatsapp_product_list'].get_report_values(price_list, qty, product_categories_ids)
        result_pricelist = request.env['ir.ui.view']._render_template("whatsapp_integration_gtica.report_pricelist",
                                                                     values)
        message_price_list = html2plaintext(result_pricelist)
        return message_price_list

class ResPartner(models.Model):
    _inherit = 'res.partner'

    send_whatsapp = fields.Selection([
        ('without_sending', 'without sending'),
        ('sent', 'sent'), ('not_sent', 'no sent'),
        ], default='without_sending')

    def send_whatsapp_step(self):

        return {'type': 'ir.actions.act_window',
                'name': _('Send Whatsapp'),
                'res_model': 'send.whatsapp.partner',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_partner_id': self.id, 'format_invisible': True},
                }

    def _action_whatsapp_confirmed(self, message=None):
        self.ensure_one()
        lang = self.env.context.get('lang')

        ctx = {
            'default_model': 'res.partner',
            'default_res_id': self.ids[0],
            'default_composition_mode': 'comment',
            'mark_so_as_sent': False,
            'mark_whatsapp_sent': True,
            'custom_layout': False,
            'proforma': self.env.context.get('proforma', False),
            'force_email': False,
            }

        subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail_mt_note')
        self.with_context(ctx).message_post(attachment_ids=[], body=message, canned_response_ids=[], channel_ids=[],
                                            message_type='notification', partner_ids=[], subtype_xmlid=None,
                                            subtype_id=subtype_id)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):

        res = super(ResPartner, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)
        if self.env.context.get('mark_whatsapp_sent'):
           pass

        return res

    def price_list_report(self, price_list, qty, product_categories_ids):
        values = self.env['report.whatsapp_product_list'].get_report_values(price_list, qty, product_categories_ids)
        result_pricelist = request.env['ir.ui.view']._render_template("whatsapp_integration_gtica.report_pricelist",
                                                                     values)
        message_price_list = html2plaintext(result_pricelist)
        return message_price_list

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def items_products(self):
        record = self.with_context(proforma=True)

        #TODO: verificar losla data que es enviada
        data = request.env['ir.ui.view']._render_template("whatsapp_integration_gtica.template_products_invoice", {
            'doc_ids': self.ids,
            'doc_model': 'account.invoice',
            'docs': record,
        })
        pre_format = html2plaintext(data)
        return pre_format

    def url_link_invoice(self):

        dominio = http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url_preview = self.get_portal_url()
        format_url = '{}{}'.format(dominio, url_preview)

        return format_url

    send_whatsapp = fields.Selection([
        ('without_sending', 'without sending'),
        ('sent', 'sent'), ('not_sent', 'no sent'),
        ], default='without_sending')

    def send_whatsapp_step(self):

        record = self.with_context(proforma=True)

        return {'type': 'ir.actions.act_window',
                'name': _('Send Whatsapp'),
                'res_model': 'send.whatsapp.invoice',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_partner_id': self.partner_id.id,},
                }

    def _action_whatsapp_confirmed(self, message=None):
        self.ensure_one()
        lang = self.env.context.get('lang')

        ctx = {
            'default_model': 'account.move',
            'default_res_id': self.ids[0],
            'default_composition_mode': 'comment',
            'mark_so_as_sent': False,
            'mark_whatsapp_sent': True,
            'force_email': False,
            }

        subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail_mt_note')
        self.with_context(ctx).message_post(attachment_ids=[], body=message, canned_response_ids=[], channel_ids=[],
                                            message_type='notification', partner_ids=[], subtype_xmlid=None,
                                            subtype_id=subtype_id)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):

        res = super(AccountInvoice, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)
        if self.env.context.get('mark_whatsapp_sent'):
           pass

        return res

class account_payment(models.Model):
    _inherit = 'account.payment'

    send_whatsapp = fields.Selection([
        ('without_sending', 'without sending'),
        ('sent', 'sent'), ('not_sent', 'no sent'),
        ], default='without_sending')

    def send_whatsapp_step(self):
        record = self.with_context(proforma=True)
        result_txt = request.env['ir.ui.view']._render_template("whatsapp_integration_gtica.template_payment", {
            'doc_ids': self.ids,
            'doc_model': 'account.payment',
            'docs': record,
            })

        result_link = request.env['ir.ui.view']._render_template(
            "whatsapp_integration_gtica.template_payment_link", {
                'doc_ids': self.ids,
                'doc_model': 'account.payment',
                'docs': record,
                })

        message_txt = html2plaintext(result_txt)
        message_link = html2plaintext(result_link)
        #message_link = str(message_link).format(link=format_url)

        return {'type': 'ir.actions.act_window',
                'name': _('Send Whatsapp'),
                'res_model': 'send.whatsapp.payment',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_partner_id': self.partner_id.id, 'message_txt': message_txt,
                            'message_link': message_link},
                }

    def _action_whatsapp_confirmed(self, message=None):
        self.ensure_one()
        lang = self.env.context.get('lang')

        ctx = {
            'default_model': 'account.payment',
            'default_res_id': self.ids[0],
            'default_composition_mode': 'comment',
            'mark_so_as_sent': False,
            'mark_whatsapp_sent': True,
            'force_email': False,
            }

        subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail_mt_note')
        self.with_context(ctx).message_post(attachment_ids=[], body=message, canned_response_ids=[], channel_ids=[],
                                            message_type='notification', partner_ids=[], subtype_xmlid=None,
                                            subtype_id=subtype_id)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):

        res = super(account_payment, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)
        if self.env.context.get('mark_whatsapp_sent'):
           pass

        return res