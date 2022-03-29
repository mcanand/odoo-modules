# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang


class SaleOrder(models.Model):
    _inherit = "sale.order"
    check_status_promo = fields.Boolean()

    def _check_status_promo(self):
        if self.check_status_promo:
            self.check_status_promo = False
            return True
        return False

    def _get_cheapest_line(self, program):
        product_search = self.env['product.template'].search([])
        cheapest_line = self.order_line.filtered(
            lambda x: not x.is_reward_line and not x.is_delivery and x.price_reduce > 0 and x.is_coupon_type)
        # cheapest_line = min(self.order_line.filtered(lambda x: not x.is_reward_line and not x.is_delivery and x.price_reduce > 0 and x.is_coupon_type),key=lambda x: x['price_reduce'])
        # product_list = []
        check_product = program.cheapest_product_select_product_ids.product_tmpl_id.ids
        if check_product:
            cheapest_product = []
            for i in cheapest_line:
                if i.product_template_id.id in check_product:
                    cheapest_product.append(i)
            if cheapest_product:
                cheap_product = min(cheapest_product, key=lambda x: x['price_reduce'])
                if cheap_product:
                    return cheap_product
                elif program.cheapest_product_select_category_ids:
                    product_list = []
                    for i in cheapest_line:
                        if i.product_template_id.public_categ_ids in program.cheapest_product_select_category_ids:
                            product_list.append(i)
                    if product_list:
                        print(product_list)
                        cheap_product_id = min(product_list, key=lambda x: x['price_reduce'])
                        if cheap_product_id:
                            return cheap_product_id
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                pass
        elif program.cheapest_product_select_category_ids:
            product_list = []
            for i in cheapest_line:
                if i.product_template_id.public_categ_ids in program.cheapest_product_select_category_ids:
                    product_list.append(i)
            if product_list:
                print(product_list)
                cheap_product_id = min(product_list, key=lambda x: x['price_reduce'])
                if cheap_product_id:
                    return cheap_product_id
                else:
                    pass
            else:
                pass

    def _get_reward_values_discount(self, program):
        p_coupn = self.promo_code
        if program.discount_type == 'fixed_amount':
            taxes = program.discount_line_product_id.taxes_id
            if self.fiscal_position_id:
                taxes = self.fiscal_position_id.map_tax(taxes)
            return [{
                'name': _("Discount: %s", program.name),
                'product_id': program.discount_line_product_id.id,
                'price_unit': - self._get_reward_values_discount_fixed_amount(program),
                'product_uom_qty': 1.0,
                'product_uom': program.discount_line_product_id.uom_id.id,
                'is_reward_line': True,
                'tax_id': [(4, tax.id, False) for tax in taxes],
            }]
        reward_dict = {}
        lines = self._get_paid_order_lines()
        amount_total = sum(self._get_base_order_lines(program).mapped('price_subtotal'))
        if program.discount_apply_on == 'cheapest_product':
            line = self._get_cheapest_line(program)
            if line:
                discount_line_amount = min(line.price_reduce * (program.discount_percentage / 100), amount_total)
                if discount_line_amount:
                    taxes = self.fiscal_position_id.map_tax(line.tax_id)

                    reward_dict[line.tax_id] = {
                        'name': _("Discount: %s", program.name),
                        'product_id': program.discount_line_product_id.id,
                        'price_unit': - discount_line_amount if discount_line_amount > 0 else 0,
                        'product_uom_qty': 1.0,
                        'product_uom': program.discount_line_product_id.uom_id.id,
                        'is_reward_line': True,
                        'tax_id': [(4, tax.id, False) for tax in taxes],
                    }
            else:
                # self.promo_code = False
                program.check_coupon = False
                self.check_status_promo = True
                # program.write({'promo_code': p_coupn})
                self.code_promo_program_id = False
                program.write({'promo_code': program.promo_code})

        elif program.discount_apply_on in ['specific_products', 'on_order']:
            if program.discount_apply_on == 'specific_products':
                # We should not exclude reward line that offer this product since we need to offer only the discount on the real paid product (regular product - free product)
                free_product_lines = self.env['coupon.program'].search([('reward_type', '=', 'product'), (
                    'reward_product_id', 'in', program.discount_specific_product_ids.ids)]).mapped(
                    'discount_line_product_id')
                lines = lines.filtered(
                    lambda x: x.product_id in (program.discount_specific_product_ids | free_product_lines))

            # when processing lines we should not discount more than the order remaining total
            currently_discounted_amount = 0
            for line in lines:
                discount_line_amount = min(self._get_reward_values_discount_percentage_per_line(program, line),
                                           amount_total - currently_discounted_amount)

                if discount_line_amount:

                    if line.tax_id in reward_dict:
                        reward_dict[line.tax_id]['price_unit'] -= discount_line_amount
                    else:
                        taxes = self.fiscal_position_id.map_tax(line.tax_id)

                        reward_dict[line.tax_id] = {
                            'name': _(
                                "Discount: %(program)s - On product with following taxes: %(taxes)s",
                                program=program.name,
                                taxes=", ".join(taxes.mapped('name')),
                            ),
                            'product_id': program.discount_line_product_id.id,
                            'price_unit': - discount_line_amount if discount_line_amount > 0 else 0,
                            'product_uom_qty': 1.0,
                            'product_uom': program.discount_line_product_id.uom_id.id,
                            'is_reward_line': True,
                            'tax_id': [(4, tax.id, False) for tax in taxes],
                        }
                        currently_discounted_amount += discount_line_amount

        # If there is a max amount for discount, we might have to limit some discount lines or completely remove some lines
        max_amount = program._compute_program_amount('discount_max_amount', self.currency_id)
        if max_amount > 0:
            amount_already_given = 0
            for val in list(reward_dict):
                amount_to_discount = amount_already_given + reward_dict[val]["price_unit"]
                if abs(amount_to_discount) > max_amount:
                    reward_dict[val]["price_unit"] = - (max_amount - abs(amount_already_given))
                    add_name = formatLang(self.env, max_amount, currency_obj=self.currency_id)
                    reward_dict[val]["name"] += "( " + _("limited to ") + add_name + ")"
                amount_already_given += reward_dict[val]["price_unit"]
                if reward_dict[val]["price_unit"] == 0:
                    del reward_dict[val]
        return reward_dict.values()

    def _get_reward_values_product(self, program):
        price_unit = self.order_line.filtered(lambda line: program.reward_product_id == line.product_id)[0].price_reduce
        # Take the default taxes on the reward product, mapped with the fiscal position
        taxes = program.reward_product_id.taxes_id.filtered(lambda t: t.company_id.id == self.company_id.id)
        taxes = self.fiscal_position_id.map_tax(taxes)
        return {
            'product_id': program.discount_line_product_id.id,
            'price_unit': - price_unit,
            'product_uom_qty': 1,
            'is_reward_line': True,
            'name': _("Free Product") + " - " + program.reward_product_id.name,
            'product_uom': program.reward_product_id.uom_id.id,
            'tax_id': [(4, tax.id, False) for tax in taxes],
        }


