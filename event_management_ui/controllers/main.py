import datetime

from odoo import http, tools
from odoo.http import Controller, route, request
import requests
from datetime import time, timedelta
import calendar


class DeliveryAddressFinder(http.Controller):
    @http.route(['/find/address'], type='json', auth="public", website=True)
    def find_address(self, input):
        if input:
            company = request.env['res.company'].sudo().search([])
            comp_list = []
            for company in company:
                if company.name and input in company.name.lower() or company.street and input in company.street.lower() or company.street2 and input in company.street2.lower() or company.city and input in \
                        company.city.lower() or company.zip and input in company.zip:
                    comp_list.append({'name': company.name,
                                      'street': company.street,
                                      'street2': company.street2,
                                      'city': company.city,
                                      'zip': company.zip
                                      })
            return comp_list


class DeliveryLocation(http.Controller):
    @http.route(['/get/current/website'], type="json", auth="public", website=True)
    def get_current_website(self):
        company = request.env.company
        website = request.env['website'].sudo().search([('company_id', '=', company.id)], limit=1)
        vals = {
            'enable_pickup': website.is_pickup,
            'enable_delivery': website.is_delivery
        }
        return vals

    @http.route(['/delivery/date/start'], type='json', auth="public", website=True)
    def delivery_date_change_start(self):
        today = datetime.datetime.today()
        weekday = calendar.day_name[today.weekday()]
        website = request.env['website'].sudo()._get_current_website()
        if weekday == 'Monday':
            vals = {
                'time_from': website.time_from_delivery_monday,
                'time_to': website.time_to_delivery_monday
            }
            return vals

    @http.route(['/delivery/date/change'], type='json', auth="public", website=True)
    def delivery_date_change(self, date):
        year, month, day = (int(x) for x in date.split('-'))
        date = datetime.date(year, month, day)
        weekday = date.strftime("%A")
        website = request.env['website'].sudo()._get_current_website()
        location_vals = {}
        if weekday == 'Sunday':
            vals = self.get_sunday_time(website, location_vals)
            return vals
        if weekday == 'Monday':
            vals = self.get_monday_time(website, location_vals)
            return vals
        if weekday == 'Tuesday':
            vals = self.get_tuesday_time(website, location_vals)
            return vals
        if weekday == 'Wednesday':
            vals = self.get_wednesday_time(website, location_vals)
            return vals
        if weekday == 'Thursday':
            vals = self.get_thursday_time(website, location_vals)
            return vals
        if weekday == 'Friday':
            vals = self.get_friday_time(website, location_vals)
            return vals
        if weekday == 'Saturday':
            vals = self.get_saturday_time(website, location_vals)
            return vals

    @http.route(['/delivery/location'], type='http', auth="public", website=True)
    def delivery_location(self):
        company = request.env.company
        user_tz = request.env.user.tz
        today = datetime.datetime.now().date()
        tomorrow = (datetime.datetime.strptime(str(today), "%Y-%m-%d") + timedelta(days=1)).date()
        location_vals = {'company': company,
                         'today': today,
                         'tomorrow': tomorrow,
                         }
        self.get_delivery_time(location_vals)
        return request.render('event_management_ui.event_management_location', location_vals)

    def get_delivery_time(self, location_vals):
        t_today = datetime.datetime.today()
        weekday = calendar.day_name[t_today.weekday()]
        website = request.env['website'].sudo()._get_current_website()
        if weekday == 'Sunday':
            self.get_sunday_time(website, location_vals)
            return location_vals
        if weekday == 'Monday':
            self.get_monday_time(website, location_vals)
            return location_vals
        if weekday == 'Tuesday':
            self.get_tuesday_time(website, location_vals)
            return location_vals
        if weekday == 'Wednesday':
            self.get_wednesday_time(website, location_vals)
            return location_vals
        if weekday == 'Thursday':
            self.get_thursday_time(website, location_vals)
            return location_vals
        if weekday == 'Friday':
            self.get_friday_time(website, location_vals)
            return location_vals
        if weekday == 'Saturday':
            self.get_saturday_time(website, location_vals)
            return location_vals

    def get_sunday_time(self, website, location_vals):
        time_from = self.convert_float_time(website.time_from_delivery_sunday)
        time_to = self.convert_float_time(website.time_to_delivery_sunday)
        location_vals.update({
            'time_from': time_from,
            'time_to': time_to
        })
        return location_vals

    def get_monday_time(self, website, location_vals):
        time_from = self.convert_float_time(website.time_from_delivery_monday)
        time_to = self.convert_float_time(website.time_to_delivery_monday)
        location_vals.update({
            'time_from': time_from,
            'time_to': time_to
        })
        return location_vals

    def get_tuesday_time(self, website, location_vals):
        time_from = self.convert_float_time(website.time_from_delivery_tuesday)
        time_to = self.convert_float_time(website.time_to_delivery_tuesday)
        location_vals.update({
            'time_from': time_from,
            'time_to': time_to
        })
        return location_vals

    def get_wednesday_time(self, website, location_vals):
        time_from = self.convert_float_time(website.time_from_delivery_wednesday)
        time_to = self.convert_float_time(website.time_to_delivery_wednesday)
        location_vals.update({
            'time_from': time_from,
            'time_to': time_to
        })
        return location_vals

    def get_thursday_time(self, website, location_vals):
        time_from = self.convert_float_time(website.time_from_delivery_thursday)
        time_to = self.convert_float_time(website.time_to_delivery_thursday)
        location_vals.update({
            'time_from': time_from,
            'time_to': time_to
        })
        return location_vals

    def get_friday_time(self, website, location_vals):
        time_from = self.convert_float_time(website.time_from_delivery_friday)
        time_to = self.convert_float_time(website.time_to_delivery_friday)
        location_vals.update({
            'time_from': time_from,
            'time_to': time_to
        })
        return location_vals

    def get_saturday_time(self, website, location_vals):
        time_from = self.convert_float_time(website.time_from_delivery_saturday)
        time_to = self.convert_float_time(website.time_to_delivery_saturday)
        location_vals.update({
            'time_from': time_from,
            'time_to': time_to
        })
        return location_vals

    def convert_float_time(self, value):
        time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(value) * 60, 60))
        return time

    @http.route(['/company/location'], type="json", auth="public", website=True)
    def company_locations(self):
        companies = request.env['res.company'].search([])
        vals = []
        for rec in companies:
            vals.append({
                'name': rec.name,
                'company_id': rec.id,
                'latitude': rec.geo_lat,
                'longitude': rec.geo_lng,
                'delivery_radius': rec.delivery_radius,
            })
        return vals
