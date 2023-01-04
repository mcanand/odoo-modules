from odoo import fields, models, api, _
from odoo.addons.calendar.models.calendar_recurrence import weekday_to_field, RRULE_TYPE_SELECTION, END_TYPE_SELECTION, MONTH_BY_SELECTION, WEEKDAY_SELECTION, BYDAY_SELECTION


class RepeatPostMethod(models.TransientModel):
    _name = 'repeat.post.method'
    _description = 'repeat post method'

    interval = fields.Integer('Repeat every', default=1)
    repeat_type = fields.Selection(RRULE_TYPE_SELECTION, string='Weekday', default='daily')
    end_type = fields.Selection(END_TYPE_SELECTION, string='Recurrence Termination', readonly=False, default='count')
    count = fields.Integer(default=1)
    until = fields.Date(readonly=False)
    month_by = fields.Selection(MONTH_BY_SELECTION, string='Option', readonly=False)
    day = fields.Integer('Date of month', readonly=False)
    byday = fields.Selection(BYDAY_SELECTION, readonly=False)
    weekday = fields.Selection(WEEKDAY_SELECTION, readonly=False)
    mo = fields.Boolean()
    tu = fields.Boolean()
    we = fields.Boolean()
    th = fields.Boolean()
    fr = fields.Boolean()
    sa = fields.Boolean()
    su = fields.Boolean()

