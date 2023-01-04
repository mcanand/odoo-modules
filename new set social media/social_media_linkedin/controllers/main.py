# -*- coding: utf-8 -*-
import json
import requests
import werkzeug
from werkzeug.urls import url_encode, url_join
from odoo import http, _
from odoo.http import request
from werkzeug.urls import url_encode
from odoo.addons.social_media_base.controllers.main import SocialValidationException


class SocialMediaLinkedin(http.Controller):

    @http.route(['/linkedin/callback'], type='http', auth='user')
    def linkedin_callback(self, access_token=None, code=None, state=None, **kw):
        if kw.get('error'):
            if not access_token and not code:
                return request.render(
                    'social_media_base.social_media_error_view',
                    {'error_message': _('linkedIn did not provide a valid access token.')})

        social_media = request.env.ref('social_media_linkedin.social_media_linkedin')
        if not access_token:
            try:
                access_token = self.get_linkedin_access_token(code, social_media)
            except SocialValidationException as e:
                return request.render('social_media_base.social_media_error_view', {'error_message': str(e)})

        self.create_linkedin_accounts(access_token, social_media)

        url_params = {
            'action': request.env.ref('social_media_base.action_social_media_accounts').id,
            'view_type': 'kanban',
            'model': 'social.media.accounts',
        }
        return werkzeug.utils.redirect('/web?#%s' % url_encode(url_params))

    def create_linkedin_accounts(self, access_token, social_media):
        linkedin_accounts = request.env['social.media.accounts'].fetch_linkedin_accounts(access_token)
        social_media_accounts = request.env['social.media.accounts'].sudo().search([
            ('social_media_id', '=', social_media.id),
            ('linkedin_account_urn', 'in', [l.get('linkedin_account_urn') for l in linkedin_accounts])])
        existing_accounts = {
            account.linkedin_account_urn: account
            for account in social_media_accounts
            if account.linkedin_account_urn
        }
        accounts_to_create = []
        for account in linkedin_accounts:
            if account['linkedin_account_urn'] in existing_accounts:
                existing_accounts[account['linkedin_account_urn']].sudo().write({
                    'linkedin_access_token': account.get('linkedin_access_token'),
                    'image': account.get('image')
                })
            else:
                account.update({'social_media_id': social_media.id})
                accounts_to_create.append(account)

        request.env['social.media.accounts'].sudo().create(accounts_to_create)

    def get_linkedin_access_token(self, code, media):
        linkedin_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        linkedin_app_id = request.env['ir.config_parameter'].sudo().get_param('social_media_linkedin.linkedin_app_id')
        linkedin_client_secret = request.env['ir.config_parameter'].sudo().get_param('social_media_linkedin.linkedin_app_secret')

        params = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': url_join(request.env['ir.config_parameter'].sudo().get_param('web.base.url'),'linkedin/callback'),
            'client_id': linkedin_app_id,
            'client_secret': linkedin_client_secret
        }
        response = requests.post(linkedin_url, data=params).json()
        error_description = response.get('error_description')
        if error_description:
            raise SocialValidationException(error_description)
        return response.get('access_token')
