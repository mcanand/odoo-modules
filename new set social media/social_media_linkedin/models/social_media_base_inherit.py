from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from werkzeug.urls import url_encode, url_join
import string
import random


class SocialMediaType(models.Model):
    _inherit = 'social.media.types'

    _linkedin_endpoint = 'https://api.linkedin.com/v2/'
    _linkedin_organisation_protection = 'localizedName,vanityName,logoV2(original~:playableStreams)'

    social_media_types = fields.Selection(selection_add=[('linkedin', 'LinkedIn')])
    csrf_token = fields.Char()

    def action_get_accounts(self):
        if self.social_media_types == 'linkedin':
            linkedin_app_id = self.env['ir.config_parameter'].get_param('social_media_linkedin.linkedin_app_id')
            linkedin_app_secret = self.env['ir.config_parameter'].get_param('social_media_linkedin.linkedin_app_secret')
            if linkedin_app_id and linkedin_app_secret:
                return self.get_linkedin_oauth_code(linkedin_app_id)
            raise ValidationError(_('Provide LinkedIn AppID and AppSecret'))
        return super(SocialMediaType, self).action_get_accounts()

    def get_linkedin_oauth_code(self, linkedin_app_id):
        params = {
            'response_type': 'code',
            'client_id': linkedin_app_id,
            'redirect_uri': url_join(self.env['ir.config_parameter'].sudo().get_param('web.base.url'),'linkedin/callback'),
            'state': self.calculate_csrf_token(),
            'scope': 'r_liteprofile r_emailaddress w_member_social rw_organization_admin w_organization_social r_organization_social'
        }

        return {
            'type': 'ir.actions.act_url',
            'url': 'https://www.linkedin.com/oauth/v2/authorization?%s' % url_encode(params),
            'target': 'self'
        }

    def calculate_csrf_token(self):
        letters = string.ascii_lowercase
        csrf_token = ''.join(random.choice(letters) for i in range(20))
        return csrf_token