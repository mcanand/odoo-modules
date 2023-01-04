from odoo import models, fields, api


class SocialMediaAccounts(models.Model):
    _name = 'social.media.accounts'
    _description = 'Social media accounts'

    name = fields.Char(required=True)
    display_name = fields.Char(readonly=True)
    image = fields.Image("Image", max_width=128, max_height=128, readonly=True)
    social_media_id = fields.Many2one('social.media.types', string='Social Media Type')
    social_media_type = fields.Selection(related='social_media_id.social_media_types')
