from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.addons.calendar.models.calendar_recurrence import weekday_to_field, RRULE_TYPE_SELECTION, END_TYPE_SELECTION, \
    MONTH_BY_SELECTION, WEEKDAY_SELECTION, BYDAY_SELECTION
import json
# from datetime import date, datetime, timedelta
from datetime import date, datetime, timezone, timedelta
import pytz
# from dateutil.relativedelta import relativedelta
# from datetime import datetime
from dateutil.relativedelta import relativedelta


class SocialMediaPost(models.Model):
    _name = 'social.media.post'
    _description = 'social media post'

    is_facebook = fields.Boolean('Facebook')
    is_instagram = fields.Boolean('Instagram')
    message = fields.Text("Message")
    status = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('posting', 'Posting'),
        ('posted', 'Posted')],
        string='Status', default='draft', readonly=True)
    is_failed = fields.Boolean()
    failure_reason = fields.Char()
    has_post_errors = fields.Boolean("There are post errors on sub-posts")
    social_media_account_ids = fields.Many2many('social.media.accounts', 'social_media_post_social_media_account',
                                                'post_id', 'account_id',
                                                string='Social Accounts')
    has_active_accounts = fields.Boolean('Are Accounts Available?')
    social_media_ids = fields.Many2many('social.media', store=True)
    social_media_post_lines = fields.One2many('social.media.post.lines', 'social_media_post_id',
                                              string="Posts By Account", readonly=True)
    image_html = fields.Char('Kanban Images', compute='compute_image_html')
    image_ids = fields.Many2many('ir.attachment', string='Attach Images')
    publish_method = fields.Selection([
        ('now', 'Send now'),
        ('scheduled', 'Schedule later')], string="When", default='now')
    scheduled_date = fields.Datetime('Scheduled post date')
    published_date = fields.Datetime('Published date', readonly=True)
    repeat_post = fields.Selection([('does_not_repeat', 'Does not repeat'),
                                    ('daily', 'Daily'),
                                    ('weekly_on_monday', 'Weekly on Monday'),
                                    ('monthly_on_the_fourth_monday', 'Monthly on the fourth Monday'),
                                    ('mnthly_on_the_last_monday', 'Monthly on the last Monday'),
                                    ('annually_on_feb_28', 'Annually on February 28'),
                                    ('every_weekdays', 'Every weekday(Monday to Friday)'),
                                    ('custom', 'Custom...')], default='does_not_repeat')
    interval = fields.Integer('Repeat every', default=1)
    repeat_type = fields.Selection(RRULE_TYPE_SELECTION, string='Weekday', default='daily')
    end_type = fields.Selection(END_TYPE_SELECTION, string='Recurrence Termination', readonly=False, default='count')
    count = fields.Integer(default=1)
    until = fields.Datetime(readonly=False)
    # month_by = fields.Boolean(string='Option', readonly=False)
    day = fields.Integer('Date of month', readonly=False)
    byday = fields.Selection(BYDAY_SELECTION, readonly=False)
    weekday = fields.Selection(WEEKDAY_SELECTION, readonly=False)
    su = fields.Boolean(string="S")
    mo = fields.Boolean(string="M")
    tu = fields.Boolean(string="T")
    we = fields.Boolean(string="W")
    th = fields.Boolean(string="T")
    fr = fields.Boolean(string="F")
    sa = fields.Boolean(string="S")

    next_posting_time = fields.Datetime()

    def get_next_posting_time(self, publish_time):
        if self.repeat_post == 'daily':
            self.next_posting_time = publish_time + timedelta(days=1)
        if self.repeat_post == 'weekly_on_monday':
            self.next_posting_time = publish_time + datetime.timedelta(days=-publish_time.weekday(), weeks=1)
        if self.repeat_post == 'monthly_on_the_fourth_monday' or self.repeat_post == 'mnthly_on_the_last_monday':
            self.get_monthly_f_l_mondays_posting_date(publish_time)
        if self.repeat_post == 'annually_on_feb_28':
            self.repeat_post = date(publish_time.year + 1, 2, 28)
        if self.repeat_post == 'every_weekdays':
            self.get_every_weekdays(publish_time)
        if self.repeat_post == 'custom':
            interval = self.interval
            count = self.count
            # custom load for day
            if self.end_type == 'count' and self.repeat_type == 'daily':
                if count != 0:
                    self.next_posting_time = publish_time + timedelta(days=interval)
                    self.count = count - 1
            if self.end_type == 'end_date' and self.repeat_type == 'daily':
                if self.until != datetime.utcnow():
                    self.next_posting_time = publish_time + timedelta(days=interval)
            if self.end_type == 'forever' and self.repeat_type == 'daily':
                self.next_posting_time = publish_time + timedelta(days=interval)
            # custom load for week
            if self.end_type == 'count' and self.repeat_type == 'weekly':
                if count != 0:
                    print("in", count)
                    self.get_weekdays_checked()
                    self.count = count - 1
            if self.end_type == 'end_date' and self.repeat_type == 'weekly':
                if self.until != datetime.utcnow():
                    self.get_weekdays_checked()
            if self.end_type == 'forever' and self.repeat_type == 'weekly':
                self.get_weekdays_checked()
            # custom load for monthly
            if self.end_type == 'count' and self.repeat_type == 'monthly':
                if count != 0:
                    self.next_posting_time = publish_time + relativedelta(months=interval)
                    self.count = count - 1
            if self.end_type == 'end_date' and self.repeat_type == 'monthly':
                if self.until != datetime.utcnow():
                    self.next_posting_time = publish_time + relativedelta(months=interval)
            if self.end_type == 'forever' and self.repeat_type == 'monthly':
                self.next_posting_time = publish_time + relativedelta(months=interval)
            # custom load for yearly
            if self.end_type == 'count' and self.repeat_type == 'yearly':
                if count != 0:
                    self.next_posting_time = publish_time + relativedelta(months=12 * int(interval))
                    self.count = count - 1
            if self.end_type == 'end_date' and self.repeat_type == 'yearly':
                if self.until != datetime.utcnow():
                    self.next_posting_time = publish_time + relativedelta(months=12 * int(interval))
            if self.end_type == 'forever' and self.repeat_type == 'yearly':
                self.next_posting_time = publish_time + relativedelta(months=12 * int(interval))

    @api.model
    def create(self, vals_list):
        res = super(SocialMediaPost, self).create(vals_list)
        if vals_list['repeat_post'] == 'custom':
            if vals_list['scheduled_date'] > vals_list['until']:
                raise ValidationError(_('end date should be greater than scheduled date'))
        return res

    def write(self, vals):
        res = super(SocialMediaPost, self).write(vals)
        if self.repeat_post == 'custom':
            if self.scheduled_date > self.until:
                raise ValidationError(_('end date should be greater than scheduled date'))
        return res

    def get_weekdays_checked(self):
        interval = self.interval
        list = {
            0: self.mo,
            1: self.tu,
            2: self.we,
            3: self.th,
            4: self.fr,
            5: self.sa,
            6: self.su, }
        today = datetime.utcnow().today()
        lis = [n for n in list if list[n] == True]
        if today.weekday() != 6:
            for k in lis:
                if today.weekday() < k:
                    self.next_posting_time = today + timedelta(days=k)
                    break
        else:
            today + timedelta(days=lis[0])
            for n in range(interval):
                today += timedelta(days=7)
            self.next_posting_time = today

    def get_every_weekdays(self, publish_time):
        publish_time += timedelta(days=1)
        if publish_time.weekday() not in [5, 6]:
            self.next_posting_time = publish_time
        if publish_time.weekday() == 5:
            self.next_posting_time = publish_time + timedelta(days=2)
        if publish_time.weekday() == 6:
            self.next_posting_time = publish_time + timedelta(days=1)

    def get_monthly_f_l_mondays_posting_date(self, publish_time):
        published_mnth = publish_time.month
        day = date(publish_time.year, publish_time.month, 1)
        loop = True
        dates = []
        while loop == True:
            day += datetime.timedelta(days=-day.weekday(), weeks=1)
            loop = False
            if day.month != published_mnth + 1:
                dates.append(day)
                loop = True
        if self.repeat_post == 'monthly_on_the_fourth_monday':
            self.next_posting_time = date[3]
        if self.repeat_post == 'mnthly_on_the_last_monday':
            self.next_posting_time = date[-1]

    @api.depends('image_ids')
    def compute_image_html(self):
        for rec in self:
            rec.image_html = 'localhost:8014/' + rec.image_ids.image_src

    def get_social_media_post_status(self):
        completed_lines = [n for n in self.social_media_post_lines if
                           self.social_media_post_lines.status in ('posted', 'failed')]
        if completed_lines:
            self.sudo().write({'status': 'posted'})

    @api.onchange('is_facebook', 'is_instagram')
    def social_media_account_filter(self):
        if self.is_instagram and self.is_facebook:
            if self.env.context.get('bool_media_type'):
                return {
                    'domain': {'social_media_account_ids': [('social_media_type', 'in', ['facebook', 'instagram'])]}}
        else:
            self.social_media_account_ids = False
            return {'domain': {
                'social_media_account_ids': [('social_media_type', '=', self.env.context.get('bool_media_type'))]}}

    @api.constrains('image_ids')
    def check_image_ids_mimetype(self):
        for social_post in self:
            if any(not image.mimetype.startswith('image') for image in social_post.image_ids):
                raise UserError(_('Uploaded file does not seem to be a valid image.'))

    def name_get(self):
        result = []
        for post in self:
            if post.message:
                name = post.message[:20] + '...'
            else:
                name = 'No name yet'
            result.append((post.id, name))
        return result

    def publish(self):
        self.write({
            'publish_method': 'now',
            'scheduled_date': False,
            'status': 'posting',
            'published_date': fields.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            'social_media_post_lines': [(0, 0, {'social_media_post_id': self.id, 'social_media_account_id': account.id})
                                        for account in self.social_media_account_ids]
        })
        for social_post in self.social_media_post_lines:
            social_post.publish_post()

    def action_schedule(self):
        if self.repeat_post == 'custom':
            if self.scheduled_date > self.until:
                raise ValidationError(_('end date should be greater than scheduled date'))
            else:
                self.write({'status': 'scheduled'})
        else:
            self.write({'status': 'scheduled'})


