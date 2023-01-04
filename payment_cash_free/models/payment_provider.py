import logging
import uuid
import pprint

import requests
from werkzeug.urls import url_encode, url_join, url_parse

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('cashfree', "Cash Free")], ondelete={'cashfree': 'set default'})
    cashfree_app_id = fields.Char(string="App ID",
                                  help="app id of cash free payment", required_if_provider='cashfree')
    cashfree_secret_key = fields.Char(string="Secret Key", required_if_provider='cashfree')

    cashfree_test_url = fields.Char(string='Test url')
    cashfree_production_url = fields.Char(string='Production url')
    cashfree_api_version = fields.Char(string='version')

    def _cash_free_create_payment_link(self, url, payload=None, headers=None, method='POST'):
        self.ensure_one()
        try:
            if method == 'POST':
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    try:
                        response.raise_for_status()
                    except requests.exceptions.HTTPError:
                        _logger.exception(
                            "Invalid API request at %s with data:\n%s", url, pprint.pformat(payload),
                        )
                        raise ValidationError("Cash Free: " + _(
                            "The communication with the API failed. cash free gave us the following "
                            "information: '%s'", response.json().get('message')
                        ))
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            _logger.exception("Unable to reach endpoint at %s", url)
            raise ValidationError(
                "cashfree: " + _("Could not establish the connection to the API.")
            )
        return response.json()


