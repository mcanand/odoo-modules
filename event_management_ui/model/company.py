from odoo import fields, models, api, _


class CompanyInherit(models.Model):
    _inherit = 'res.company'

    geo_lat = fields.Float(String="Latitude")
    geo_lng = fields.Float(String="Longitude")
    delivery_radius = fields.Float(String="Delivery Radius")


