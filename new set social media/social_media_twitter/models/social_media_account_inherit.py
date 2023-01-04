from odoo import models, fields, api, _


class SocialMediaAccountsInherit(models.Model):
    _inherit = 'social.media.accounts'

    twitter_account_id = fields.Char()
    twitter_display_name = fields.Char()
    twitter_access_token = fields.Char()
    twitter_token_secret = fields.Char()

