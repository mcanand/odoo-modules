# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class CouponLine(models.Model):
    _inherit = 'sale.order.line'

    is_coupon = fields.Boolean()
    is_coupon_type = fields.Boolean(default=True)


class AvailableChannel(models.Model):
    _name = 'available.channels'

    name = fields.Char("Name")
    name_key = fields.Char("Value")


class Coupon(models.Model):
    _inherit = 'coupon.coupon'

    code = fields.Char(required=True, readonly=False)
    exclusive_coupon = fields.Boolean(default=True, help="Customer's can't use any other coupon if this coupon is used")
    available_channels = fields.Many2many('available.channels',
                                          string="Available Channel",
                                          help="Coupon can be used only for selected channel")

    all_days = fields.Boolean("All days")
    all_time = fields.Boolean("All time")
    same_time = fields.Boolean("Same time")
    enter_time_from = fields.Float(string='From')
    enter_time_to = fields.Float(string='To')
    sunday_available = fields.Boolean("Sunday")
    sunday_available_time_from = fields.Float(string='From')
    sunday_available_time_to = fields.Float(string='To')
    monday_available = fields.Boolean("Monday")
    monday_available_time_from = fields.Float(string='From')
    monday_available_time_to = fields.Float(string='To')
    tuesday_available = fields.Boolean("Tuesday")
    tuesday_available_time_from = fields.Float(string='From')
    tuesday_available_time_to = fields.Float(string='To')
    wednesday_available = fields.Boolean("Wednesday")
    wednesday_available_time_from = fields.Float(string='From')
    wednesday_available_time_to = fields.Float(string='To')
    thursday_available = fields.Boolean("Thursday")
    thursday_available_time_from = fields.Float(string='From')
    thursday_available_time_to = fields.Float(string='To')
    friday_available = fields.Boolean("Friday")
    friday_available_time_from = fields.Float(string='From')
    friday_available_time_to = fields.Float(string='To')
    saturday_available = fields.Boolean("Saturday")
    saturday_available_time_from = fields.Float(string='From')
    saturday_available_time_to = fields.Float(string='To')
    restricted_product_ids = fields.Many2many('product.template',
                                              string="Restricted Products",
                                              help="Coupon can not be applied for restricted products")
    partner_type = fields.Selection([
        ('guest', 'Guest'),
        ('loyalist', 'Loyalist'),
        ('both', 'Both')
    ], string="Coupon Apply for partner type", default='guest')

    @api.onchange('partner_type')
    def select_partner(self):
        lis = []
        if self.partner_type == 'guest':
            for rec in self.env['res.partner'].search([('partner_type', '=', 'guest')]):
                lis.append(rec.id)
        elif self.partner_type == 'loyalist':
            for rec in self.env['res.partner'].search([('partner_type', '=', 'loyalist')]):
                lis.append(rec.id)
        elif self.partner_type == 'both':
            for rec in self.env['res.partner'].search([]):
                lis.append(rec.id)
        return {'domain': {'partner_id': [('id', 'in',lis)]}}


    @api.onchange('enter_time_from', 'enter_time_to')
    def check_from_to_time(self):
        if self.same_time is True:
            if self.enter_time_from and self.enter_time_to == 0.00:
                raise ValidationError(_("Please enter the valid same time"))
            if self.enter_time_from > 24:
                raise ValidationError(_("Please enter the valid same time"))
            if self.enter_time_to < self.sunday_available_time_from or self.enter_time_to > 24:
                raise ValidationError(_("Value of  'to time' must be greater than or equal to the 'from time'"))

    @api.constrains("sunday_available_time_from", "sunday_available_time_to", "monday_available_time_from",
                    "monday_available_time_to",
                    "tuesday_available_time_from", "tuesday_available_time_to", "wednesday_available_time_from",
                    "wednesday_available_time_to"
                    "thursday_available_time_from", "thursday_available_time_to", "friday_available_time_from",
                    "friday_available_time_to",
                    "saturday_available_time_from", "saturday_available_time_to")
    def check_valid_time(self):
        if self.sunday_available_time_from > 24:
            raise ValidationError(_("Please enter valid time for Sunday"))
        if self.monday_available_time_from > 24:
            raise ValidationError(_("Please enter valid time for Monday"))
        if self.tuesday_available_time_from > 24:
            raise ValidationError(_("Please enter valid time for Tuesday"))
        if self.wednesday_available_time_from > 24:
            raise ValidationError(_("Please enter valid time for Wednesday"))
        if self.thursday_available_time_from > 24:
            raise ValidationError(_("Please enter valid time for Thursday"))
        if self.friday_available_time_from > 24:
            raise ValidationError(_("Please enter valid time for Friday"))
        if self.saturday_available_time_from > 24:
            raise ValidationError(_("Please enter valid time for Saturday"))

        if self.sunday_available_time_to < self.sunday_available_time_from or self.sunday_available_time_to > 24:
            raise ValidationError(_("Sunday 'to time' must be greater than or equal to the 'from time'"))
        if self.monday_available_time_to < self.monday_available_time_from or self.monday_available_time_to > 24:
            raise ValidationError(_("Monday 'to time' must be greater than or equal to the 'from time'"))
        if self.tuesday_available_time_to < self.tuesday_available_time_from or self.tuesday_available_time_to > 24:
            raise ValidationError(_("Tuesday 'to time' must be greater than or equal to the 'from time'"))
        if self.wednesday_available_time_to < self.wednesday_available_time_from or self.wednesday_available_time_to > 24:
            raise ValidationError(_("Wednesday 'to time' must be greater than or equal to the 'from time'"))
        if self.thursday_available_time_to < self.thursday_available_time_from or self.thursday_available_time_to > 24:
            raise ValidationError(_("Thursday 'to time' must be greater than or equal to the 'from time'"))
        if self.friday_available_time_to < self.friday_available_time_from or self.friday_available_time_to > 24:
            raise ValidationError(_("Friday 'to time' must be greater than or equal to the 'from time'"))
        if self.saturday_available_time_to < self.saturday_available_time_from or self.saturday_available_time_to > 24:
            raise ValidationError(_("Saturday 'to time' must be greater than or equal to the 'from time'"))

    @api.onchange('sunday_available', 'monday_available', 'tuesday_available',
                  'wednesday_available', 'thursday_available', 'friday_available', 'saturday_available')
    def set_time(self):
        if self.sunday_available == False:
            print("osincohduvbcivwghsfdvcighfscd sa")
            self.write({'sunday_available_time_from': 0,
                        'sunday_available_time_to': 0})
        if self.monday_available == False:
            self.write({'monday_available_time_from': 0,
                        'monday_available_time_to': 0})
        if self.tuesday_available == False:
            self.write({'tuesday_available_time_from': 0,
                        'tuesday_available_time_to': 0})
        if self.wednesday_available == False:
            self.write({'wednesday_available_time_from': 0,
                        'wednesday_available_time_to': 0})
        if self.thursday_available == False:
            self.write({'thursday_available_time_from': 0,
                        'thursday_available_time_to': 0})
        if self.friday_available == False:
            self.write({'friday_available_time_from': 0,
                        'friday_available_time_to': 0})
        if self.saturday_available == False:
            self.write({'saturday_available_time_from': 0,
                        'saturday_available_time_to': 0})

    @api.onchange('same_time', 'enter_time_from', 'enter_time_to')
    def set_same_time(self):
        if self.same_time == True:
            if self.enter_time_from and self.enter_time_to:
                self.write({'all_time': False,
                            'sunday_available_time_from': self.enter_time_from,
                            'monday_available_time_from': self.enter_time_from,
                            'tuesday_available_time_from': self.enter_time_from,
                            'wednesday_available_time_from': self.enter_time_from,
                            'thursday_available_time_from': self.enter_time_from,
                            'friday_available_time_from': self.enter_time_from,
                            'saturday_available_time_from': self.enter_time_from,
                            'sunday_available_time_to': self.enter_time_to,
                            'monday_available_time_to': self.enter_time_to,
                            'tuesday_available_time_to': self.enter_time_to,
                            'wednesday_available_time_to': self.enter_time_to,
                            'thursday_available_time_to': self.enter_time_to,
                            'friday_available_time_to': self.enter_time_to,
                            'saturday_available_time_to': self.enter_time_to,
                            })

    @api.onchange('all_days', 'all_time')
    def set_all_days(self):
        if self.all_days == True:
            self.write({'sunday_available': True,
                        'monday_available': True,
                        'tuesday_available': True,
                        'wednesday_available': True,
                        'thursday_available': True,
                        'friday_available': True,
                        'saturday_available': True
                        })
        if self.all_days == False:
            self.write({'all_time': False,
                        'same_time': False,
                        'sunday_available': False,
                        'monday_available': False,
                        'tuesday_available': False,
                        'wednesday_available': False,
                        'thursday_available': False,
                        'friday_available': False,
                        'saturday_available': False
                        })

        if self.all_time == True:
            self.write({'same_time': False,
                        'enter_time_from': 0,
                        'sunday_available_time_from': 0,
                        'monday_available_time_from': 0,
                        'tuesday_available_time_from': 0,
                        'wednesday_available_time_from': 0,
                        'thursday_available_time_from': 0,
                        'friday_available_time_from': 0,
                        'saturday_available_time_from': 0,
                        'enter_time_to': 24,
                        'sunday_available_time_to': 24,
                        'monday_available_time_to': 24,
                        'tuesday_available_time_to': 24,
                        'wednesday_available_time_to': 24,
                        'thursday_available_time_to': 24,
                        'friday_available_time_to': 24,
                        'saturday_available_time_to': 24,
                        })

    ################################################################################################################

    @api.onchange('restricted_product_ids')
    def action_restrict_product_conflict(self):
        data = []
        check_product = self.restricted_product_ids.ids
        l1 = self.program_id.reward_product_id.product_tmpl_id.id
        if l1 in check_product:
            raise ValidationError(_("It is a reward offer product in this coupon!"))
        for rec in self.program_id.discount_specific_product_ids:
            data = rec.product_tmpl_id.ids
        if set(check_product).intersection(data):
            raise ValidationError(_("It is a discount offer product in this coupon!!"))

    ###############################################################################################################

    def _check_coupon_code(self, order):
        now = fields.datetime.now() + timedelta(hours=5, minutes=30)
        current_time = str(now.strftime("%H.%M"))
        actual_time = current_time.replace(".", ":")
        if datetime.today().weekday() == 0 and self.monday_available is True:
            time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.monday_available_time_from) * 60, 60))
            time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.monday_available_time_to) * 60, 60))
            if time_from <= actual_time and time_to >= actual_time:
                pass
            else:
                message = {
                    'error': _('Coupon is not available')}
                return message
        elif datetime.today().weekday() == 1 and self.tuesday_available is True:
            time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.tuesday_available_time_from) * 60, 60))
            time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.tuesday_available_time_to) * 60, 60))
            if time_from <= actual_time and time_to >= actual_time:
                pass
            else:
                message = {
                    'error': _('Coupon is not available')}
                return message
        elif datetime.today().weekday() == 2 and self.wednesday_available is True:
            time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.wednesday_available_time_from) * 60, 60))
            time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.wednesday_available_time_to) * 60, 60))
            if time_from <= actual_time and time_to >= actual_time:
                pass
            else:
                message = {
                    'error': _('Coupon is not available')}
                return message
        elif datetime.today().weekday() == 3 and self.thursday_available is True:
            time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.thursday_available_time_from) * 60, 60))
            time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.thursday_available_time_to) * 60, 60))
            if time_from <= actual_time and time_to >= actual_time:
                pass
            else:
                message = {
                    'error': _('Coupon is not available')}
                return message
        elif datetime.today().weekday() == 4 and self.friday_available is True:
            time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.friday_available_time_from) * 60, 60))
            time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.friday_available_time_to) * 60, 60))
            if time_from <= actual_time and time_to >= actual_time:
                pass
            else:
                message = {
                    'error': _('Coupon is not available')}
                return message
        elif datetime.today().weekday() == 5 and self.saturday_available is True:
            time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.saturday_available_time_from) * 60, 60))
            time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.saturday_available_time_to) * 60, 60))
            if time_from <= actual_time and time_to >= actual_time:
                pass
        elif datetime.today().weekday() == 6 and self.sunday_available is True:
            time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.sunday_available_time_from) * 60, 60))
            time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.sunday_available_time_to) * 60, 60))
            if time_from <= actual_time and time_to >= actual_time:
                pass
            else:
                message = {
                    'error': _('Coupon is not available')}
                return message
        else:
            message = {
                'error': _('Coupon is not available')}
            return message
        message = {}
        if order.order_line:
            exclusive = False
            for i in order.order_line:
                if i.is_reward_line and self.exclusive_coupon:
                    message = {
                        'error': _('Only one discount at a time')}
                    return message
        ######################################################################################################
        # restrict products from applying coupon
        product_ids = self.restricted_product_ids.ids
        order_line_count = self.env['sale.order.line'].search([('order_id', '=', order.id)])
        line_list = []
        for rec in order_line_count:
            line_list.append(rec.product_template_id.id)
        result = list(filter(lambda x: x in line_list, product_ids))
        if not result:
            pass
        else:
            if self.program_id.discount_apply_on == 'specific_products' and self.program_id.discount_specific_product_ids:
                check_product_ids = self.program_id.discount_specific_product_ids.product_tmpl_id.ids
                discount_list = list(filter(lambda x: x in line_list, check_product_ids))
                if discount_list:
                    pass
                else:
                    message = {'error': _('Coupon is not applicable')}
                    return message
            elif self.program_id.reward_type == 'product' and self.program_id.reward_product_id:
                reward_id = self.program_id.reward_product_id.product_tmpl_id.id
                if reward_id in line_list:
                    pass
                else:
                    message = {'error': _('Coupon is not applicable')}
                    return message
            else:
                message = {'error': _('Coupon is not applicable')}
                return message

        ######################################################################################################

        channel_values = []
        for channel_key in self.available_channels:
            channel_values.append(str(channel_key.name_key))
        if order.website_delivery_type:
            if not order.pickup_date_string and order.website_delivery_type == "pickup":
                if "takeaway" in channel_values:
                    pass
                else:
                    message = {'error': _('Coupon code not available')}
                    return message
            elif order.website_delivery_type in channel_values:
                pass
            else:
                message = {'error': _('Coupon code not available')}
                return message

        applicable_programs = order._get_applicable_programs()
        if self.state == 'reserved':
            message = {
                'error': _('This coupon %s exists but the origin sales order is not validated yet.') % (self.code)}
        elif self.state == 'cancel':
            message = {'error': _('This coupon has been cancelled (%s).') % (self.code)}
        elif self.state == 'expired' or (self.expiration_date and self.expiration_date < order.date_order.date()):
            message = {'error': _('This coupon is expired (%s).') % (self.code)}
        # Minimum requirement should not be checked if the coupon got generated by a promotion program (the requirement should have only be checked to generate the coupon)
        elif self.program_id.program_type == 'coupon_program' and not self.program_id._filter_on_mimimum_amount(order):
            message = {'error': _(
                'A minimum of %(amount)s %(currency)s should be purchased to get the reward',
                amount=self.program_id.rule_minimum_amount,
                currency=self.program_id.currency_id.name
            )}
        elif not self.program_id.active:
            message = {'error': _('The coupon program for %s is in draft or closed state') % (self.code)}
        elif self.partner_id and self.partner_id != order.partner_id:
            message = {'error': _('Invalid partner.')}
        elif self.program_id in order.applied_coupon_ids.mapped('program_id'):
            message = {'error': _('A Coupon is already applied for the same reward')}
        elif self.program_id._is_global_discount_program() and order._is_global_discount_already_applied():
            message = {'error': _('Global discounts are not cumulable.')}
        elif self.program_id.reward_type == 'product' and not order._is_reward_in_order_lines(self.program_id):
            message = {'error': _('The reward products should be in the sales order lines to apply the discount.')}
        elif not self.program_id._is_valid_partner(order.partner_id):
            message = {'error': _("The customer doesn't have access to this reward.")}
        # Product requirement should not be checked if the coupon got generated by a promotion program (the requirement should have only be checked to generate the coupon)
        elif self.program_id.program_type == 'coupon_program' and not self.program_id._filter_programs_on_products(
                order):
            message = {'error': _(
                "You don't have the required product quantities on your sales order. All the products should be recorded on the sales order. (Example: You need to have 3 T-shirts on your sales order if the promotion is 'Buy 2, Get 1 Free').")}
        else:
            if self.program_id not in applicable_programs and self.program_id.promo_applicability == 'on_current_order':
                message = {'error': _('At least one of the required conditions is not met to get the reward!')}
        return message

