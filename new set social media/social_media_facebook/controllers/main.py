from odoo import http, _
from odoo.http import request
import werkzeug
from werkzeug.urls import url_encode, url_join
from odoo.addons.social_media_base.controllers.main import SocialValidationException
from werkzeug.exceptions import Forbidden
from odoo.addons.web.controllers.main import Binary
import requests
import base64
import functools


def fragment_to_query_string(func):
    @functools.wraps(func)
    def wrapper(self, *a, **kw):
        kw.pop('debug', False)
        if not kw:
            return """<html><head><script>
                var l = window.location;
                var q = l.hash.substring(1);
                var r = l.pathname + l.search;
                if(q.length !== 0) {
                    var s = l.search ? (l.search === '?' ? '' : '&') : '?';
                    r = l.pathname + l.search + s + q;
                }
                if (r == l.pathname) {
                    r = '/';
                }
                window.location = r;
            </script></head><body></body></html>"""
        return func(self, *a, **kw)

    return wrapper


class OAuthFacebookController(http.Controller):

    @http.route('/facebook/callback', type='http', auth='user')
    @fragment_to_query_string
    def facebook_authentication_callback(self, access_token=None, is_extended_token=False, **kw):
        if kw.get('error') != 'access_denied':
            if not access_token:
                return request.render(
                    'social_media_base.social_media_error_view',
                    {'error_message': _('Facebook did not provide a valid access token.')})
            socialmedia = request.env.ref('social_media_facebook.social_media_facebook')
            try:
                self.create_facebook_accounts(access_token, socialmedia, is_extended_token)
            except SocialValidationException as e:
                return request.render('social_media_base.social_media_error_view', {'error_message': str(e)})

        url_params = {
            'action': request.env.ref('social_media_base.action_social_media_accounts').id,
            'view_type': 'kanban',
            'model': 'social.media.accounts',
        }

        url = '/web?#%s' % url_encode(url_params)
        return werkzeug.utils.redirect(url)

    def create_facebook_accounts(self, access_token, socialmedia, is_extended_token):
        extended_access_token = access_token if is_extended_token else self.get_extended_access_token(access_token)

        account_url = url_join(request.env['social.media.types']._facebook_endpoint, "/me/accounts/")
        response = requests.get(account_url, params={
            'access_token': extended_access_token}).json()
        if 'data' in response:
            account_vals = []
            existing_account = self.get_existing_account(socialmedia, response)
            for account in response['data']:
                account_id = account['id']
                access_token = account['access_token']
                if not existing_account.get(account_id):
                    account_vals.append({
                        'name': account.get('name'),
                        'social_media_id':socialmedia.id,
                        'facebook_account_id':account_id,
                        'facebook_access_token':access_token,
                        'image': self.get_account_image(account_id)
                    })
                else:
                    existing_account.get(account_id).sudo().write({
                        'facebook_access_token': access_token
                    })
        else:
            raise SocialValidationException(_('Facebook did not provide a valid access token.'))
        if account_vals:
            request.env['social.media.accounts'].sudo().create(account_vals)

    def get_existing_account(self, socialmedia, response):
        facebook_accounts_ids = [account['id'] for account in response.get('data', [])]
        if facebook_accounts_ids:
            existing_accounts = request.env['social.media.accounts'].search([
                ('social_media_id', '=', int(socialmedia)),
                ('facebook_account_id', 'in', facebook_accounts_ids)
            ])

            return {existing_account.facebook_account_id: existing_account for existing_account in existing_accounts}
        return {}

    def get_extended_access_token(self, access_token):
        facebook_app_id = request.env['ir.config_parameter'].sudo().get_param('social_media_facebook.facebook_app_id')
        facebook_app_secret = request.env['ir.config_parameter'].sudo().get_param('social_media_facebook.facebook_app_secret')
        extended_token_url = url_join(request.env['social.media.types']._facebook_endpoint, "/oauth/access_token")
        extended_token_request = requests.post(extended_token_url, params={
            'client_id': facebook_app_id,
            'client_secret': facebook_app_secret,
            'grant_type': 'fb_exchange_token',
            'fb_exchange_token': access_token
        })
        return extended_token_request.json().get('access_token')

    def get_account_image(self, account_id):
        image_url = url_join(request.env['social.media.types']._facebook_endpoint,
                                     '/v3.3/%s/picture?height=300' % account_id)
        return base64.b64encode(requests.get(image_url).content)


