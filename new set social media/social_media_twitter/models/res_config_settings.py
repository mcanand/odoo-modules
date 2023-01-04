from odoo import models, fields, api, _


class ResConfigInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    use_twitter = fields.Boolean(string='Use Twitter Account')
    twitter_app_id = fields.Char(string='Twitter Client ID')
    twitter_app_secret = fields.Char(string='Twitter Client Secret')
    twitter_token_manually = fields.Boolean(string="Enter Bearer Token Manually")
    twitter_access_token = fields.Char(string='Twitter Access Token')

    def get_values(self):
        res = super(ResConfigInherit, self).get_values()
        config_para = self.env['ir.config_parameter'].sudo()
        res.update(use_twitter=config_para.get_param('social_media_twitter.use_twitter'),
                   twitter_app_id=config_para.get_param('social_media_twitter.twitter_app_id'),
                   twitter_app_secret=config_para.get_param('social_media_twitter.twitter_app_secret'),
                   twitter_token_manually=config_para.get_param('social_media_twitter.twitter_token_manually'),
                   twitter_access_token=config_para.get_param('social_media_twitter.twitter_access_token'))
        return res

    def set_values(self):
        super(ResConfigInherit, self).set_values()
        para = self.env['ir.config_parameter'].sudo()
        para.set_param('social_media_twitter.use_twitter',self.use_twitter)
        para.set_param('social_media_twitter.twitter_app_id', self.twitter_app_id)
        para.set_param('social_media_twitter.twitter_app_secret', self.twitter_app_secret)
        para.set_param('social_media_twitter.twitter_token_manually',self.twitter_token_manually)
        para.set_param('social_media_twitter.twitter_access_token', self.twitter_access_token)