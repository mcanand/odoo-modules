from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from werkzeug.urls import url_join, url_quote
import requests
import uuid
import time
import base64
import hmac
import hashlib


class SocialMediaTypeInherit(models.Model):
    _inherit = 'social.media.types'

    _twitter_endpoint = 'https://api.twitter.com'
    social_media_types = fields.Selection(selection_add=[('twitter','Twitter')])

    def action_get_accounts(self):
        if self.social_media_types == 'twitter':
            client_id = self.env['ir.config_parameter'].get_param('social_media_twitter.twitter_app_id')
            client_secret = self.env['ir.config_parameter'].get_param('social_media_twitter.twitter_app_secret')
            if client_id and client_secret:
                return self.twitter_account_config()
            raise ValidationError(_('Provide Twitter ClientID and client Secret'))
        return super(SocialMediaTypeInherit, self).action_get_accounts()

    def twitter_account_config(self):
        twitter_url = url_join(self._twitter_endpoint, "oauth/request_token")

        headers = self.twitter_header()
        r = requests.post(twitter_url, headers=headers)
        if r.status_code != 200:
            raise ValidationError(_(r.text))
        values = {val.split('=')[0]: val.split('=')[1]for val in r.text.split('&')}
        twitter_authorize = url_join(self._twitter_endpoint, 'oauth/authorize')
        return {
            'name': 'Add Account',
            'type': 'ir.actions.act_url',
            'url': twitter_authorize + '?oauth_token=' + values['oauth_token'],
            'target': 'self'
        }

    def twitter_header(self):
        twitter_app_id = self.env['ir.config_parameter'].sudo().get_param('social_media_twitter.twitter_app_id')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = url_join(self._twitter_endpoint, "oauth/request_token")
        method = 'POST'
        header_params = {
            'oauth_nonce': uuid.uuid4(),
            'oauth_consumer_key': twitter_app_id,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_version': '1.0',
            'oauth_callback': url_join(base_url, "twitter/callback")
        }
        sig_param = {}
        sig_param.update(header_params)
        header_params['oauth_signature'] = self.get_oauth_signature(method,url,sig_param,oauth_token_secret='')
        header_oauth = 'OAuth ' + ', '.join([('%s="%s"' % (key, url_quote(header_params[key], unsafe='+:/'))) for key in sorted(header_params.keys())])
        return {'Authorization': header_oauth}

    def get_oauth_signature(self, method, url, params, oauth_token_secret):
        twitter_app_secret = self.env['ir.config_parameter'].sudo().get_param('social_media_twitter.twitter_app_secret')
        if twitter_app_secret:
            sign_key = '&'.join([twitter_app_secret, oauth_token_secret])
            basestring = '&'.join([method,url_quote(url, unsafe='+:/'),url_quote('&'.join([
                    ('%s=%s' % (url_quote(key, unsafe='+:/'), url_quote(params[key], unsafe='+:/')))
                    for key in sorted(params.keys())
                ]), unsafe='+:/')
            ])

            sign = hmac.new(bytes(sign_key, 'utf-8'), bytes(basestring, 'utf-8'), hashlib.sha1).digest()
            return base64.b64encode(sign).decode('ascii')