# class SaleCouponApplyCodes(models.TransientModel):
#     _inherit = 'sale.coupon.apply.code'
#
#     def apply_coupon(self, order, coupon_code):
#         error_status = {}
#         pg = False
#         cd = False
#         program = False
#         if coupon_code:
#             program = self.env['coupon.program'].search([('promo_code', 'ilike', coupon_code)], limit=1)
#         if program:
#             if len(program.promo_code) == len(coupon_code):
#                 pg = True
#         if program and pg:
#             error_status = program._check_promo_code(order, coupon_code)
#             if not error_status:
#                 if program.promo_applicability == 'on_next_order':
#                     # Avoid creating the coupon if it already exist
#                     if program.discount_line_product_id.id not in order.generated_coupon_ids.filtered(lambda coupon: coupon.state in ['new', 'reserved']).mapped('discount_line_product_id').ids:
#                         coupon = order._create_reward_coupon(program)
#                         return {
#                             'generated_coupon': {
#                                 'reward': coupon.program_id.discount_line_product_id.name,
#                                 'code': coupon.code,
#                             }
#                         }
#                 else:  #  The program is applied on this order
#                     order._create_reward_line(program)
#                     order.code_promo_program_id = program
#         else:
#             coupon = self.env['coupon.coupon'].search([('code', 'ilike', coupon_code)], limit=1)
#             if coupon:
#                 if len(coupon.code) == len(coupon_code):
#                     cd = True
#             if coupon and cd:
#                 error_status = coupon._check_coupon_code(order)
#                 if not error_status:
#                     order._create_reward_line(coupon.program_id)
#                     order.applied_coupon_ids += coupon
#                     coupon.write({'state': 'used'})
#             else:
#                 error_status = {'not_found': _('This coupon is invalid (%s).') % (coupon_code)}
#         return error_status
