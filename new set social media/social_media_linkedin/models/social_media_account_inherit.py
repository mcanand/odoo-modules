from odoo import models, fields, api, _
import requests
from werkzeug.urls import url_join
import base64


class SocialMediaAccountInherit(models.Model):
    _inherit = 'social.media.accounts'

    linkedin_account_id = fields.Char(string='LinkedIn Account ID')
    linkedin_account_urn = fields.Char(string='LinkedIn Account URN', readonly=True)
    linkedin_access_token = fields.Char(string='LinkedIn access token', readonly=True)

    def fetch_linkedin_accounts(self, access_token=None):
        response = requests.get(
            url_join(self.env['social.media.types']._linkedin_endpoint, 'organizationAcls'),
            params={
                'q': 'roleAssignee',
                'role': 'ADMINISTRATOR',
                'projection': '(elements*(*,organization~(%s)))' % self.env['social.media.types']._linkedin_organisation_protection,},
            headers={'Authorization': 'Bearer %s' % access_token,
                     'cache-control': 'no-cache',
                     'X-Restli-Protocol-Version': '2.0.0'}).json()

        accounts = []
        if 'elements' in response and isinstance(response.get('elements'), list):
            for acc in response.get('elements'):
                image_url = self.get_pro_pic(acc.get('organization~'))
                image_data = requests.get(image_url).content if image_url else None
                accounts.append({
                    'name': acc.get('organization~', {}).get('localizedName'),
                    'linkedin_account_urn': acc.get('organization'),
                    'linkedin_access_token': access_token,
                    'image': base64.b64encode(image_data) if image_data else False,
                })
        return accounts

    def get_pro_pic(self, data):
        elements = None
        if data and 'logoV2' in data:
            elements = data.get('logoV2', {}).get('original~', {})
        elif data and 'profilePicture' in data:
            elements = data.get('profilePicture', {}).get('displayImage~', {})
        if elements:
            return elements.get('elements', [{}])[0].get('identifiers', [{}])[0].get('identifier', '')
        return ''