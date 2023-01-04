from odoo import models, fields, api, _, tools
import requests
import base64
from werkzeug.urls import url_join
import json
from odoo.exceptions import ValidationError


class SocialMediaPostInherit(models.Model):
    _inherit = 'social.media.post'

    @api.depends('instagram_post_preview')
    def _compute_instagram_image_id(self):
        for post in self:
            jpeg_images = post.image_ids.filtered(lambda image: image.mimetype == 'image/jpeg')
            post.instagram_image_id = jpeg_images[0] if jpeg_images else False

    facebook_preview = fields.Boolean('Facebook Post Preview')
    instagram_image_id = fields.Many2one('ir.attachment', compute='_compute_instagram_image_id')
    instagram_preview = fields.Boolean('Instagram Preview')
    instagram_post_preview = fields.Html('Instagram', compute='compute_instagram_preview')
    show_instagram_post_preview = fields.Boolean('Display Instagram Preview', compute='compute_display_instagram_preview')
    facebook_post_preview = fields.Html('Facebook', compute='compute_facebook_preview')
    show_facebook_post_preview = fields.Boolean('Display Facebook Preview', compute='compute_display_facebook_preview')

    @api.onchange('facebook_preview', 'instagram_preview')
    def preview_change(self):
        lis = ['facebook_preview', 'instagram_preview']
        for field in lis:
            if self.env.context.get('bool_field_name') != field:
                self[field] = False

    @api.depends('message', 'social_media_account_ids.social_media_id.social_media_types', 'instagram_preview', 'facebook_preview')
    def compute_display_facebook_preview(self):
        for post in self:
            if post.facebook_preview:
                post.show_facebook_post_preview = post.message and (
                            'facebook' in post.social_media_account_ids.social_media_id.mapped('social_media_types'))
            else:
                post.show_facebook_post_preview = False

    @api.depends('message', 'scheduled_date', 'image_ids')
    def compute_facebook_preview(self):
        for post in self:
            post.facebook_post_preview = self.env.ref('social_media_facebook.facebook_preview')._render({
                'message': post.message,
                'published_date': post.scheduled_date if post.scheduled_date else fields.Datetime.now(),
                'images': [
                    image.datas if not image.id
                    else base64.b64encode(open(image._full_path(image.store_fname), 'rb').read()) for image in
                    post.image_ids
                ]
            })

    @api.depends('message', 'social_media_account_ids.social_media_id.social_media_types','instagram_preview', 'facebook_preview')
    def compute_display_instagram_preview(self):
        for post in self:
            if post.instagram_preview:
                post.show_instagram_post_preview = post.message and (
                        'instagram' in post.social_media_account_ids.social_media_id.mapped('social_media_types'))
            else:
                post.show_instagram_post_preview = False

    @api.depends('message', 'scheduled_date', 'image_ids')
    def compute_instagram_preview(self):
        for post in self:
            if 'instagram' in post.social_media_account_ids.social_media_id.mapped('social_media_types'):
                image_error_code = post._get_instagram_image_error()
                if image_error_code == 'missing':
                    raise ValidationError(_('An image is required when posting on Instagram.'))
                elif image_error_code == 'wrong_extension':
                    raise ValidationError(_('Only .jpg/.jpeg images can be posted on Instagram.'))
                elif image_error_code == 'incorrect_ratio':
                    raise ValidationError(
                        _('Your image has to be within the 4:5 and the 1.91:1 aspect ratio as required by Instagram.'))
                elif image_error_code == 'corrupted':
                    raise ValidationError(_('Your image appears to be corrupted, please try loading it again.'))
        for post in self:
            post.instagram_post_preview = self.env.ref('social_media_facebook.instagram_preview')._render({
                'message': post.message,
                'published_date': post.scheduled_date if post.scheduled_date else fields.Datetime.now(),
                'images': [
                    image.datas if not image.id
                    else base64.b64encode(open(image._full_path(image.store_fname), 'rb').read()) for image in
                    post.image_ids
                ]
            })

    def _get_instagram_image_error(self):
        self.ensure_one()
        error_code = False

        if not self.image_ids:
            error_code = 'missing_image'
        else:
            if not self.instagram_image_id:
                error_code = 'wrong_extension'
            else:
                try:
                    image_base64 = self.image_ids.with_context(bin_size=False).datas
                    image = tools.base64_to_image(image_base64)
                    image_ratio = image.width / image.height if image.height else 0
                    if image_ratio < 0.8 or image_ratio > 1.91:
                        error_code = 'incorrect_ratio'
                except Exception:
                    # image could not be loaded
                    error_code = 'corrupted'

        return error_code


