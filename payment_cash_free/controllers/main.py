# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint

import requests
from werkzeug import urls
from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class CashFreeController(http.Controller):
    _return_url = '/payment/cashfree/return/'
    _webhook_url = '/payment/cashfree/webhook/'

    @http.route(
        _return_url, type='http', auth='public', methods=['GET', 'POST'], csrf=False,
        save_session=False
    )
    def cashfree_return_from_checkout(self, **pdt_data):
        _logger.info("handling redirection from cashfree with data:\n%s", pprint.pformat(pdt_data))
        """pt data link id will come"""
        if not pdt_data:  # The customer has canceled or paid then clicked on "Return to Merchant"
            pass  # Redirect them to the status page to browse the (currently) draft transaction
        else:
            # Check the origin of the notification
            tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
                'cashfree', pdt_data
            )
            try:
                notification_data = self._verify_pdt_cash_free_payment(pdt_data, tx_sudo)
            except Forbidden:
                _logger.exception("could not verify the origin of the data; discarding it")
            else:
                # Handle the notification data
                tx_sudo._handle_notification_data('cashfree', notification_data)

        return request.redirect('/payment/status')

    def _verify_pdt_cash_free_payment(self, pdt_data, tx_sudo):
        if pdt_data:
            endpoint = 'links/' + tx_sudo.cash_free_reference
            url = tx_sudo._cash_free_url() + endpoint
            headers = tx_sudo._cash_free_payment_link_header()
            try:
                response = requests.get(url, headers=headers)
                response = response.json()
                return response
            except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError):
                raise Forbidden("cashfree: Encountered an error when verifying payment")
