# -*- coding: utf-8 -*-

import logging
from odoo import fields, models
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import werkzeug.urls
_logger = logging.getLogger(__name__)


class ProTemplate(models.Model):
    _inherit = "product.template"

    website_sequence_product = fields.Integer()


class DeliveryConfigSetting(models.Model):
    _inherit = "res.company"

    delivery_location = fields.Many2many('delivery.location', 'name')
    delivery_radius = fields.Float(string="Delivery Radius", default=5.0, digits=(16, 2))
    latitude = fields.Float(string='Geo latitude', digits=(16, 5))
    longitude = fields.Float(string='Geo Longitude', digits=(16, 5))

    def google_map_dynamic_link(self):
        google_maps_api_key = self.env['website'].get_current_website().google_maps_api_key
        if not google_maps_api_key:
            return False
        company = self.env.company
        center = '%s, %s %s, %s' % (self.street or '', self.city or '', self.zip or '', self.country_id.display_name or ''),
        params = 'https://www.google.com/maps/embed/v1/place?key='+str(google_maps_api_key)+'&q='+str(center)
        print(params)
        return params


class DeliverLocations(models.Model):
    _name = 'delivery.location'

    name = fields.Char(string="Area")
    delivery_radius = fields.Float(string="Delivery Radius", default=5.0, digits=(16, 2))
    latitude = fields.Float(string='Geo latitude', digits=(16, 5))
    longitude = fields.Float(string='Geo Longitude', digits=(16, 5))


    @api.model
    def create(self, vals):
        location = super(DeliverLocations, self).create(vals)
        latitude = location.latitude
        longitude = location.longitude
        if not -90 <= latitude <= +90:
            raise ValidationError(_('Invalid Latitude.'))
        if not -180 <= longitude <= 180:
            raise ValidationError(_('Invalid Longitude.'))
        return location


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    valid_address = fields.Boolean()
    street1 = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    zip = fields.Char()

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.public_partner:
                order.partner_id = order.public_partner
                order.partner_invoice_id = order.public_partner
                order.partner_shipping_id = order.public_partner
        return res

class PartnerAddress(models.Model):
    _inherit = "res.partner"

    valid_address = fields.Boolean()
