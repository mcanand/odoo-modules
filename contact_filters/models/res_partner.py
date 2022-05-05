from odoo import models, fields, api, _
import logging
from datetime import date
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

# MASS_MAILING_BUSINESS_MODELS = [
#     'crm.lead',
#     'event.registration',
#     'hr.applicant',
#     'res.partner',
#     'event.track',
#     'sale.order',
#     'mailing.list',
#     'mailing.contact',
# ]
#
#
# class MassMailing(models.Model):
#     """ MassMailing models a wave of emails for a mass mailign campaign.
#     A mass mailing is an occurence of sending emails. """
#     _inherit = 'mailing.mailing'
#
#     mailing_model_id = fields.Many2one(
#         'ir.model', string='Recipients Model', ondelete='cascade', required=True,
#         domain=[('model', 'in', MASS_MAILING_BUSINESS_MODELS)],
#         default=lambda self: self.env.ref('mass_mailing.model_mailing_list').id)


class Loyalist(models.Model):
    _name = 'loyalist.contacts'

    name = fields.Char()
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()
    loyalist_contacts_id = fields.Many2one()


class Guest(models.Model):
    _name = 'guest.contacts'

    name = fields.Char()
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()
    guest_contacts_id = fields.Many2one()


# class NotPurchaseIn30Days(models.Model):
#     _name = 'not.purchase.thirty.d'
#
#     name = fields.Char()
#     email = fields.Char()
#     phone = fields.Char()
#     mobile = fields.Char()
#     partner_id = fields.Many2one()
#
#
# class NotPurchaseIn60Days(models.Model):
#     _name = 'not.purchase.sixty.d'
#
#     name = fields.Char()
#     email = fields.Char()
#     phone = fields.Char()
#     mobile = fields.Char()
#     partner_id = fields.Many2one()
#
#
# class NotPurchaseIn90Days(models.Model):
#     _name = 'not.purchase.ninety.d'
#
#     name = fields.Char()
#     email = fields.Char()
#     phone = fields.Char()
#     mobile = fields.Char()
#     partner_id = fields.Many2one()
#
#
# class OrderdPickupOnly(models.Model):
#     _name = 'order.pickup.only'
#
#     name = fields.Char()
#     email = fields.Char()
#     phone = fields.Char()
#     mobile = fields.Char()
#     partner_id = fields.Many2one()
#
#
# class OrderdDeliveryOnly(models.Model):
#     _name = 'order.delivery.only'
#
#     name = fields.Char()
#     email = fields.Char()
#     phone = fields.Char()
#     mobile = fields.Char()
#     partner_id = fields.Many2one()

