from odoo import models, fields, api, _


# class SocailMediaDashboardViewssss(models.Model):
#     _inherit = 'ir.ui.menu'
#
#     restrict_user_ids = fields.Char()

class SocailMediaDashboardViews(models.Model):
    _inherit = 'social.media.dashboard'

    dash_name = fields.Char(readonly=True,store=True,compute='facebook_accounts_insight')
    dash_posts = social_media_post_lines = fields.One2many('social.media.post.lines', 'social_media_post_id',
                                              string="Posts By Account", readonly=True)
    xx = fields.Char()

    # def facebook_accounts_insight(self):
    #     self.write({ 'dash_name' : 'facebook','xx':['1','2','3','4','5','6','7','8']})
    #     return {
    #         'name': _('Social Media insight Dashboard'),
    #         'view_mode': 'form',
    #         # 'domain': "[('social_media_type', '=', 'facebook')]",
    #         'res_model': 'social.media.dashboard',
    #         'type': 'ir.actions.act_window',
    #         'context': {
    #             'default_dash_name': self.dash_name,
    #             'default_xx':self.xx
    #         }
    #     }

    def instagram_accounts_insight(self):

        self.write({'dash_name': 'instagram'})
        return {
            'name': _('Social Media insight Dashboard'),
            'view_mode': 'form',
            # 'domain': "[('social_media_type', '=', 'insta')]",
            'res_model': 'social.media.dashboard',
            'type': 'ir.actions.act_window',
            'context': {'default_dash_name': self.dash_name}
        }

    def linkedin_accounts_insight(self):
        print("z")

    def twitter_accounts_insight(self):
        print("a")
