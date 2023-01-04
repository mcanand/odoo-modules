# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging
import psycopg2
import time
from odoo.tools import float_is_zero
from odoo import models, fields, api, tools, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from datetime import datetime
from operator import itemgetter
from timeit import itertools
from itertools import groupby


from datetime import datetime
from dateutil import relativedelta
import pprint
import psycopg2
from odoo import api, exceptions, fields, models, _, SUPERUSER_ID
from odoo.tools import consteq, float_round, image_process, ustr
from odoo.http import request
_logger = logging.getLogger(__name__)


def _partner_format_address(address1=False, address2=False):
    return ' '.join((address1 or '', address2 or '')).strip()



def _partner_split_name(partner_name):
    return [' '.join(partner_name.split()[:-1]), ' '.join(partner_name.split()[-1:])]


def create_missing_journal_for_acquirers(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['payment.acquirer']._create_missing_journal_for_acquirers()


class WebsiteSale(models.Model):
    _inherit = 'website'

    def sale_product_domain(self):
        return [("sale_ok", "=", True), ("is_optional_product", "=", False)] + self.get_current_website().website_domain()

class PaymentAcquirerrepartner(models.Model):
    """ Acquirer Model. Each specific acquirer can extend the model by adding
    """
    _inherit = 'sale.order'

    public_partner = fields.Many2one('res.partner')
    email_confirmation = fields.Boolean('email_confirmation', default=False)
    sms_confirmation = fields.Boolean('sms_confirmation', default=False)
    contactless_confirmation = fields.Boolean('contactless_confirmation', default=False, track_visibility="on_change")


class PaymentAcquirer(models.Model):
    """ Acquirer Model. Each specific acquirer can extend the model by adding
    """
    _inherit = 'payment.acquirer'


    def render(self, reference, amount, currency_id, partner_id=False, values=None):
        """ Renders the form template of the given acquirer as a qWeb template.
        :param string reference: the transaction reference
        :param float amount: the amount the buyer has to pay
        :param currency_id: currency id
        :param dict partner_id: optional partner_id to fill values
        :param dict values: a dictionary of values for the transction that is
        given to the acquirer-specific method generating the form values

        All templates will receive:

         - acquirer: the payment.acquirer browse record
         - user: the current user browse record
         - currency_id: id of the transaction currency
         - amount: amount of the transaction
         - reference: reference of the transaction
         - partner_*: partner-related values
         - partner: optional partner browse record
         - 'feedback_url': feedback URL, controler that manage answer of the acquirer (without base url) -> FIXME
         - 'return_url': URL for coming back after payment validation (wihout base url) -> FIXME
         - 'cancel_url': URL if the client cancels the payment -> FIXME
         - 'error_url': URL if there is an issue with the payment -> FIXME
         - context: Odoo context

        """
        if values is None:
            values = {}

        if not self.view_template_id:
            return None

        values.setdefault('return_url', '/payment/process')
        # reference and amount
        values.setdefault('reference', reference)
        amount = float_round(amount, 2)
        values.setdefault('amount', amount)

        # currency id
        currency_id = values.setdefault('currency_id', currency_id)
        if currency_id:
            currency = self.env['res.currency'].browse(currency_id)
        else:
            currency = self.env.company.currency_id
        values['currency'] = currency

        # Fill partner_* using values['partner_id'] or partner_id argument
        partner_id = values.get('partner_id', partner_id)
        billing_partner_id = values.get('billing_partner_id', partner_id)
        order = request.website.sale_get_order()
        if order:
            if order.partner_id:
                partner_id = order.partner_id.id
                if not request.session.uid:
                    partner_id = order.public_partner.id
                    if not partner_id:
                        partner_id = order.partner_id.id
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            if partner_id != billing_partner_id:
                billing_partner = self.env['res.partner'].browse(billing_partner_id)
            else:
                billing_partner = partner
            values.update({
                'partner': partner,
                'partner_id': partner_id,
                'partner_name': partner.name,
                'partner_lang': partner.lang,
                'partner_email': partner.email,
                'partner_zip': partner.zip,
                'partner_city': partner.city,
                'partner_address': _partner_format_address(partner.street, partner.street2),
                'partner_country_id': partner.country_id.id or self.env['res.company']._company_default_get().country_id.id,
                'partner_country': partner.country_id,
                'partner_phone': partner.phone,
                'partner_state': partner.state_id,
                'billing_partner': billing_partner,
                'billing_partner_id': billing_partner_id,
                'billing_partner_name': billing_partner.name,
                'billing_partner_commercial_company_name': billing_partner.commercial_company_name,
                'billing_partner_lang': billing_partner.lang,
                'billing_partner_email': billing_partner.email,
                'billing_partner_zip': billing_partner.zip,
                'billing_partner_city': billing_partner.city,
                'billing_partner_address': _partner_format_address(billing_partner.street, billing_partner.street2),
                'billing_partner_country_id': billing_partner.country_id.id,
                'billing_partner_country': billing_partner.country_id,
                'billing_partner_phone': billing_partner.phone,
                'billing_partner_state': billing_partner.state_id,
            })
        if values.get('partner_name'):
            values.update({
                'partner_first_name': _partner_split_name(values.get('partner_name'))[0],
                'partner_last_name': _partner_split_name(values.get('partner_name'))[1],
            })
        if values.get('billing_partner_name'):
            values.update({
                'billing_partner_first_name': _partner_split_name(values.get('billing_partner_name'))[0],
                'billing_partner_last_name': _partner_split_name(values.get('billing_partner_name'))[1],
            })

        # Fix address, country fields
        if not values.get('partner_address'):
            values['address'] = _partner_format_address(values.get('partner_street', ''), values.get('partner_street2', ''))
        if not values.get('partner_country') and values.get('partner_country_id'):
            values['country'] = self.env['res.country'].browse(values.get('partner_country_id'))
        if not values.get('billing_partner_address'):
            values['billing_address'] = _partner_format_address(values.get('billing_partner_street', ''), values.get('billing_partner_street2', ''))
        if not values.get('billing_partner_country') and values.get('billing_partner_country_id'):
            values['billing_country'] = self.env['res.country'].browse(values.get('billing_partner_country_id'))

        # compute fees
        fees_method_name = '%s_compute_fees' % self.provider
        if hasattr(self, fees_method_name):
            fees = getattr(self, fees_method_name)(values['amount'], values['currency_id'], values.get('partner_country_id'))
            values['fees'] = float_round(fees, 2)

        # call <name>_form_generate_values to update the tx dict with acqurier specific values
        cust_method_name = '%s_form_generate_values' % (self.provider)
        if hasattr(self, cust_method_name):
            method = getattr(self, cust_method_name)
            values = method(values)

        values.update({
            'tx_url': self._context.get('tx_url', self.get_form_action_url()),
            'submit_class': self._context.get('submit_class', 'btn btn-link'),
            'submit_txt': self._context.get('submit_txt'),
            'acquirer': self,
            'user': self.env.user,
            'context': self._context,
            'type': values.get('type') or 'form',
        })

        _logger.info('payment.acquirer.render: <%s> values rendered for form payment:\n%s', self.provider, pprint.pformat(values))
        return self.view_template_id._render(values, engine='ir.qweb')