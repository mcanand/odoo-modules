# -*- coding: utf-8 -*-

import logging
import urllib
import re

from odoo import models, fields, _
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools import html2plaintext

_logger = logging.getLogger(__name__)


class WhatsappTemplate(models.Model):
    _name = 'whatsapp.template'
    _description = 'Message default in Whatsapp'

    name = fields.Char(string="Title Template")
    template_messege = fields.Text(string="Message Template")
    category = fields.Selection([ ('partner', 'Partner/Contact'),
                                  ('sale', 'Sale/Quoting'),
                                  ('invoice', 'Invoice'),
                                  ('delivery', 'Delivery/Stock'),
                                  ('lead', 'CRM/Marketing'),
                                  ('purchase', 'Provider'),
                                  ('resuser', 'Res/User'),
                                  ('events', 'Events'),
                                  ('other', 'Other')], default='other', string="Category")