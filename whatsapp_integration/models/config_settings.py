from odoo import api, fields, models, _
import string
import requests
from odoo.http import request


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    app_id = fields.Char(string="App Id", readonly=False, required=True)
    app_secret = fields.Char(string="App Secret", readonly=False, required=True)
    host_url = fields.Char(string="Host Url", default="https://graph.facebook.com/")
    auth_token = fields.Char(string="AuthToken")
    api_version = fields.Char(string="API Version", required=True)
    phone_number = fields.Char(string="Number ID", required=True)



    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(app_id=self.env['ir.config_parameter'].sudo().get_param('whatsapp_integration.app_id'))
        res.update(app_secret=self.env['ir.config_parameter'].sudo().get_param('whatsapp_integration.app_secret'))
        res.update(host_url=self.env['ir.config_parameter'].sudo().get_param('whatsapp_integration.host_url'))
        res.update(auth_token=self.env['ir.config_parameter'].sudo().get_param('whatsapp_integration.auth_token'))
        res.update(api_version=self.env['ir.config_parameter'].sudo().get_param('whatsapp_integration.api_version'))
        res.update(phone_number=self.env['ir.config_parameter'].sudo().get_param('whatsapp_integration.phone_number'))
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        app_id = self.app_id
        app_secret = self.app_secret
        host_url = self.host_url
        auth_token = self.auth_token
        api_version = self.api_version
        phone_number = self.phone_number
        param.set_param('whatsapp_integration.app_id', app_id)
        param.set_param('whatsapp_integration.app_secret', app_secret)
        param.set_param('whatsapp_integration.host_url', host_url)
        param.set_param('whatsapp_integration.auth_token', auth_token)
        param.set_param('whatsapp_integration.api_version', api_version)
        param.set_param('whatsapp_integration.phone_number', phone_number)














    def action_confirm(self):
        res = super(EventRegistration, self).action_confirm()
        recepient = self.mobile
        message = "Hi,","+", self.partner_id.name + "Your registration is successfully completed"
        self.send_text_message(recepient,message)
        return res

    def send_text_message(self, recipient, message,retry=0):
        graph_host_url = self.env['ir.config_parameter'].sudo().get_param('whatsapp_integration.host_url')
        api_version = self.env['ir.config_parameter'].sudo().get_param('whatsapp_integration.api_version')
        phone_number_id = self.env['ir.config_parameter'].sudo().get_param('whatsapp_integration.phone_number')
        token = self.env['ir.config_parameter'].sudo().get_param('whatsapp_integration.auth_token')
        api_url = graph_host_url + "/" + api_version + "/" + phone_number_id + "/messages"
        api_header = {'Content-Type': 'application/json',
                      'Authorization': 'Bearer %s' %token,
                      'Accept': 'application/json'}
        body = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        print("api url",api_url)
        print("api header",api_header)
        response = requests.post(url=api_url, headers=api_header, data=json.dumps(body))
        print("resssss",response)
        if retry != 4:
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                retry += 1
                self.get_auth_token()
        else:
            return False