class SocialMediaPostLineInherit(models.Model):
    _inherit = 'social.media.post.lines'

    instagram_post_id = fields.Char()
    facebook_post_id = fields.Char()

    def publish_post(self):
        social_media_post = self.filtered(lambda post: post.social_media_account_id.social_media_type in ('facebook', 'instagram'))
        super(SocialMediaPostLineInherit, (self - social_media_post)).publish_post()
        if social_media_post.social_media_type == 'facebook':
            for n in social_media_post:
                n.publish_to_facebook(n.social_media_account_id.facebook_account_id)
        if social_media_post.social_media_type == 'instagram':
            for n in social_media_post:
                n.publish_to_instagram()

    def publish_to_instagram(self):
        self.ensure_one()
        account_id = self.social_media_account_id
        post_id = self.social_media_post_id
        base_url = self.get_base_url()
        message = self.env['mail.render.mixin'].sudo()._shorten_links_text(self.social_media_post_id.message,
                                                                                      {'campaign_id': False,
                                                                                       'medium_id': False,
                                                                                       'source_id': False})
        media_result = requests.post(
            url_join(
                self.env['social.media.types']._instagram_endpoint,
                "/%s/media" % account_id.instagram_account_id
            ),
            data={
                'caption': message,
                'access_token': account_id.instagram_access_token,
                'image_url': url_join(
                    base_url, f'/social_media_instagram/{post_id.id}/get_image'
                )
            },
            timeout=10
        )

        if media_result.status_code != 200 or not media_result.json().get('id'):
            self.write({
                'status': 'failed',
                'reason_for_failure': json.loads(media_result.text or '{}').get('error', {}).get('message', '')
            })
            return

        publish_result = requests.post(
            url_join(
                self.env['social.media.types']._instagram_endpoint,
                "/%s/media_publish" % account_id.instagram_account_id
            ),
            data={
                'access_token': account_id.instagram_access_token,
                'creation_id': media_result.json()['id'],
            },
            timeout=5
        )
        if (publish_result.status_code == 200):
            self.instagram_post_id = publish_result.json().get('id', False)
            values = {
                'status': 'posted',
                'reason_for_failure': False
            }
        else:
            values = {
                'status': 'failed',
                'reason_for_failure': json.loads(publish_result.text or '{}').get('error', {}).get('message', '')
            }

        self.write(values)
        self.social_media_post_id.status = 'posted'

    def get_insta_facebook_accesstoken(self):
        facebook_accounts = self.env['social.media.accounts'].search([('social_media_type', '=', 'facebook')])
        facebook_url = url_join(self.env['social.media.types']._facebook_endpoint,"/v12.0/me?")
        for rec in facebook_accounts:
            params = {'fields': 'instagram_accounts', 'access_token': rec.facebook_access_token}
            response = requests.get(facebook_url, params=params).json()
            if response.get('instagram_accounts'):
                return rec.facebook_access_token
            return self.social_media_account_id.instagram_access_token

    def get_image_url(self):
        image_src = self.sudo().social_media_post_id.image_ids.image_src
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print(base_url+image_src)
        return base_url+image_src

    def publish_to_facebook(self, facebook_account_id):
        self.ensure_one()
        facebook_post_url = url_join(self.env['social.media.types']._facebook_endpoint, "/v3.3/%s/feed" % facebook_account_id)
        shorten_links_text = self.env['mail.render.mixin'].sudo()._shorten_links_text(self.social_media_post_id.message, {'campaign_id': False,'medium_id': False,'source_id': False})
        params = {
            'message': shorten_links_text,
            'access_token': self.social_media_account_id.facebook_access_token
        }
        if self.social_media_post_id.image_ids and len(self.social_media_post_id.image_ids) == 1:
            params['caption'] = params['message']
            image = self.social_media_post_id.image_ids[0]
            result = requests.request('POST', url_join(self.env['social.media.types']._facebook_endpoint, '/v3.3/%s/photos' % facebook_account_id), params=params,
                files={'source': ('source', open(image._full_path(image.store_fname), 'rb'), image.mimetype)})
        else:
            if self.social_media_post_id.image_ids:
                images_attachments = self.formate_facebook_images(facebook_account_id, self.social_media_account_id.facebook_access_token)
                if images_attachments:
                    for index, image_attachment in enumerate(images_attachments):
                        params.update({'attached_media[' + str(index) + ']': json.dumps(image_attachment)})
            result = requests.post(facebook_post_url, params)
        if result.status_code == 200:
            self.facebook_post_id = result.json().get('id', False)
            values = {
                'status': 'posted',
                'reason_for_failure': False}
        else:
            values = {
                'status': 'failed',
                'reason_for_failure': json.loads(result.text or '{}').get('error', {}).get('message', '')
            }
        self.write(values)
        self.social_media_post_id.status = 'posted'
        
    def formate_facebook_images(self, facebook_account_id, facebook_access_token):
        self.ensure_one()
        images = []
        for image in self.social_media_post_id.image_ids:
            post_result = requests.request('POST', url_join(self.env['social.media.types']._facebook_endpoint, '/v3.2/%s/photos' % facebook_account_id), params={
                'published': 'false',
                'access_token': facebook_access_token
            }, files={'source': ('source', open(image._full_path(image.store_fname), 'rb'), image.mimetype)})
            images.append({'media_fbid': post_result.json().get('id')})
        return image