class SocialMediaPostLines(models.Model):
    _name = 'social.media.post.lines'
    _description = 'Social media post lines'

    social_media_post_id = fields.Many2one('social.media.post')
    social_media_account_id = fields.Many2one('social.media.accounts', string="Social Media Account", required=True)
    reason_for_failure = fields.Text('Failure Reason')
    status = fields.Selection([
        ('ready', 'Ready'),
        ('posted', 'POSTED'),
        ('failed', 'Failed')],
        string='Status', default='ready', required=True)
    social_media_type = fields.Char(compute="compute_social_media_types")
    account_name = fields.Char(compute='compute_account_name')

    def cron_schedule(self):
        print("11")
        scheduled_post = self.env['social.media.post'].search(
            [('status', '=', 'scheduled'), ('publish_method', '=', 'scheduled'),
             ('scheduled_date', '<=', fields.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))])
        publish_time = scheduled_post.scheduled_date
        scheduled_post.get_next_posting_time(publish_time)
        if scheduled_post:
            for rec in scheduled_post:
                rec.publish()

    def compute_social_media_types(self):
        for rec in self:
            rec.social_media_type = rec.social_media_account_id.social_media_type
            rec.account_name = rec.social_media_account_id.name

    def publish_post(self):
        pass

    def name_get(self):
        return [(n.id, n.social_media_account_id.social_media_type + "-" + n.social_media_post_id.message) for n in
                self]
