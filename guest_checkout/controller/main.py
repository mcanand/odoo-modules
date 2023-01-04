from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
import requests


class WebsiteSale(WebsiteSale):

    def _checkout_form_save(self, mode, checkout, all_values):
        """if a guest try to shop with same email then
        create a record as delivery contact and add it to the
        child of the existing partner
        and creates a user in res_users
        """
        vals = {'login': checkout.get('email'),
                'name': checkout.get('name'),
                'phone': checkout.get('phone'),
                'street': checkout.get('street'),
                'street2': checkout.get('street2'),
                'zip': checkout.get('zip'),
                'city': checkout.get('city'),
                'country_id': checkout.get('country_id'),
                'sel_groups_1_9_10': 9,
                }
        res_partner = request.env['res.partner'].sudo()
        partner = res_partner.search([('email', '=', checkout.get('email')), ('type', '=', 'contact')], limit=1)
        if partner:
            vals.update({'partner_id': partner.id})
            checkout.update({'type': 'delivery', 'parent_id': partner.id})
            res_partner.create(checkout)
            self.create_user(vals)
            return partner.id
        else:
            res = super(WebsiteSale, self)._checkout_form_save(mode, checkout, all_values)
            vals.update({'partner_id': partner.id})
            self.create_user(vals)
            return res

    def create_user(self, vals):
        res_users = request.env['res.users'].sudo()
        if not res_users.search([('login', '=', vals.get('login'))]):
            partner = request.env['res.partner'].sudo().search(
                [('email', '=', vals.get('login')), ('type', '=', 'contact')], limit=1)
            if partner:
                vals.update({'partner_id': partner.id})
            res_users.create(vals)


class CountryPoneCodeCheckout(http.Controller):
    @http.route('/get/country/phone_code',type='json',auth='public')
    def country_phone_code(self):
        country = self.get_current_country()
        return country.phone_code
    def get_ip(self):
        response = requests.get('https://api64.ipify.org?format=json').json()
        return response["ip"]

    def get_current_country(self):
        ip_address = self.get_ip()
        response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
        country = request.env['res.country'].sudo().search([('code', '=', response.get('country_code'))])
        return country