from odoo import models, fields, api, _


class SocailMediaDashboard(models.Model):
    _name = 'social.media.dashboard'
    _description = 'social media dashboard'

    name = fields.Char()
    color = fields.Char()
    all_account_count = fields.Integer(compute='account_counts')
    facebook_account_count = fields.Integer(compute="facebook_account_counts")
    instagram_account_count = fields.Integer(compute="instagram_account_counts")
    linkedin_account_count = fields.Integer(compute="linkedin_account_counts")
    twitter_account_count = fields.Integer(compute="twitter_account_counts")


    def account_counts(self):
        social_media_account_obj = self.env['social.media.accounts']
        self.all_account_count = social_media_account_obj.search_count([])

    @api.model
    def facebook_account_counts(self):
        social_media_account_obj = self.env['social.media.accounts']
        self.facebook_account_count = social_media_account_obj.search_count([('social_media_type', '=', 'facebook')])

    def instagram_account_counts(self):
        social_media_account_obj = self.env['social.media.accounts']
        self.instagram_account_count = social_media_account_obj.search_count([('social_media_type', '=', 'instagram')])

    def linkedin_account_counts(self):
        social_media_account_obj = self.env['social.media.accounts']
        self.linkedin_account_count = social_media_account_obj.search_count([('social_media_type', '=', 'linkedin')])

    def twitter_account_counts(self):
        social_media_account_obj = self.env['social.media.accounts']
        self.twitter_account_count = social_media_account_obj.search_count([('social_media_type', '=', 'twitter')])

    @api.model
    def link_facebook_account(self, *a):
        facebook = self.env['social.media.types'].search([('social_media_types', '=', 'facebook')])
        if facebook:
            return facebook.action_get_accounts()

    def link_instagram_account(self):
        instagram = self.env['social.media.types'].search([('social_media_types', '=', 'instagram')])
        if instagram:
            instagram.action_get_accounts()

    def link_linkedin_account(self):
        linkedin = self.env['social.media.types'].search([('social_media_types', '=', 'linkedin')])
        if linkedin:
            linkedin.action_get_accounts()

    def link_twitter_account(self):
        twitter = self.env['social.media.types'].search([('social_media_types', '=', 'twitter')])
        if twitter:
            twitter.action_get_accounts()

    def all_accounts(self):
        return {
            'name': _('Facebook'),
            'view_mode': 'kanban',
            'res_model': 'social.media.accounts',
            'type': 'ir.actions.act_window'
        }

    # def facebook_accounts(self):
        # return {
        #     'name': _('Facebook'),
        #     'view_mode': 'kanban',
        #     'domain': "[('social_media_type', '=', 'facebook')]",
        #     'res_model': 'social.media.accounts',
        #     'type': 'ir.actions.act_window'
        # }

    # def instagram_accounts(self):
    #     return {
    #         'name': _('Instagram'),
    #         'view_mode': 'kanban',
    #         'domain': "[('social_media_type', '=', 'instagram')]",
    #         'res_model': 'social.media.accounts',
    #         'type': 'ir.actions.act_window'
    #     }
    
    # def linkedin_accounts(self):
    #     return {
    #         'name': _('LinkedIn'),
    #         'view_mode': 'kanban',
    #         'domain': "[('social_media_type', '=', 'linkedin')]",
    #         'res_model': 'social.media.accounts',
    #         'type': 'ir.actions.act_window'
    #     }

    # def twitter_accounts(self):
    #     return {
    #         'name': _('Twitter'),
    #         'view_mode': 'kanban',
    #         'domain': [('social_media_type', '=', 'twitter')],
    #         'res_model': 'social.media.accounts',
    #         'type': 'ir.actions.act_window'
    #     }