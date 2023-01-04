from odoo import fields, models, api, _


class WebsiteInherit(models.Model):
    _inherit = 'website'

    is_pickup = fields.Boolean(string="Enable Pickup")
    is_delivery = fields.Boolean(string="Enable Delivery")

    # DELIVERY Timings

    time_from_delivery_sunday = fields.Float('From')
    time_to_delivery_sunday = fields.Float('To')

    time_from_delivery_monday = fields.Float('From')
    time_to_delivery_monday = fields.Float('To')

    time_from_delivery_tuesday = fields.Float('From')
    time_to_delivery_tuesday = fields.Float('To')

    time_from_delivery_wednesday = fields.Float('From')
    time_to_delivery_wednesday = fields.Float('To')

    time_from_delivery_thursday = fields.Float('From')
    time_to_delivery_thursday = fields.Float('To')

    time_from_delivery_friday = fields.Float('From')
    time_to_delivery_friday = fields.Float('To')

    time_from_delivery_saturday = fields.Float('From')
    time_to_delivery_saturday = fields.Float('To')

    def _get_current_website(self):
        company = self.env.company
        website = self.search([('company_id', '=', company.id)], limit=1)
        return website