class CouponProgramme(models.Model):
    _inherit = 'coupon.program'

    new_code = fields.Char("Promo Program Code")
    code = fields.Char(required=True, readonly=False)
    exclusive_coupon = fields.Boolean(default=True, help="Customer's can't use any other coupon if this coupon is used")
    available_channels = fields.Many2many('available.channels',
                                          string="Available Channel",
                                          help="Coupon can be used only for selected channel")
    restricted_product_ids = fields.Many2many('product.template',
                                              string="Restricted Products",
                                              help="Coupon can not be applied for restricted products")

    cheapest_product_select_category_id = fields.Many2one('product.public.category', string="Product Category",
                                                          help="Coupon can be used only for selected category products"
                                                          )
    cheapest_product_select_product_id = fields.Many2one('product.template', string="Product",
                                                         help="Coupon can be used for selected product only, if is the selected product in order line",
                                                         domain="[('public_categ_ids', '=', cheapest_product_select_category_id)]")

    cheapest_product_select_category_ids = fields.Many2many('product.public.category', string="Product Category",
                                                            help="Coupon can be used only for selected category products"
                                                            )
    cheapest_product_select_product_ids = fields.Many2many('product.product', string="Product",
                                                           help="Coupon can be used for selected product only, if is the selected product in order line",
                                                           domain="[('product_tmpl_id.public_categ_ids', 'in', cheapest_product_select_category_ids)]")

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
    check_coupon = fields.Boolean(default=True)

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

    ########################################################################################

    @api.onchange('discount_specific_product_ids', 'discount_apply_on')
    def action_restrict_conflict_discount(self):
        data = []
        if self.reward_type == 'discount':
            if self.reward_product_id:
                raise ValidationError(_("Remove Reward Free product!"))
        check_product = self.restricted_product_ids.ids
        for rec in self.discount_specific_product_ids:
            data = rec.product_tmpl_id.ids
        if set(check_product).intersection(data):
            raise ValidationError(_("It is a restricted product!"))

    @api.onchange('reward_product_id')
    def action_restrict_conflict(self):
        if self.reward_type == 'product':
            if self.discount_specific_product_ids:
                raise ValidationError(_("Remove Discount product!"))
        check_product = self.restricted_product_ids.ids
        l1 = self.reward_product_id.product_tmpl_id.id
        if l1 in check_product:
            raise ValidationError(_("It is a restricted product!"))

    @api.onchange('cheapest_product_select_category_id', 'cheapest_product_select_product_id')
    def action_restrict_cheapest_conflict(self):
        if self.reward_type == 'discount':
            if self.discount_specific_product_ids:
                raise ValidationError(_("Remove Discount product!"))
        check_product = self.restricted_product_ids.ids
        l1 = self.cheapest_product_select_product_id.id
        if l1 in check_product:
            raise ValidationError(_("It is a restricted product!"))

    ####################################################################################

    def _check_promo_code(self, order, coupon_code):
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

        ###################################################################################################
        line_list = []
        order_line_count = self.env['sale.order.line'].search([('order_id', '=', order.id)])
        for rec in order_line_count:
            if not rec.bundle_option:
                line_list.append(rec.product_template_id.id)
        product_ids = self.restricted_product_ids.ids
        result = list(filter(lambda x: x in line_list, product_ids))
        if not result:
            pass
        else:
            if self.discount_apply_on == 'specific_products' and self.discount_specific_product_ids:
                check_product_ids = self.discount_specific_product_ids.product_tmpl_id.ids
                discount_list = list(filter(lambda x: x in line_list, check_product_ids))
                if discount_list:
                    pass
                else:
                    message = {'error': _('Coupon is not applicable')}
                    return message
            elif self.reward_type == 'product' and self.reward_product_id:
                reward_id = self.reward_product_id.product_tmpl_id.id
                if reward_id in line_list:
                    pass
                else:
                    message = {'error': _('Coupon is not applicable')}
                    return message
            else:
                message = {'error': _('Coupon is not applicable')}
                return message
        ##############################################################################################
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
        message = {}
        if self.maximum_use_number != 0 and self.order_count >= self.maximum_use_number:
            message = {'error': _('Promo code %s has been expired.') % (coupon_code)}
        elif not self._filter_on_mimimum_amount(order):
            message = {'error': _(
                'A minimum of %(amount)s %(currency)s should be purchased to get the reward',
                amount=self.rule_minimum_amount,
                currency=self.currency_id.name
            )}
        elif self.promo_code and self.promo_code == order.promo_code:
            message = {'error': _('The promo code is already applied on this order')}
        elif self in order.no_code_promo_program_ids:
            message = {'error': _('The promotional offer is already applied on this order')}
        elif not self.active:
            message = {'error': _('Promo code is invalid')}
        elif self.rule_date_from and self.rule_date_from > order.date_order or self.rule_date_to and order.date_order > self.rule_date_to:
            message = {'error': _('Promo code is expired')}
        elif order.promo_code and self.promo_code_usage == 'code_needed':
            message = {'error': _('Promotionals codes are not cumulative.')}
        elif self._is_global_discount_program() and order._is_global_discount_already_applied():
            message = {'error': _('Global discounts are not cumulative.')}
        elif self.promo_applicability == 'on_current_order' and self.reward_type == 'product' and not order._is_reward_in_order_lines(
                self):
            message = {'error': _('The reward products should be in the sales order lines to apply the discount.')}
        elif not self._is_valid_partner(order.partner_id):
            message = {'error': _("The customer doesn't have access to this reward.")}
        elif not self._filter_programs_on_products(order):
            message = {'error': _(
                "You don't have the required product quantities on your sales order. If the reward is same product quantity, please make sure that all the products are recorded on the sales order (Example: You need to have 3 T-shirts on your sales order if the promotion is 'Buy 2, Get 1 Free'.")}
        elif self.promo_applicability == 'on_current_order' and not self.env.context.get('applicable_coupon'):
            applicable_programs = order._get_applicable_programs()
            if self not in applicable_programs:
                message = {'error': _('At least one of the required conditions is not met to get the reward!')}
        return message

    def _compute_order_count(self):
        orders = self.env['sale.order.line'].search_read([
            ('product_id', 'in', self.mapped('discount_line_product_id').ids)],
            ['product_id', 'order_id'], order="product_id")
        data = {}
        for record in orders:
            if record.get('product_id') and record.get('order_id'):
                data.setdefault(record['product_id'][0], set()).add(record['order_id'][0])
        for rec in self:
            rec.order_count = len(data.get(rec.discount_line_product_id.id, []))

    def action_view_sales_orders(self):
        self.ensure_one()
        orders = self.env['sale.order.line'].search([('product_id', '=', self.discount_line_product_id.id)]).mapped(
            'order_id')
        return {
            'name': _('Sales Orders'),
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'search_view_id': [self.env.ref('sale.sale_order_view_search_inherit_quotation').id],
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', orders.ids)],
            'context': dict(self._context, create=False),
        }


