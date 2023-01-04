from odoo import models, fields, api, _
import requests
from odoo.exceptions import ValidationError
import base64
from werkzeug.urls import url_encode, url_join
from odoo.http import request


class ResConfigInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    use_facebook = fields.Boolean(string='Use Facebook Account')
    facebook_app_id = fields.Char(string='Facebook App Id')
    facebook_app_secret = fields.Char(string='Facebook App Secret')
    facebook_token_manually = fields.Boolean(string="Enter Token Manually")
    facebook_user_access_token = fields.Char(string='Facebook User Access Token')
    use_instagram = fields.Boolean(string='Use instagram Account')
    instagram_app_id = fields.Char(string='instagram App Id')
    instagram_app_secret = fields.Char(string='instagram App Secret')
    instagram_token_manually = fields.Boolean(string="Enter Token Manually")
    instagram_user_access_token = fields.Char(string='instagram User Access Token')

    def get_values(self):
        res = super(ResConfigInherit, self).get_values()
        config_para = self.env['ir.config_parameter'].sudo()
        res.update(use_facebook=config_para.get_param('social_media_facebook.use_facebook'),
                   facebook_app_id=config_para.get_param('social_media_facebook.facebook_app_id'),
                   facebook_app_secret=config_para.get_param('social_media_facebook.facebook_app_secret'),
                   facebook_token_manually=config_para.get_param('social_media_facebook.facebook_token_manually'),
                   facebook_user_access_token=config_para.get_param('social_media_facebook.facebook_user_access_token'),
                   use_instagram=config_para.get_param('social_media_facebook.use_instagram'),
                   instagram_app_id=config_para.get_param('social_media_facebook.instagram_app_id'),
                   instagram_app_secret=config_para.get_param('social_media_facebook.instagram_app_secret'),
                   instagram_token_manually=config_para.get_param('social_media_facebook.instagram_token_manually'),
                   instagram_user_access_token=config_para.get_param('social_media_facebook.instagram_user_access_token')
                   )
        return res

    def set_values(self):
        super(ResConfigInherit, self).set_values()
        para = self.env['ir.config_parameter'].sudo()
        para.set_param('social_media_facebook.use_facebook',self.use_facebook)
        para.set_param('social_media_facebook.facebook_app_id', self.facebook_app_id)
        para.set_param('social_media_facebook.facebook_app_secret', self.facebook_app_secret)
        para.set_param('social_media_facebook.facebook_token_manually',self.facebook_token_manually)
        para.set_param('social_media_facebook.facebook_user_access_token', self.facebook_user_access_token)
        para.set_param('social_media_facebook.use_instagram', self.use_instagram)
        para.set_param('social_media_facebook.instagram_app_id', self.instagram_app_id)
        para.set_param('social_media_facebook.instagram_app_secret', self.instagram_app_secret)
        para.set_param('social_media_facebook.instagram_token_manually', self.instagram_token_manually)
        para.set_param('social_media_facebook.instagram_user_access_token', self.instagram_user_access_token)

    def action_get_facebook_accounts(self):
        self.get_values()
        self.set_values()
        if not self.facebook_user_access_token:
            raise ValidationError(_('Please Provide Facebook Accesstoken'))
        else:
            response = requests.get(self.env['social.media.types']._facebook_endpoint+"/v7.0/me/accounts",
                                    params={'access_token': self.get_extended_access_token(self.facebook_user_access_token)}).json()
            socialmedia = self.env.ref('social_media_facebook.social_media_facebook')
            if response.get('error'):
                raise ValidationError(response['error']['message'])
            if not response.get('data'):
                return
            account_vals = []
            existing_account = self.get_existing_account(socialmedia, response)
            for account in response['data']:
                account_id = account['id']
                access_token = account['access_token']
                if not existing_account.get(account_id):
                    account_vals.append({
                        'name': account.get('name'),
                        'social_media_id': socialmedia.id,
                        'facebook_account_id': account_id,
                        'facebook_access_token': access_token,
                        'image': self.get_account_image(account_id)
                    })
                else:
                    existing_account.get(account_id).sudo().write({
                        'facebook_access_token': access_token
                    })
            if account_vals:
                self.env['social.media.accounts'].sudo().create(account_vals)
            action = self.env.ref('social_media_base.action_social_media_accounts').read()[0]
            return action

    def get_existing_account(self, socialmedia, response):
        facebook_accounts_ids = [account['id'] for account in response.get('data', [])]
        if facebook_accounts_ids:
            existing_accounts = self.env['social.media.accounts'].search([
                ('social_media_id', '=', int(socialmedia)),
                ('facebook_account_id', 'in', facebook_accounts_ids)
            ])

            return {existing_account.facebook_account_id: existing_account for existing_account in existing_accounts}
        return {}

    def get_account_image(self, account_id):
        image_url = url_join(self.env['social.media.types']._facebook_endpoint,
                                     '/v3.3/%s/picture?height=300' % account_id)
        return base64.b64encode(requests.get(image_url).content)

    def get_extended_access_token(self, access_token):
        facebook_app_id = self.env['ir.config_parameter'].sudo().get_param('social_media_facebook.facebook_app_id')
        facebook_app_secret = self.env['ir.config_parameter'].sudo().get_param(
            'social_media_facebook.facebook_app_secret')
        extended_token_url = url_join(request.env['social.media.types']._facebook_endpoint, "/oauth/access_token")
        extended_token_request = requests.post(extended_token_url, params={
            'client_id': facebook_app_id,
            'client_secret': facebook_app_secret,
            'grant_type': 'fb_exchange_token',
            'fb_exchange_token': access_token
        })
        return extended_token_request.json().get('access_token')

    def action_get_instagram_accounts(self):
        self.get_values()
        self.set_values()
        if not self.instagram_user_access_token:
            raise ValidationError(_('Please Provide Instagram Accesstoken'))
        else:
            media = request.env.ref('social_media_facebook.social_media_instagram')
            accounts_url = url_join(request.env['social.media.types']._instagram_endpoint, "/me/accounts/")
            accounts = requests.get(accounts_url, params={
                'access_token': self._instagram_get_extended_access_token(self.instagram_user_access_token)
            }).json()
            if 'data' not in accounts:
                raise ValidationError(_('Could not find any account to add.'))
            existing_accounts = {
                account_id.instagram_account_id: account_id
                for account_id in request.env['social.media.accounts'].search([
                    ('social_media_id', '=', media.id)])
            }
            accounts_to_create = []
            has_existing_accounts = False
            for account in accounts['data']:
                instagram_account_name = account['name']
                instagram_access_token = account['access_token']
                facebook_account_id = account['id']

                instagram_accounts_endpoint = url_join(
                    request.env['social.media.types']._instagram_endpoint,
                    '/v10.0/%s' % facebook_account_id)

                instagram_account = requests.get(instagram_accounts_endpoint,
                                                 params={
                                                     'fields': 'instagram_business_account,instagram_accounts{username}',
                                                     'access_token': instagram_access_token
                                                 },
                                                 timeout=5
                                                 ).json()
                if 'instagram_business_account' not in instagram_account:
                    continue
                name = ' '.join([n.get('username') for n in  instagram_account['instagram_accounts']['data']])
                try:
                    insta_accnt_id = instagram_account['instagram_accounts']['data'][0].get('id')
                except:
                    pass
                instagram_account_id = instagram_account['instagram_business_account']['id']
                account_values = {
                    'name': name,
                    'instagram_facebook_account_id': facebook_account_id,
                    'instagram_account_id': instagram_account_id,
                    'instagram_access_token': instagram_access_token,
                    # 'image': self._instagram_get_profile_image(insta_accnt_id, instagram_access_token)
                }
                if account_values['instagram_account_id'] in existing_accounts:
                    has_existing_accounts = True
                    # account_values.update({'is_media_disconnected': False})
                    existing_accounts[account_values['instagram_account_id']].sudo().write(account_values)
                else:
                    account_values.update({
                        'social_media_id': media.id,
                    })
                    accounts_to_create.append(account_values)
                    if accounts_to_create:
                        request.env['social.media.accounts'].sudo().create(accounts_to_create)
                    elif not has_existing_accounts:
                        raise ValidationError(_('No Instagram accounts linked with your Facebook page'))

    def _instagram_get_profile_image(self, account_id, instagram_access_token):
        profile_image_url = url_join(
            request.env['social.media.types']._instagram_endpoint,
            '/v10.0/{}?fields=profile_pic&access_token={}' .format(account_id, instagram_access_token))
        return base64.b64encode(requests.get(profile_image_url).content)

    def _instagram_get_extended_access_token(self, access_token):
        instagram_app_id = self.env['ir.config_parameter'].sudo().get_param('social_media_facebook.instagram_app_id')
        instagram_client_secret = self.env['ir.config_parameter'].sudo().get_param(
            'social_media_facebook.instagram_app_secret')
        extended_token_url = url_join(request.env['social.media.types']._instagram_endpoint, "/oauth/access_token")
        extended_token_request = requests.post(extended_token_url,
                                               params={
                                                   'client_id': instagram_app_id,
                                                   'client_secret': instagram_client_secret,
                                                   'fb_exchange_token': access_token,
                                                   'grant_type': 'fb_exchange_token'
                                               },
                                               timeout=5
                                               )
        return extended_token_request.json().get('access_token')

