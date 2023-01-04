import base64
import json

import requests
import werkzeug
from werkzeug.urls import url_encode, url_join

from odoo import http, _
from odoo.http import request
from odoo.addons.social_media_base.controllers.main import SocialValidationException


class SocialMediaTwitter(http.Controller):

    @http.route('/twitter/callback', type='http', auth='user')
    def twitter_callback(self, oauth_token=None, oauth_verifier=None, **kw):
        if not kw.get('denied'):
            if not oauth_token or not oauth_verifier:
                return request.render(
                    'social_media_base.social_media_error_view',
                    {'error_message': _('linkedIn did not provide a valid access token.')})
            social_media = request.env.ref('social_media_twitter.social_media_twitter')
            try:
                self.create_twitter_accounts(oauth_token, oauth_verifier, social_media)
            except SocialValidationException as e:
                return request.render('social.social_http_error_view',
                                      {'error_message': str(e)})
        url_params = {
            'action': request.env.ref('social_media_base.action_social_media_accounts').id,
            'view_type': 'kanban',
            'model': 'social.media.accounts'}
        url = '/web?#%s' % url_encode(url_params)
        return werkzeug.utils.redirect(url)

    def create_twitter_accounts(self, oauth_token, oauth_verifier, social_media):
        twitter_client_id = request.env['ir.config_parameter'].sudo().get_param('social_media_twitter.twitter_app_id')
        twitter_access_token_url = url_join(request.env['social.media.types']._twitter_endpoint, "oauth/access_token")
        r = requests.post(twitter_access_token_url, data={
            'oauth_consumer_key': twitter_client_id,
            'oauth_token': oauth_token,
            'oauth_verifier': oauth_verifier})
        if r.status_code != 200:
            raise SocialValidationException(_('Twitter did not provide a valid access token or it may have expired.'))
        values = {val.split('=')[0]: val.split('=')[1]for val in r.text.split('&')}
        existing_account = request.env['social.media.accounts'].sudo().search([
            ('social_media_id', '=', social_media.id),
            ('twitter_account_id', '=', values['user_id'])])

        if existing_account:
            return existing_account.write({
                'twitter_display_name': values['screen_name'],
                'twitter_access_token': values['oauth_token'],
                'twitter_token_secret': values['oauth_token_secret']
            })
        else:
            return request.env['social.media.accounts'].sudo().create({
                'social_media_id': social_media.id,
                'name': values['screen_name'],
                'twitter_account_id': values['user_id'],
                'twitter_display_name': values['screen_name'],
                'twitter_access_token': values['oauth_token'],
                'twitter_token_secret': values['oauth_token_secret']})