# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import requests
import json
from odoo.exceptions import ValidationError


class WhatsappMessageSend(models.Model):
    _name = 'whatsapp.send.message'
    _description = 'send message'

    partner_id = fields.Many2one('res.partner')
    message = fields.Char(string='message')
    state = fields.Selection([('done', 'Done'), ('cancel', 'Failed')])
    category = fields.Many2one('whatsapp.template', string="Category")

    def get_parameters(self):
        config_parameter = self.env['ir.config_parameter'].sudo()
        params = {'host_url': config_parameter.get_param('whatsapp_integration.host_url'),
                  'version': config_parameter.get_param('whatsapp_integration.api_version'),
                  'number_id': config_parameter.get_param('whatsapp_integration.phone_number'),
                  'token': config_parameter.get_param('whatsapp_integration.auth_token')}
        return params

    def get_api_url(self):
        parameters = self.get_parameters()
        api_url = parameters.get('host_url') + "v" + parameters.get('version') + "/" + parameters.get(
            'number_id') + "/messages"
        return api_url

    def prepare_header(self):
        api_header = {'Content-Type': 'application/json',
                      'Authorization': 'Bearer %s' % self.get_parameters().get('token'),
                      'Accept': 'application/json'}
        return api_header

    def prepare_wa_value(self, partner, message):
        if partner.mobile:
            phone_code = partner.country_id.phone_code
            mob_num = str(phone_code) + str(partner.mobile)
            prepare_value = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": mob_num,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            return self.prepare_json(prepare_value)
        else:
            raise ValidationError(_("partner mobile number is missing"))

    def prepare_json(self, val):
        data = json.dumps(val)
        return data

    def send_message(self, partner, message, message_id):
        response = requests.post(url=self.get_api_url(),
                                 headers=self.prepare_header(),
                                 data=self.prepare_wa_value(partner, message))
        if response.status_code == 200:
            vals = {'partner_id': partner.id,
                    'message': message,
                    'state': 'done',
                    'category': message_id.id if message_id else ""}
            self.sudo().create(vals)
        else:
            vals = {'partner_id': partner.id,
                    'message': message,
                    'state': 'cancel',
                    'category': message_id.id if message_id else ""}
            self.sudo().create(vals)