class OAuthInstagramController(http.Controller):

    @http.route('/instagram/callback', type='http', auth='user')
    @fragment_to_query_string
    def instagram_authentication_callback(self, access_token=None, extended_access_token=None, **kw):
        print("-----------------debug--------------------------")
        if kw.get('error') != 'access_denied':
            if not access_token:
                return request.render(
                    'social_media_base.social_media_error_view',
                    {'error_message': _('Instagram did not provide a valid Code.')})
            socialmedia = request.env.ref('social_media_facebook.social_media_instagram')
            try:
                self.create_instagram_accounts(access_token, extended_access_token)
            except SocialValidationException as e:
                return request.render('social_media_base.social_media_error_view', {'error_message': str(e)})

        url_params = {
            'action': request.env.ref('social_media_base.action_social_media_accounts').id,
            'view_type': 'kanban',
            'model': 'social.media.accounts',
        }

        url = '/web?#%s' % url_encode(url_params)
        return werkzeug.utils.redirect(url)

    def create_instagram_accounts(self, access_token, extended_access_token):
        account_url = url_join(request.env['social.media.types']._instagram_endpoint, "/me/accounts/")
        media = request.env.ref('social_media_facebook.social_media_instagram')
        accounts = requests.get(account_url, params={
            'access_token': extended_access_token or self._instagram_get_extended_access_token(access_token, media)
        }).json()
        if 'data' not in accounts:
            raise SocialValidationException(_('Could not find any account to add.'))
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
                                                 'fields': 'instagram_business_account',
                                                 'access_token': instagram_access_token
                                             },
                                             timeout=5
                                             ).json()
            if 'instagram_business_account' not in instagram_account:
                continue

            instagram_account_id = instagram_account['instagram_business_account']['id']
            account_values = {
                'name': instagram_account_name,
                'instagram_facebook_account_id': facebook_account_id,
                'instagram_account_id': instagram_account_id,
                'instagram_access_token': instagram_access_token,
                'image': self._instagram_get_profile_image(facebook_account_id)
            }
            if account_values['instagram_account_id'] in existing_accounts:
                has_existing_accounts = True
                account_values.update({'is_media_disconnected': False})
                existing_accounts[account_values['instagram_account_id']].write(account_values)
            else:
                account_values.update({
                    'social_media_id': media.id,
                })
                accounts_to_create.append(account_values)
                if accounts_to_create:
                    request.env['social.media.accounts'].sudo().create(accounts_to_create)
                elif not has_existing_accounts:
                    raise SocialValidationException(_('No Instagram accounts linked with your Facebook page'))

    def _instagram_get_profile_image(self, account_id):
        profile_image_url = url_join(
            request.env['social.media.types']._instagram_endpoint,
            '/v10.0/%s/picture?height=300' % account_id)
        return base64.b64encode(requests.get(profile_image_url, timeout=10).content)


    def exchange_code_for_accesstoken(self, code):
        instagram_app_id = request.env['ir.config_parameter'].sudo().get_param('social_media_facebook.instagram_app_id')
        instagram_app_secret = request.env['ir.config_parameter'].sudo().get_param('social_media_facebook.instagram_app_secret')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        in_values = {'client_id':instagram_app_id,
                     'client_secret':instagram_app_secret,
                     'grant_type':'authorization_code',
                     # 'redirect_uri': "https://5125-202-88-234-48.ngrok.io/instagram/callback",
                     'redirect_uri':url_join(base_url, "instagram/callback"),
                     'code':code }
        access_token_request = requests.post("https://api.instagram.com/oauth/access_token?", data = in_values).json()
        longlived_accesstoken = self.get_long_lived_accesstoke(instagram_app_secret, access_token_request.get('access_token'))
        return longlived_accesstoken

    def _instagram_get_extended_access_token(self, access_token, media):
        instagram_app_id = request.env['ir.config_parameter'].sudo().get_param('social_media_facebook.instagram_app_id')
        instagram_client_secret = request.env['ir.config_parameter'].sudo().get_param('social_media_facebook.instagram_app_secret')
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

    @http.route(['/social_media_instagram/<string:post_id>/get_image'], type='http', auth='public')
    def social_post_instagram_image(self, post_id):
        print(post_id)
        social_post = request.env['social.media.post'].sudo().search([('id', '=', int(post_id))])

        status, headers, image_base64 = request.env['ir.http'].sudo().binary_content(
            id=social_post.image_ids.id,
            default_mimetype='image/jpeg'
        )

        return Binary._content_image_get_response(status, headers, image_base64)
