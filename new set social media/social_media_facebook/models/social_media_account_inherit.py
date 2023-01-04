from odoo import models, fields, api


class SocialMediaAccountInherit(models.Model):
    _inherit = 'social.media.accounts'

    facebook_account_id = fields.Char(string='Facebook Account Id', readonly=True)
    facebook_access_token = fields.Char(string='Facebook Access Token', readonly=True)
    instagram_account_id = fields.Char(string='Facebook Account Id', readonly=True)
    instagram_access_token = fields.Char(string='Facebook Access Token', readonly=True)
    instagram_facebook_account_id = fields.Char(string="Instagram Facebook Account Id")
    