import logging

from werkzeug import urls
from werkzeug.urls import url_encode, url_join
from odoo import _, api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare
from odoo.addons.payment import utils as payment_utils

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    cash_free_reference = fields.Char(string='cash free reference')
    cash_free_payment_link = fields.Char(string='cash free reference')

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Alipay-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'cashfree':
            return res
        endpoint = 'links'
        url = self._cash_free_url() + 'links'
        payload = self._cash_free_payment_link_payload()
        header = self._cash_free_payment_link_header()
        response = self.provider_id._cash_free_create_payment_link(url, payload, header)
        pay_link = response.get('link_url')
        base_url = self.provider_id.get_base_url()
        converted_amount = payment_utils.to_minor_currency_units(self.amount, self.currency_id)
        self.write({'cash_free_payment_link':pay_link})
        rendering_values = {
            'key_id': self.provider_id.id,
            'name': self.company_id.name,
            'description': self.reference,
            # 'company_logo': url_join(base_url, f'web/image/res.company/{self.company_id.id}/logo'),
            'order_id': self.sale_order_ids.id,
            'amount': self.sale_order_ids.amount_total,
            'currency': 'INR',
            'partner_name': self.partner_name,
            'partner_email': self.partner_email,
            'partner_phone': self.partner_id.phone,
            'api_url': pay_link
        }
        return rendering_values

    def _cash_free_url(self):
        provider = self.provider_id
        if provider:
            if provider.state == 'test':
                return provider.cashfree_test_url
            elif provider.state == 'enabled':
                return provider.cashfree_production_url

    def _cash_free_payment_link_payload(self):
        base_url = self.provider_id.get_base_url()
        return_url_params = {'link_id': "PT" + str(self.id)}
        payload = {
            "customer_details": {
                "customer_phone": str(self.partner_id.phone),
                "customer_email": self.partner_id.email,
                "customer_name": self.partner_id.name
            },
            "link_notify": {
                "send_sms": True,
                "send_email": True
            },
            "link_meta": {
                "upi_intent": True,
                "return_url": base_url + "payment/cashfree/return?link_id = {link_id}",

                # "return_url": url_join(base_url, f'{"payment/cashfree/return"}?{url_encode(return_url_params)}'),

            },
            "link_partial_payments": False,
            "link_purpose": "order payment",
            "link_currency": "INR",
            "link_amount": self.sale_order_ids.amount_total,
            "link_id": "PT" + str(self.id)
        }
        self.write({'cash_free_reference': "PT" + str(self.id)})
        return payload

    def _cash_free_payment_link_header(self):
        headers = {
            "accept": "application/json",
            "x-client-id": self.provider_id.cashfree_app_id,
            "x-client-secret": self.provider_id.cashfree_secret_key,
            "x-api-version": self.provider_id.cashfree_api_version,
            "content-type": "application/json"
        }
        return headers

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of payment to find the transaction based on cashfree data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'cashfree' or len(tx) == 1:
            return tx

        link_id = notification_data.get('link_id ')
        tx = self.search([('cash_free_reference', '=', link_id.split(' ')), ('provider_code', '=', 'cashfree')])
        if not tx:
            raise ValidationError(
                "cashfree: " + _("No transaction found matching reference %s.", link_id)
            )
        return tx

    def _process_notification_data(self, notification_data):
        """ Override of payment to process the transaction based on Paypal data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        res = super()._process_notification_data(notification_data)
        if self.provider_code != 'cashfree':
            return res
        if notification_data:
            payment_status = notification_data.get('link_status')
            if payment_status == 'ACTIVE':
                "cancel the payment"
                self._set_canceled()
                # self._set_pending(state_message=notification_data.get('link_status'))
            elif payment_status == 'PAID':
                self._set_done()
            elif payment_status == 'CANCELLED':
                self._set_canceled()
            else:
                _logger.info(
                    "received data with invalid payment status (%s) for transaction with id %s",
                    payment_status, self.cash_free_reference
                )
