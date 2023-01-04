from odoo import models, fields, api, _


class ResConfigInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    use_linkedin = fields.Boolean(string='Use LinkedIn Account')
    linkedin_app_id = fields.Char(string='LinkedIn Client ID')
    linkedin_app_secret = fields.Char(string='LinkedIn Client Secret')
    linkedin_token_manually = fields.Boolean(string="Enter Token Manually")
    linkedin_access_token = fields.Char(string='LinkedIn Access Token')

    def get_values(self):
        res = super(ResConfigInherit, self).get_values()
        config_para = self.env['ir.config_parameter'].sudo()
        res.update(use_linkedin=config_para.get_param('social_media_linkedin.use_linkedin'),
                   linkedin_app_id=config_para.get_param('social_media_linkedin.linkedin_app_id'),
                   linkedin_app_secret=config_para.get_param('social_media_linkedin.linkedin_app_secret'),
                   linkedin_token_manually=config_para.get_param('social_media_linkedin.linkedin_token_manually'),
                   linkedin_access_token=config_para.get_param('social_media_linkedin.linkedin_access_token'))
        return res

    def set_values(self):
        super(ResConfigInherit, self).set_values()
        para = self.env['ir.config_parameter'].sudo()
        para.set_param('social_media_linkedin.use_linkedin',self.use_linkedin)
        para.set_param('social_media_linkedin.linkedin_app_id', self.linkedin_app_id)
        para.set_param('social_media_linkedin.linkedin_app_secret', self.linkedin_app_secret)
        para.set_param('social_media_linkedin.linkedin_token_manually',self.linkedin_token_manually)
        para.set_param('social_media_linkedin.linkedin_access_token', self.linkedin_access_token)