class SaleCouponApplyCodes(models.TransientModel):
    _inherit = 'sale.coupon.apply.code'

    def apply_coupon(self, order, coupon_code):
        error_status = {}
        pg = False
        cd = False
        program = self.env['coupon.program'].search([('promo_code', '=', coupon_code)], limit=1)
        if program:
            if len(program.promo_code) == len(coupon_code):
                pg = True
        if program and pg:
            error_status = program._check_promo_code(order, coupon_code)
            if not error_status:
                if program.promo_applicability == 'on_next_order':
                    # Avoid creating the coupon if it already exist
                    if program.discount_line_product_id.id not in order.generated_coupon_ids.filtered(
                            lambda coupon: coupon.state in ['new', 'reserved']).mapped('discount_line_product_id').ids:
                        coupon = order._create_reward_coupon(program)
                        return {
                            'generated_coupon': {
                                'reward': coupon.program_id.discount_line_product_id.name,
                                'code': coupon.code,
                            }
                        }
                else:  # The program is applied on this order
                    order._create_reward_line(program)
                    order.code_promo_program_id = program
        else:
            coupon = self.env['coupon.coupon'].search([('code', 'ilike', coupon_code)], limit=1)
            if coupon:
                if len(coupon.code) == len(coupon_code):
                    cd = True
            if coupon and cd:
                error_status = coupon._check_coupon_code(order)
                if not error_status:
                    order._create_reward_line(coupon.program_id)
                    order.applied_coupon_ids += coupon
                    coupon.write({'state': 'used'})
            else:
                error_status = {'not_found': _('This coupon is invalid (%s).') % (coupon_code)}
        return error_status