#
# class CouponPurchase(models.Model):
#     _name = 'use.coupon.purchase'
#
#     name = fields.Char()
#     email = fields.Char()
#     phone = fields.Char()
#     mobile = fields.Char()
#     partner_id = fields.Many2one()


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # loyalist_contacts = fields.Many2one(string="loyalist contacts")
    loyalist_boolean = fields.Boolean(string="Loyalist Boolean", compute='get_details_for_filter')

    loyalist_contacts = fields.One2many('loyalist.contacts', 'loyalist_contacts_id')
    guest_contacts = fields.One2many('guest.contacts', 'guest_contacts_id')
    # not_purchased_30_days = fields.One2many('not.purchase.thirty.d', 'partner_id')
    # not_purchased_60_days = fields.One2many('not.purchase.sixty.d', 'partner_id')
    # not_purchased_90_days = fields.One2many('not.purchase.ninety.d', 'partner_id')
    # order_pickup_only = fields.One2many('order.pickup.only', 'partner_id')
    # order_delivery_only = fields.One2many('order.delivery.only', 'partner_id')
    # used_a_coupon_to_purchase = fields.One2many('use.coupon.purchase', 'partner_id')

    def click_btn_contact(self):
        self.get_loyalist_accounts()
        self.get_guest_accounts()
        # self.get_not_purchase_in_30_days()
        # self.get_not_purchase_in_60_days()
        # self.get_not_purchase_in_90_days()
        # self.get_order_pickup_only()
        # self.get_order_delivery_only()
        # self.get_use_coupon_purchase()
        # res = {'warning': {
        #     'title': _('Warning'),
        #     'message': _('My warning message.')
        # }
        # }
        return True

    # def get_use_coupon_purchase(self):
    #     partners = self.search([])
    #     for i in partners:
    #         if i.sale_order_ids.applied_coupon_ids:
    #             self.env['use.coupon.purchase'].create({'partner_id': i.id,
    #                                                 'name': i.name,
    #                                                 'phone': i.phone,
    #                                                 'mobile': i.mobile})

    # def get_not_purchase_in_30_days(self):
    #     thirty_days = date.today() - relativedelta(days=30)
    #     partners = self.search([('sale_order_ids.date_order', '<=', thirty_days)])
    #
    #     for i in partners:
    #         self.env['not.purchase.thirty.d'].create({'partner_id': i.id,
    #                                                   'name': i.name,
    #                                                   'phone': i.phone,
    #                                                   'mobile': i.mobile})
    #
    # def get_not_purchase_in_60_days(self):
    #     sixty_days = date.today() - relativedelta(days=60)
    #     partners = self.search([('sale_order_ids.date_order', '<=', sixty_days)])
    #     for i in partners:
    #         self.env['not.purchase.sixty.d'].create({'partner_id': i.id,
    #                                                  'name': i.name,
    #                                                  'phone': i.phone,
    #                                                  'mobile': i.mobile})
    #
    # def get_not_purchase_in_90_days(self):
    #     ninety_days = date.today() - relativedelta(days=90)
    #     partners = self.search([('sale_order_ids.date_order', '<=', ninety_days)])
    #     for i in partners:
    #         self.env['not.purchase.ninety.d'].create({'partner_id': i.id,
    #                                                   'name': i.name,
    #                                                   'phone': i.phone,
    #                                                   'mobile': i.mobile})

    def get_loyalist_accounts(self):
        loyalist = self.env['loyalist.contacts'].search([])
        loyalist_partners = self.search([('user_ids', '!=', False)])
        if len(loyalist) != len(loyalist_partners):
            for i in loyalist_partners:
                self.env['loyalist.contacts'].create({'loyalist_contacts_id': i.id,
                                                      'name': i.name,
                                                      'phone': i.phone,
                                                      'mobile': i.mobile})

    def get_guest_accounts(self):
        loyalist = self.env['guest.contacts'].search([])
        guest_partners = self.search([('user_ids', '=', False)])
        if len(loyalist) != len(guest_partners):
            for i in guest_partners:
                self.env['guest.contacts'].create({'guest_contacts_id': i.id,
                                                   'name': i.name,
                                                   'phone': i.phone,
                                                   'mobile': i.mobile})
    #
    # def get_order_pickup_only(self):
    #     partners = self.search([('sale_order_ids.website_delivery_type', '=', 'pickup'),
    #                             ('sale_order_ids.state', 'not in', ('draft', 'sent', 'cancel'))])
    #     for i in partners:
    #         self.env['order.pickup.only'].create({'partner_id': i.id,
    #                                               'name': i.name,
    #                                               'phone': i.phone,
    #                                               'mobile': i.mobile})
    #
    # def get_order_delivery_only(self):
    #     partners = self.search([('sale_order_ids.website_delivery_type', '=', 'delivery'),
    #                             ('sale_order_ids.state', 'not in', ('draft', 'sent', 'cancel'))])
    #     for i in partners:
    #         self.env['order.delivery.only'].create({'partner_id': i.id,
    #                                                 'name': i.name,
    #                                                 'phone': i.phone,
    #                                                 'mobile': i.mobile})
