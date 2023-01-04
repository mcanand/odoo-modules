from odoo import fields, http, _
from odoo.http import request
from geopy.geocoders import Nominatim
import requests
import werkzeug

from odoo.addons.website_event.controllers.main import WebsiteEventController


class WebsiteEventBoothController(WebsiteEventController):
    @http.route(['/event/<model("event.event"):event>/registration/new'], type='json', auth="public", methods=['POST'],
                website=True)
    def registration_new(self, event, **post):
        tickets = self._process_tickets_form(event, post)
        availability_check = True
        if event.seats_limited:
            ordered_seats = 0
            for ticket in tickets:
                ordered_seats += ticket['quantity']
            if event.seats_available < ordered_seats:
                availability_check = False
        if not tickets:
            return False
        default_first_attendee = {}
        if not request.env.user._is_public():
            default_first_attendee = {
                "name": request.env.user.name,
                "email": request.env.user.email,
                "phone": request.env.user.mobile or request.env.user.phone,
            }
        else:
            visitor = request.env['website.visitor']._get_visitor_from_request()
            if visitor.email:
                default_first_attendee = {
                    "name": visitor.name,
                    "email": visitor.email,
                    "phone": visitor.mobile,
                }
        return request.env['ir.ui.view']._render_template("website_event.registration_attendee_details", {
            'tickets': tickets,
            'event': event,
            'country': self.get_current_country(),
            'availability_check': availability_check,
            'default_first_attendee': default_first_attendee,
        })

    def get_ip(self):
        response = requests.get('https://api64.ipify.org?format=json').json()
        return response["ip"]

    def get_current_country(self):
        ip_address = self.get_ip()
        response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
        country = request.env['res.country'].sudo().search([('code', '=', response.get('country_code'))])
        return country

    @http.route(['''/event/<model("event.event"):event>/registration/confirm'''], type='http', auth="public",
                methods=['POST'], website=True)
    def registration_confirm(self, event, **post):
        registrations = self._process_attendees_form(event, post)
        self.create_user(registrations, post)
        attendees_sudo = self._create_attendees_from_registration_post(event, registrations)
        return request.redirect(('/event/%s/registration/success?' % event.id) + werkzeug.urls.url_encode(
            {'registration_ids': ",".join([str(id) for id in attendees_sudo.ids])}))

    def create_user(self, reg, post):
        for reg in reg:
            country = request.env['res.country'].sudo().search([('id', '=', reg.get('country_id'))])
            login = str(country.phone_code) + reg.get('phone')
            vals = {'login': login,
                    'name': reg.get('name') if reg.get('name') else "",
                    'email': reg.get('email') if reg.get('email') else "",
                    'mobile': reg.get('phone') if reg.get('phone') else "",
                    'country_id': reg.get('country_id') if reg.get('country_id') else "",
                    'sel_groups_1_9_10': 9,
                    'street': reg.get('street') if reg.get('street') else "",
                    'street2': reg.get('street2') if reg.get('street2') else "",
                    'zip': reg.get('zip') if reg.get('zip') else "",
                    'city': reg.get('city') if reg.get('city') else "",
                    'receive_offer': post.get('1-offer') if post.get('1-offer') else False,
                    'newsletter': post.get('1-newsletter') if post.get('1-newsletter') else False,

                    }
            res_users = request.env['res.users'].sudo()
            check1 = res_users.search([('login', '=', vals.get('login'))])
            check2 = res_users.search([('login', '=', reg.get('email'))])
            if not check1 and not check2:
                res_user = res_users.create(vals)
                if res_user.partner_id:
                    partner_val = {'name': reg.get('name'),
                                   'email': reg.get('email') if reg.get('email') else "",
                                   'mobile': reg.get('phone'),
                                   'country_id': reg.get('country_id'),
                                   'street': reg.get('street') if reg.get('street') else "",
                                   'street2': reg.get('street2') if reg.get('street2') else "",
                                   'zip': reg.get('zip') if reg.get('zip') else "",
                                   'city': reg.get('city') if reg.get('city') else "", }
                    res_user.partner_id.write(partner_val)
