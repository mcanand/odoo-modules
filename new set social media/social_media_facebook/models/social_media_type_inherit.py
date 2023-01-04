from odoo import models, fields, api, _
from werkzeug.urls import url_encode, url_join
from odoo.exceptions import UserError, ValidationError


class SocialMediaFacebook(models.Model):
    _inherit = 'social.media.types'

    _facebook_endpoint = 'https://graph.facebook.com'
    _instagram_endpoint = 'https://graph.facebook.com'
    social_media_types = fields.Selection(selection_add=[('facebook', 'Facebook'),
                                                         ('instagram','Instagram')])

    def action_get_accounts(self):
        self.ensure_one()
        if self.social_media_types == 'facebook':
            facebook_app_id = self.env['ir.config_parameter'].sudo().get_param('social_media_facebook.facebook_app_id')
            facebook_app_secret = self.env['ir.config_parameter'].sudo().get_param('social_media_facebook.facebook_app_secret')
            if facebook_app_id and facebook_app_secret:
                return self.configure_facebook_account(facebook_app_id)
            raise ValidationError(_('Facebook AppID and App secret are not Provided'))
        if self.social_media_types == 'instagram':
            instagram_app_id = self.env['ir.config_parameter'].sudo().get_param('social_media_facebook.instagram_app_id')
            instagram_app_secret = self.env['ir.config_parameter'].sudo().get_param('social_media_facebook.instagram_app_secret')
            if instagram_app_id and instagram_app_secret:
                return self.configure_instagram_account(instagram_app_id)
            raise ValidationError(_('Instagram AppID and App secret are not Provided'))
        return super(SocialMediaFacebook, self).action_get_accounts()

    def configure_instagram_account(self, appid):
        base_url = self.get_base_url()
        base_instagram_url = 'https://www.facebook.com/v10.0/dialog/oauth?%s'

        params = {
            'client_id': appid,
            'redirect_uri': url_join(base_url, "instagram/callback"),
            'response_type': 'token',
            'state': self.csrf_token,
            'scope': ','.join([
                'instagram_basic',
                'instagram_content_publish',
                'instagram_manage_comments',
                'instagram_manage_insights',
                'pages_show_list',
                'pages_manage_ads',
                'pages_manage_metadata',
                'pages_read_engagement',
                'pages_read_user_content',
                'pages_manage_engagement',
                'pages_manage_posts',
                'read_insights'
            ])
        }

        return {
            'type': 'ir.actions.act_url',
            'url': base_instagram_url % url_encode(params),
            'target': 'self'
        }

    def configure_facebook_account(self, appid):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        facebook_url = 'https://www.facebook.com/v13.0/dialog/oauth?%s'
        params = {
            'client_id': appid,
            'redirect_uri': url_join(base_url, "facebook/callback"),
            'response_type': 'token',
            'scope': 'leads_retrieval,pages_manage_ads,pages_read_engagement,ads_management'}
        return {
            'type': 'ir.actions.act_url',
            'url': facebook_url % url_encode(params),
            'target': 'self'
        }
