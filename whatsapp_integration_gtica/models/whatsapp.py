# -*- coding: utf-8 -*-

import logging
import urllib
import re

from odoo import models, fields, api, _
from odoo.tools import html2plaintext
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class WhatsappDefault(models.Model):
    _name = 'whatsapp.default'
    _description = 'Message default in Whatsapp'

    name = fields.Char(string="Title Template")
    default_messege = fields.Text(string="Message Default")
    category = fields.Selection([ ('partner', 'Partner/Contact'),
                                  ('quote', 'Quoting'),
                                  ('sale', 'Sale'),
                                  ('invoice', 'Invoice'),
                                  ('delivery', 'Delivery'),
                                  ('provider', 'Provider'),
                                  ('other', 'Other'),], default='other', string="Category")

class SendWhatsapp(models.TransientModel):
    _name = 'send.whatsapp'
    _description = 'Send Whatsapp'

    partner_id = fields.Many2one('res.partner', domain="[('parent_id','=',partner_id)]")
    default_messege_id = fields.Many2one('whatsapp.default')

    name = fields.Char(related='partner_id.name',required=True,readonly=True)
    mobile = fields.Char(related='partner_id.mobile',required=True,readonly=True,help="use country mobile code without the + sign")
    format_message = fields.Selection([('txt', 'Text Plan'),
                                 ('link', 'Link Url'),
                                  ], string="Format Message")
    message = fields.Text(string="Message", required=True)
    format_visible_context = fields.Boolean(default=False)

    @api.model
    @api.onchange('partner_id')
    def __onchange_partner_id(self):
        self.format_visible_context = self.env.context.get('format_invisible', False)
        self.mobile = self.partner_id.mobile

    @api.onchange('format_message')
    def _onchange_type(self):

        if self.format_message == 'txt' or self.env.context.get('format_invisible'):
            self.message = self.env.context.get('message_txt', False)
        if self.format_message == 'link':
            self.message = self.env.context.get('message_link', False)

    @api.onchange('default_messege_id')
    def _onchange_message(self):

        message = self.default_messege_id.default_messege
        incluid_name = str(message).format(name =self.partner_id.name)

        if message:
            self.message = incluid_name

    @api.model
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def send_dialog(self,whatsapp_url):
        action = {'type': 'ir.actions.act_url','url': whatsapp_url,'target': 'new', 'res_id': self.id}

    def send_whatsapp(self):

        if not self.mobile:
            raise ValidationError(_("You must add mobil number in the partner form"))
        else:
            movil = self.mobile
            array_int = re.findall("\d+", movil)
            whatsapp_number = ''.join(str(e) for e in array_int)
            pre_format = html2plaintext(self.message)
            messege_prepare = u'{}'.format(pre_format)

            messege_encode = urllib.parse.quote(messege_prepare.encode('utf8'))
            whatsapp_url = 'https://web.whatsapp.com/send?phone={}&text={}'.format(whatsapp_number, messege_encode)

            return {'type': 'ir.actions.act_url',
                'url': whatsapp_url,
                'nodestroy': True,
                'target': 'new',
                'target_type': 'public',
                'res_id': self.id,
                 }
