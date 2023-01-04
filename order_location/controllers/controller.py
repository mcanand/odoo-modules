import base64
import json
import pytz
from werkzeug.exceptions import Forbidden, NotFound
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.web import Home
import geopy.distance
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from datetime import datetime
from operator import itemgetter
from timeit import itertools
from itertools import groupby
from datetime import date
from odoo import http, api, fields, models, _
import datetime
from datetime import date
from dateutil import relativedelta
from datetime import timedelta
import base64
import json
import pytz
from odoo import http
from odoo.http import request
import googlemaps
from geopy.geocoders import GoogleV3
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


class Website(Home):
    def _login_redirect(self, uid, redirect=None):
        """ Redirect regular users (employees) to the backend) and others to
        the frontend
        """
        if request.env['res.users'].browse(uid).has_group('base.group_user'):
            user = request.env.user

            if user.kitchen_screen_user == 'cook' and user.default_pos:
                try:

                    sessions = user.default_pos.session_ids.filtered(
                        lambda r: r.user_id == user.id and r.state not in ['opened', 'opening_control'])
                    if not sessions:
                        user.default_pos.open_session_cb()

                    redirect = '/pos/ui?config_id=' + str(user.default_pos.id)
                except Exception as e:
                    redirect = '/'
            else:
                redirect = '/'
        return super()._login_redirect(uid, redirect=redirect)


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, **post):
        super(WebsiteSale, self).cart(**post)
        return request.redirect("/shop")

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True, sitemap=False)
    def confirm_order(self, **post):
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection
        # try:
        order.onchange_partner_shipping_id()
        order.order_line._compute_tax_id()
        request.session['sale_last_order_id'] = order.id
        request.website.sale_get_order(update_pricelist=True)
        extra_step = request.website.viewref('website_sale.extra_info_option')
        uid = request.session.uid
        user = order.partner_shipping_id
        partner_location = request.env['res.partner'].sudo().search([("id", "=", user.id)])
        partner_location.geo_localize()

        partner_latitude = partner_location.partner_latitude
        partner_longitude = partner_location.partner_longitude
        valid = False

        partner_loaction = (partner_latitude, partner_longitude)

        delivery_locations = request.env['delivery.location'].sudo().search([])
        for loc in delivery_locations:
            delivery_location = (loc.latitude, loc.longitude)

            distance = 0.0
            if partner_latitude != 0.0 and partner_longitude != 0.0:
                distance = geopy.distance.distance(partner_loaction, delivery_location).km

                if distance <= loc.delivery_radius:
                    valid = True
                    break
            else:
                valid = False

        if extra_step.active:
            return request.redirect("/shop/extra_info")
        data = request.env['res.partner'].sudo().search([("id", "=", user.id)])
        if valid:
            order.sudo().write({'valid_address': True})
            return request.redirect("/shop/payment")
        else:
            if order.website_delivery_type == 'pickup':
                return request.redirect("/shop/payment")
            else:
                order.sudo().write({'valid_address': False})
                return request.redirect("/shop/checkout")

    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def check_time(self, **post):
        order = request.website.sale_get_order()
        current_uid = request.env.user
        tz = pytz.timezone(current_uid.tz or 'Australia/Brisbane')
        now = datetime.datetime.now(tz).astimezone(tz)
        values = self.checkout_values(**post)
        time_custom = int(now.time().strftime('%H'))
        values.update({
            'website_sale_order': order,
            'timezone': now.time().strftime('%H:%M'),
            'time_custom': time_custom,
        })
        return request.render("website_sale.checkout", values)

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else:  # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.with_context(not_self_saleperson=True).onchange_partner_id()
                    # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
                    order.partner_invoice_id = partner_id
                    if not kw.get('use_same'):
                        if order.website_delivery_type == 'delivery':
                            old_user = request.env['res.users'].sudo().search([('login', '=', order.partner_id.email)])
                            if order.partner_id:
                                order.sudo().write({'public_partner': order.partner_id})
                            kw['callback'] = '/shop/confirm_order'
                        else:
                            kw['callback'] = kw.get('callback') or \
                                             (not order.only_services and (
                                                     mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))

                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                # TDE FIXME: don't ever do this
                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(
            int(values['country_id']))
        country = country and country.exists() or def_country_id
        current_uid = request.env.user
        tz = pytz.timezone(current_uid.tz or 'Australia/Brisbane')
        now = datetime.datetime.now(tz).astimezone(tz)
        time_custom = int(now.time().strftime('%H'))
        render_values = {
            'website_sale_order': order,
            'timezone': now.time().strftime('%H:%M'),
            'time_custom': time_custom,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'country': country,
            'country_states': country.get_website_sale_states(mode=mode[1]),
            'countries': country.get_website_sale_countries(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
        }
        return request.render("website_sale.address", render_values)
        # return request.render("website_sale.address_crust", render_values)

    def _checkout_form_save(self, mode, checkout, all_values):
        Partner = request.env['res.partner']
        if mode[0] == 'new':
            partner_id = Partner.sudo().with_context(tracking_disable=True).create(checkout).id
        elif mode[0] == 'edit':
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                # double check
                order = request.website.sale_get_order()
                shippings = Partner.sudo().search([("id", "child_of", order.partner_id.commercial_partner_id.ids)])
                if partner_id not in shippings.mapped('id') and partner_id != order.partner_id.id:
                    return Forbidden()
                Partner.browse(partner_id).sudo().write(checkout)
        return partner_id

    @http.route(['/shop/payment/transaction/',
                 '/shop/payment/transaction/<int:so_id>',
                 '/shop/payment/transaction/<int:so_id>/<string:access_token>'], type='json', auth="public",
                website=True)
    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        """ Json method that creates a payment.transaction, used to create a
        transaction when the user clicks on 'pay now' button. After having
        created the transaction, the event continues and the user is redirected
        to the acquirer website.

        :param int acquirer_id: id of a payment.acquirer record. If not set the
                                user is redirected to the checkout page
        """
        # Ensure a payment acquirer is selected
        if not acquirer_id:
            return False

        try:
            acquirer_id = int(acquirer_id)
        except:
            return False

        # Retrieve the sale order
        if so_id:
            env = request.env['sale.order']
            domain = [('id', '=', so_id)]
            if access_token:
                env = env.sudo()
                domain.append(('access_token', '=', access_token))
            order = env.search(domain, limit=1)
        else:
            order = request.website.sale_get_order()

        # Ensure there is something to proceed
        if not order or (order and not order.order_line):
            return Falsepickup_date

        # assert order.partner_id.id != request.website.partner_id.id

        # Create transaction
        vals = {'acquirer_id': acquirer_id,
                'return_url': '/shop/payment/validate'}

        if save_token:
            vals['type'] = 'form_save'
        if token:
            vals['payment_token_id'] = int(token)

        transaction = order._create_payment_transaction(vals)

        # store the new transaction into the transaction list and if there's an old one, we remove it
        # until the day the ecommerce supports multiple orders at the same time
        last_tx_id = request.session.get('__website_sale_last_tx_id')
        last_tx = request.env['payment.transaction'].browse(last_tx_id).sudo().exists()
        if last_tx:
            PaymentProcessing.remove_payment_transaction(last_tx)
        PaymentProcessing.add_payment_transaction(transaction)
        request.session['__website_sale_last_tx_id'] = transaction.id
        return transaction.render_sale_button(order)


class PickUpAndDelivery(http.Controller):
    @http.route('/order/delivery', type='json', csrf=False, auth="none")
    def OrderDelivery(self, **kw):
        order_id = int(kw['order_id'])
        delivery = str(kw['delivery_type'])
        method = ""
        if delivery == 'pickup':
            method = "pickup"
        elif delivery == 'delivery':
            method = "delivery"
        elif delivery == 'kerbside':
            method = "kerbside"
        if order_id:
            order = request.env['sale.order'].sudo().search([('id', '=', order_id)])
            if order:
                if order.order_line:
                    for lines in order.order_line:
                        if lines.is_reward_line:
                            lines.unlink()
                order.sudo().write({'website_delivery_type': method})

    @http.route('/get/time/cooking', csrf=False, type='json', auth="public")
    def CookingTime(self, **kw):

        picking_date = kw.get('picking_date', 'Today')
        current_uid = request.env.user
        tz = pytz.timezone(current_uid.tz or 'Australia/Brisbane')
        if picking_date == 'Today':
            today = datetime.datetime.now(tz).strftime("%A")
        else:

            date = datetime.datetime.strptime(picking_date, "%m/%d/%Y")
            today = date.astimezone(tz).strftime("%A")

        res_config_settings = request.env['ir.config_parameter'].sudo()
        min_delivery_time = res_config_settings.get_param('website_sale_hour.pickup_time')
        minutes = float(min_delivery_time) * 60
        time = datetime.datetime.now(tz)

        from_time_1 = ''
        from_time_2 = ''
        if today == 'Sunday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_sunday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_sunday')
        elif today == 'Monday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_monday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_monday')
        elif today == 'Tuesday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_tuesday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_tuesday')
        elif today == 'Wednesday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_wednesday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_wednesday')
        elif today == 'Thursday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_thursday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_thursday')
        elif today == 'Friday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_friday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_friday')
        elif today == 'Saturday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_saturday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_saturday')

        time_from1 = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_1) * 60, 60))
        time_from2 = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_2) * 60, 60))

        pickup_date_val = time + datetime.timedelta(minutes=minutes)

        time_now = pickup_date_val.time().strftime('%H:%M')
        if picking_date == 'Today':
            picking_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')
        else:
            picking_date = datetime.datetime.strptime(picking_date, "%m/%d/%Y").date().strftime('%Y-%m-%d')

        return {'time_now': time_now, 'picking_date': picking_date,
                'after_date': pickup_date_val.date().strftime('%Y-%m-%d'),
                'today_date': datetime.datetime.now(tz).date().strftime('%Y-%m-%d'), "from_time_1": time_from1,
                'from_time_2': time_from2}

    @http.route('/get/time/cooking/kerbside', csrf=False, type='json', auth="public")
    def CookingTimeCurb(self, **kw):

        picking_date = kw.get('picking_date', 'Today')
        current_uid = request.env.user
        tz = pytz.timezone(current_uid.tz or 'Australia/Brisbane')
        if picking_date == 'Today':
            today = datetime.datetime.now(tz).strftime("%A")
        else:

            date = datetime.datetime.strptime(picking_date, "%m/%d/%Y")
            today = date.astimezone(tz).strftime("%A")

        res_config_settings = request.env['ir.config_parameter'].sudo()
        min_delivery_time = res_config_settings.get_param('website_sale_hour.pickup_time')
        minutes = float(min_delivery_time) * 60
        time = datetime.datetime.now(tz)

        from_time_1 = ''
        from_time_2 = ''
        if today == 'Sunday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_sunday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_sunday')
        elif today == 'Monday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_monday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_monday')
        elif today == 'Tuesday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_tuesday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_tuesday')
        elif today == 'Wednesday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_wednesday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_wednesday')
        elif today == 'Thursday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_thursday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_thursday')
        elif today == 'Friday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_friday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_friday')
        elif today == 'Saturday':
            from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_saturday')
            from_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_saturday')

        time_from1 = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_1) * 60, 60))
        time_from2 = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_2) * 60, 60))

        pickup_date_val = time + datetime.timedelta(minutes=minutes)

        time_now = pickup_date_val.time().strftime('%H:%M')
        if picking_date == 'Today':
            picking_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')
        else:
            picking_date = datetime.datetime.strptime(picking_date, "%m/%d/%Y").date().strftime('%Y-%m-%d')

        return {'time_now': time_now, 'picking_date': picking_date,
                'after_date': pickup_date_val.date().strftime('%Y-%m-%d'),
                'today_date': datetime.datetime.now(tz).date().strftime('%Y-%m-%d'), "from_time_1": time_from1,
                'from_time_2': time_from2}

    @http.route('/save/checkout', csrf=False, type='json', auth="public", website=True)
    def OrderPickupTimeSave(self, **kw):
        order_id = kw['order_id']
        partner_name = kw['partner_name']
        partner_phone = kw['partner_phone']
        partner_email = kw['partner_email']
        delivery_type = kw['delivery_type']
        email_confirmation = kw['email_confirmation']
        sms_confirmation = kw['sms_confirmation']
        contactless_confirmation = kw['contactless_confirmation']
        pickup_date_time = ''
        picking = ''
        print("informationss", order_id, partner_name, partner_phone, partner_email, delivery_type)
        print("informationss", email_confirmation, sms_confirmation, contactless_confirmation)
        # state_id = request.env['res.country.state'].sudo().search([('code', '=', 'QLD')], limit=1).id
        # if pickup_date == 'Today':
        #     pickup_date_val1 = datetime.datetime.now() + datetime.timedelta(hours=10, minutes=00)
        #     pickup_date_val = pickup_date_val1.date()
        # else:
        #     pickup_date_val = datetime.datetime.strptime(pickup_date, '%m/%d/%Y').date()
        # if pickup_time:
        #     time_val = datetime.datetime.strptime(pickup_time, '%H:%M').time()
        #     pickup_date_time = datetime.datetime.combine(pickup_date_val, time_val)
        #     backend_time = pickup_date_time + datetime.timedelta(hours=10, minutes=00)
        # if pickup_date and pickup_time and order_id:

        if order_id:
            # country = request.env['res.country'].sudo().search([('code', '=', 'AU')], limit=1).id
            # company = request.env['res.company'].sudo().browse(request.website.company_id.id)
            order = request.env['sale.order'].sudo().search([('id', '=', int(order_id))])
            country = order.company_id.id
            company = order.company_id
            order.onchange_partner_shipping_id()
            order.order_line._compute_tax_id()
            request.session['sale_last_order_id'] = order.id
            request.website.sale_get_order(update_pricelist=True)
            # pickup_date_string = pickup_date_time.strftime("%d/%m/%Y %H:%M")
            if order:
                order.sudo().write({
                    'carrier_id': 1,
                    'email_confirmation': True if email_confirmation == 'on' else False,
                    'sms_confirmation': True if sms_confirmation == 'on' else False,
                    'contactless_confirmation': True if contactless_confirmation == 'on' else False,
                })
                if delivery_type == "user":
                    p_id = order.partner_id.id
                    if p_id:
                        uid = order.partner_id.id
                        if uid:
                            user = request.env['res.partner'].sudo().search([('id', '=', uid)])
                            val = {
                                'company_type': 'person',
                                'parent_id': user.id,
                                'type': 'delivery',
                                'name': str(partner_name),
                                'phone': int(partner_phone),
                                'email': str(partner_email),
                            }
                            child = request.env['res.partner'].sudo().create(val)
                            request.env.cr.commit()
                            child.sudo().write({
                                'country_id': company.country_id,
                                'state_id': company.state_id,
                                'zip': company.zip,
                                'street': company.street,
                                'street2': company.street2,
                                'city': company.city
                            })
                            order.sudo().update({
                                'partner_id': child.id,
                                'partner_shipping_id': child.id,
                                'public_partner': child.id,
                                'carrier_id': 1
                            })
                            order.sudo().update({'partner_invoice_id': child.id})
                            request.env.cr.commit()
                            return True
                elif delivery_type == "public":
                    p_id = order.partner_id.id
                    login_user = request.env['res.users'].sudo().search([('partner_id', '=', p_id)])
                    if login_user:
                        uid = order.partner_id.id
                        if uid:
                            user = request.env['res.partner'].sudo().search([('id', '=', uid)])
                            val = {
                                'company_type': 'person',
                                'parent_id': user.id,
                                'type': 'delivery',
                                'name': str(partner_name),
                                'phone': int(partner_phone),
                                'email': str(partner_email),
                            }

                            child = request.env['res.partner'].sudo().create(val)
                            request.env.cr.commit()
                            child.sudo().write({
                                'country_id': company.country_id,
                                'state_id': company.state_id,
                                'zip': company.zip,
                                'street': company.street,
                                'street2': company.street2,
                                'city': company.city
                            })
                            order.sudo().write({
                                'partner_id': child.id,
                                'partner_shipping_id': child.id,
                                'public_partner': child.id,
                                'carrier_id': 1
                            })
                            request.env.cr.commit()
                            order.sudo().write({'partner_invoice_id': child.id})
                            return True
                    else:
                        login = str(partner_email)
                        users = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
                        if users:
                            val = {
                                'company_type': 'person',
                                'parent_id': users.partner_id.id,
                                'type': 'delivery',
                                'name': str(partner_name),
                                'phone': int(partner_phone),
                                'email': str(partner_email),
                            }
                            child = request.env['res.partner'].sudo().create(val)
                            child.write({
                                'country_id': company.country_id,
                                'state_id': company.state_id,
                                'zip': company.zip,
                                'street': company.street,
                                'street2': company.street2,
                                'city': company.city
                            })
                            order.sudo().write({
                                'partner_id': child.id,
                                'partner_shipping_id': child.id,
                                'public_partner': child.id,
                                'carrier_id': 1
                            })
                            order.sudo().write({'partner_invoice_id': child.id})
                            request.env.cr.commit()
                            return True
                        else:
                            val = {
                                'name': str(partner_name),
                                'login': str(partner_email),
                                'groups_id': [(4, request.env.ref('base.group_portal').id)]
                            }
                            user = request.env['res.users']
                            new_user = user.sudo().create(val)

                            if new_user.partner_id:
                                new_user.partner_id.sudo().write({
                                    'name': str(partner_name),
                                    'phone': int(partner_phone),
                                    'email': str(partner_email),
                                    'country_id': company.country_id,
                                    'state_id': company.state_id,
                                    'zip': company.zip,
                                    'street': company.street,
                                    'street2': company.street2,
                                    'city': company.city
                                })

                                order.sudo().write(
                                    {'partner_id': new_user.partner_id.id,
                                     'public_partner': new_user.partner_id.id,
                                     'partner_shipping_id': new_user.partner_id.id,
                                     'carrier_id': 1})

                                order.sudo().write({'partner_invoice_id': new_user.partner_id.id})
                                request.env.cr.commit()
                                return True

    @http.route('/order/pickup/time', csrf=False, type='json', auth="public", website=True)
    def SaveChanges(self, **kw):
        pickup_date = kw['pickup_date']
        pickup_time = kw['pickup_time']
        order_id = kw['order_id']
        partner_name = kw['partner_name']
        partner_phone = kw['partner_phone']
        partner_email = kw['partner_email']
        delivery_type = kw['delivery_type']
        pickup_date_time = ''
        pickup_date_val = ''
        picking = ''
        country = request.env['res.country'].sudo().search([('code', '=', 'AU')], limit=1).id
        company = request.env['res.company'].sudo().browse(request.website.company_id.id)
        state_id = request.env['res.country.state'].sudo().search([('code', '=', 'QLD')], limit=1).id
        if pickup_date == 'Today':
            pickup_date_val1 = datetime.datetime.now() + datetime.timedelta(hours=10, minutes=00)
            pickup_date_val = pickup_date_val1.date()
        else:
            pickup_date_val = datetime.datetime.strptime(pickup_date, '%m/%d/%Y').date()
        if pickup_time:
            time_val = datetime.datetime.strptime(pickup_time, '%H:%M').time()
            pickup_date_time = datetime.datetime.combine(pickup_date_val, time_val)
            backend_time = pickup_date_time + datetime.timedelta(hours=10, minutes=00)
        if pickup_date and pickup_time and order_id:
            if order_id:
                order = request.env['sale.order'].sudo().search([('id', '=', int(order_id))])
                order.onchange_partner_shipping_id()
                order.order_line._compute_tax_id()
                request.session['sale_last_order_id'] = order.id
                request.website.sale_get_order(update_pricelist=True)
                pickup_date_string = pickup_date_time.strftime("%d/%m/%Y %H:%M")
                if order:
                    order.sudo().write(
                        {'pickup_date': pickup_date_time, 'pickup_date_string': str(pickup_date_string),
                         'carrier_id': 1})
                    if delivery_type == "user":
                        p_id = order.partner_id.id
                        if p_id:
                            uid = order.partner_id.id
                            if uid:
                                user = request.env['res.partner'].sudo().search([('id', '=', uid)])
                                val = {
                                    'company_type': 'person',
                                    'parent_id': user.id,
                                    'type': 'delivery',
                                    'name': str(partner_name),
                                    'phone': int(partner_phone),
                                    'email': str(partner_email),
                                }
                                child = request.env['res.partner'].sudo().create(val)
                                request.env.cr.commit()
                                child.sudo().write({
                                    'country_id': company.country_id,
                                    'state_id': company.state_id,
                                    'zip': company.zip,
                                    'street': company.street,
                                    'street2': company.street2,
                                    'city': company.city
                                })
                                order.sudo().update({
                                    'partner_id': child.id,
                                    'partner_shipping_id': child.id,
                                    'public_partner': child.id,
                                    'carrier_id': 1
                                })
                                order.sudo().update({'partner_invoice_id': child.id})
                                request.env.cr.commit()
                                return True
                    elif delivery_type == "public":
                        p_id = order.partner_id.id
                        login_user = request.env['res.users'].sudo().search([('partner_id', '=', p_id)])
                        if login_user:
                            uid = order.partner_id.id
                            if uid:
                                user = request.env['res.partner'].sudo().search([('id', '=', uid)])
                                val = {
                                    'company_type': 'person',
                                    'parent_id': user.id,
                                    'type': 'delivery',
                                    'name': str(partner_name),
                                    'phone': int(partner_phone),
                                    'email': str(partner_email),
                                }

                                child = request.env['res.partner'].sudo().create(val)
                                request.env.cr.commit()
                                child.sudo().write({
                                    'country_id': company.country_id,
                                    'state_id': company.state_id,
                                    'zip': company.zip,
                                    'street': company.street,
                                    'street2': company.street2,
                                    'city': company.city
                                })
                                order.sudo().write({
                                    'partner_id': child.id,
                                    'partner_shipping_id': child.id,
                                    'public_partner': child.id,
                                    'carrier_id': 1
                                })
                                request.env.cr.commit()
                                order.sudo().write({'partner_invoice_id': child.id})
                                return True
                        else:
                            login = str(partner_email)
                            users = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
                            if users:
                                val = {
                                    'company_type': 'person',
                                    'parent_id': users.partner_id.id,
                                    'type': 'delivery',
                                    'name': str(partner_name),
                                    'phone': int(partner_phone),
                                    'email': str(partner_email),
                                }
                                child = request.env['res.partner'].sudo().create(val)
                                child.write({
                                    'country_id': company.country_id,
                                    'state_id': company.state_id,
                                    'zip': company.zip,
                                    'street': company.street,
                                    'street2': company.street2,
                                    'city': company.city
                                })
                                order.sudo().write({
                                    'partner_id': child.id,
                                    'partner_shipping_id': child.id,
                                    'public_partner': child.id,
                                    'carrier_id': 1
                                })
                                order.sudo().write({'partner_invoice_id': child.id})
                                request.env.cr.commit()
                                return True
                            else:
                                val = {
                                    'name': str(partner_name),
                                    'login': str(partner_email),
                                    'groups_id': [(4, request.env.ref('base.group_portal').id)]
                                }
                                user = request.env['res.users']
                                new_user = user.sudo().create(val)

                                if new_user.partner_id:
                                    new_user.partner_id.sudo().write({
                                        'name': str(partner_name),
                                        'phone': int(partner_phone),
                                        'email': str(partner_email),
                                        'country_id': company.country_id,
                                        'state_id': company.state_id,
                                        'zip': company.zip,
                                        'street': company.street,
                                        'street2': company.street2,
                                        'city': company.city
                                    })

                                    order.sudo().write(
                                        {'partner_id': new_user.partner_id.id,
                                         'public_partner': new_user.partner_id.id,
                                         'partner_shipping_id': new_user.partner_id.id,
                                         'carrier_id': 1})

                                    order.sudo().write({'partner_invoice_id': new_user.partner_id.id})
                                    request.env.cr.commit()
                                    return True

    @http.route('/order/time/range', csrf=False, type='json', auth="public")
    def OrderTimeRange(self, **kw):
        pickup_date = kw['pickup_date']
        pickup_time = kw['pickup_time']
        order_id = kw['order_id']
        delivery_type = kw['delivery_type']
        pickup_date_time = ''
        pickup_date_val = ''
        pick_time_val = ''
        picking = ''
        method = kw['method']
        # vehicle_type = kw['vehicle_type']
        vehicle_color = kw['vehicle_color']
        license_plate_no = kw['license_plate_no']
        type_name1 = kw['v_type']
        make_name1 = kw['v_make']
        location_name1 = kw['v_location']
        location_notes = kw['location_note']
        invalid_product = False
        if order_id:
            order_data = request.env['sale.order'].sudo().search([('id', '=', int(order_id))])
            if order_data.order_line:
                for pro in order_data.order_line:
                    if pro.product_id.not_available_for_pickup:
                        invalid_product = True
        if invalid_product:
            val = {"status": "invalid_products"}
            return val

        type_name = None
        make_name = None
        location_name = None
        if type_name1:
            type_name = request.env['vehicle.type'].sudo().search([('type_name', '=', str(type_name1))]).id
        if make_name1:
            make_name = request.env['vehicle.make'].sudo().search([('make_name', '=', str(make_name1))]).id
        if location_name1:
            location_name = request.env['vehicle.location'].sudo().search(
                [('location_name', '=', str(location_name1))]).id
        if pickup_date == 'Today':
            pickup_date_val = datetime.datetime.now() + datetime.timedelta(hours=10, minutes=00)
        else:
            pickup_date_val = datetime.datetime.strptime(pickup_date, '%m/%d/%Y').date() + datetime.timedelta(hours=10,
                                                                                                              minutes=00)
        if pickup_time:
            time_val = datetime.datetime.strptime(pickup_time, '%H:%M').time()
            pick_time_val = time_val
            pickup_date_time = datetime.datetime.combine(pickup_date_val, time_val)
        ###########################################################################################
        order = request.env['sale.order'].sudo().search([('id', '=', int(order_id))])
        res_config_settings = request.env['ir.config_parameter'].sudo()
        today_date = fields.Datetime.today()
        today_day = today_date.strftime('%A')
        from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_sunday')
        from_time_2 = res_config_settings.get_param('website_sale_hour.time_from_pickup_monday')
        from_time_3 = res_config_settings.get_param('website_sale_hour.time_from_pickup_tuesday')
        from_time_4 = res_config_settings.get_param('website_sale_hour.time_from_pickup_wednesday')
        from_time_5 = res_config_settings.get_param('website_sale_hour.time_from_pickup_thursday')
        from_time_6 = res_config_settings.get_param('website_sale_hour.time_from_pickup_friday')
        from_time_7 = res_config_settings.get_param('website_sale_hour.time_from_pickup_saturday')
        to_time_1 = res_config_settings.get_param('website_sale_hour.time_to_pickup_sunday')
        to_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_monday')
        to_time_3 = res_config_settings.get_param('website_sale_hour.time_to_pickup_tuesday')
        to_time_4 = res_config_settings.get_param('website_sale_hour.time_to_pickup_wednesday')
        to_time_5 = res_config_settings.get_param('website_sale_hour.time_to_pickup_thursday')
        to_time_6 = res_config_settings.get_param('website_sale_hour.time_to_pickup_friday')
        to_time_7 = res_config_settings.get_param('website_sale_hour.time_to_pickup_saturday')
        list1 = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        list2 = [from_time_2, from_time_3, from_time_4, from_time_5, from_time_6, from_time_7, from_time_1]
        i = 1
        data = list(zip(list1, list2))
        next_date = False
        x = ''
        prep_time = order.preparation_time
        while True:
            next_date = fields.Datetime.today() + timedelta(days=i)
            w = next_date.weekday()
            m, n = data[w]
            if float(n):
                time_vals = str(n).split('.')
                actual_time = next_date.replace(hour=int(time_vals[0]), minute=int(time_vals[1]), second=0)
                opening_time = actual_time + timedelta(minutes=prep_time)
                x = opening_time.strftime('%H:%M')
                break
            i += 1

        ################################################################################################
        if pickup_date and pickup_time and order_id:
            order = request.env['sale.order'].sudo().search([('id', '=', int(order_id))])
            pickup_date_string = pickup_date_time.strftime("%d/%m/%Y %H:%M")
            if order:
                order.sudo().write(
                    {'pickup_date': pickup_date_time,
                     'pickup_date_string': str(pickup_date_string),
                     'website_delivery_type': str(method),
                     'vehicle_type': type_name,
                     'approximate_location': location_name,
                     'vehicle_make': make_name,
                     'location_notes': str(location_notes),
                     'vehicle_color': str(vehicle_color),
                     'license_plate_no': str(license_plate_no)})
            res_config_settings = request.env['ir.config_parameter'].sudo()
            min_delivery_time = res_config_settings.get_param('website_sale_hour.pickup_time')

            sunday_from = res_config_settings.get_param('website_sale_hour.sunday_from')
            sunday_to = res_config_settings.get_param('website_sale_hour.sunday_to')
            monday_from = res_config_settings.get_param('website_sale_hour.monday_from')
            monday_to = res_config_settings.get_param('website_sale_hour.monday_to')
            tuesday_from = res_config_settings.get_param('website_sale_hour.tuesday_from')
            tuesday_to = res_config_settings.get_param('website_sale_hour.tuesday_to')
            wednesday_from = res_config_settings.get_param('website_sale_hour.wednesday_from')
            wednesday_to = res_config_settings.get_param('website_sale_hour.wednesday_to')
            thursday_from = res_config_settings.get_param('website_sale_hour.thursday_from')
            thursday_to = res_config_settings.get_param('website_sale_hour.thursday_to')
            friday_from = res_config_settings.get_param('website_sale_hour.friday_from')
            friday_to = res_config_settings.get_param('website_sale_hour.friday_to')
            saturday_from = res_config_settings.get_param('website_sale_hour.saturday_from')
            saturday_to = res_config_settings.get_param('website_sale_hour.saturday_to')

            day_value = pickup_date_time.strftime('%A')
            time_from = ''
            time_to = ''
            day_pickup_time = ''
            if day_value == 'Sunday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_1) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_1) * 60, 60))
            elif day_value == 'Monday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_2) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_2) * 60, 60))
            elif day_value == 'Tuesday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_3) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_3) * 60, 60))
            elif day_value == 'Wednesday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_4) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_4) * 60, 60))
            elif day_value == 'Thursday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_5) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_5) * 60, 60))
            elif day_value == 'Friday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_6) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_6) * 60, 60))
            elif day_value == 'Saturday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_7) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_7) * 60, 60))

            future_order_from = res_config_settings.get_param('website_sale_hour.future_order_from')
            future_order_to = res_config_settings.get_param('website_sale_hour.future_order_to')
            future_order_from_type = res_config_settings.get_param('website_sale_hour.future_order_from_type')
            future_order_to_type = res_config_settings.get_param('website_sale_hour.future_order_to_type')

            future_order_from_hr = 0
            future_order_from_min = 0
            future_order_from_day = 0

            future_order_to_hr = 0
            future_order_to_min = 0
            future_order_to_day = 0

            if int(future_order_from) <= 0:
                pass
            elif future_order_from_type == 'minute':
                if int(future_order_from) > 0:
                    future_order_from_min = future_order_from
            elif future_order_from_type == 'hour':
                if int(future_order_from) > 0:
                    future_order_from_hr = future_order_from
            elif future_order_from_type == 'day':
                if int(future_order_from) > 0:
                    future_order_from_day = future_order_from

            if int(future_order_to) <= 0:
                pass
            elif future_order_to_type == 'minute':
                if int(future_order_to) > 0:
                    future_order_to_min = future_order_to
            elif future_order_to_type == 'hour':
                if int(future_order_to) > 0:
                    future_order_to_hr = future_order_to
            elif future_order_to_type == 'day':
                if int(future_order_to) > 0:
                    future_order_to_day = future_order_to

            days = [0, 1, 2, 3, 4, 5, 6]

            tz = pytz.timezone('Australia/Brisbane')
            earliest_time = ''

            min_pick_time = ''
            max_pick_time = ''
            if int(future_order_from_hr) > 0:
                min_pick_time = datetime.datetime.now() + datetime.timedelta(hours=10 + int(future_order_from_hr),
                                                                             minutes=00)
            elif int(future_order_from_min) > 0:
                min_pick_time = datetime.datetime.now() + datetime.timedelta(hours=10,
                                                                             minutes=00 + int(future_order_from_min))

            if int(future_order_to_hr) > 0:
                max_pick_time = datetime.datetime.now() + datetime.timedelta(hours=10 + int(future_order_to_hr),
                                                                             minutes=00)
            elif int(future_order_from_min) > 0:
                max_pick_time = datetime.datetime.now() + datetime.timedelta(hours=10,
                                                                             minutes=00 + int(future_order_to_min))

            if int(future_order_from_hr) and int(future_order_to_hr):
                t_min_hour = min_pick_time.hour
                t_min_minute = min_pick_time.minute

                t_max_hour = max_pick_time.hour
                t_max_minute = max_pick_time.minute

                data = "Please Select a pickup time between " + str(t_min_hour) + ":" + str(
                    t_min_minute) + " and " + str(t_max_hour) + ":" + str(t_max_minute)
                if pickup_date_time > min_pick_time and pickup_date_time < max_pick_time:
                    val = {"status": "valid_pickup", "warning": data}
                else:
                    val = {"status": "invalid_pickup", "warning": data}
                    return val

            earliest_time = ''
            min_delivery = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(min_delivery_time) * 60, 60))
            min_tim = min_delivery.split(':')
            min_hr = min_tim[0]
            min_time = min_tim[1]
            this_day1 = datetime.datetime.now() + datetime.timedelta(hours=10, minutes=00)
            if int(min_hr) > 0 and int(min_time) > 0:
                earliest_time = datetime.datetime.now() + datetime.timedelta(hours=10 + int(min_hr),
                                                                             minutes=int(min_time))
            elif int(min_hr) > 0:
                earliest_time = datetime.datetime.now() + datetime.timedelta(hours=10 + int(min_hr), minutes=30)
            elif int(min_time) > 0:
                earliest_time = datetime.datetime.now() + datetime.timedelta(hours=10, minutes=int(min_time))
            else:
                earliest_time = datetime.datetime.now() + datetime.timedelta(hours=10, minutes=30)

            this_day = this_day1.weekday()
            this_now = this_day1.time().strftime('%H.%M')
            # earliest_time_1 = earliest_time.time().strftime('%H.%M')
            this_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(this_now) * 60, 60))
            c_now = pickup_date_time.time().strftime('%H.%M')
            # c_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(c_now) * 60, 60))
            c_time = c_now.replace(".", ":")
            now = int(this_day)
            picking_time = pick_time_val.strftime('%H.%M')
            minutes = 0
            if min_hr:
                minutes = int(min_hr) * 60
            if min_time:
                minutes = minutes + int(min_time)
            # if pickup_date == 'Today':
            pickup_date_time_new = pickup_date_time + datetime.timedelta(days=1)
            difference_tym = pickup_date_time - this_day1
            tot_sec = difference_tym.total_seconds()
            tot_tym = tot_sec / 60
            if tot_tym <= 0:
                val = {"status": "invalid", 'time_hr': min_hr, 'time_minute': min_time}
                return val
            if int(minutes) > int(tot_tym):
                val = {"status": "invalid", 'time_hr': min_hr, 'time_minute': min_time}
                return val
            else:
                pass
            time_ok = False
            if c_time >= time_from and c_time <= time_to:
                pickup_date_string = pickup_date_time.strftime("%d/%m/%Y %H:%M")
                order.sudo().write({'pickup_date': pickup_date_time,
                                    'pickup_date_string': str(pickup_date_string),
                                    'website_delivery_type': method})
                time_ok = True
            else:
                pass
            return {'time_ok': time_ok, 'next_date': next_date.strftime("%d/%m/%Y"), 'opening_time': x}
        else:
            val = {"status": "none", 'next_date': next_date.strftime("%d/%m/%Y"), 'opening_time': x}
            return val

    @http.route('/order/time/range/delivery/type', csrf=False, type='json', auth="public")
    def CrustOrderTimeRange(self, **kw):

        pickup_date = kw['pickup_date']
        pickup_time = kw['pickup_time']
        order_id = kw['order_id']
        # delivery_type = kw['delivery_type']
        pickup_date_time = ''
        pickup_date_val = ''
        pick_time_val = ''
        picking = ''
        # method = kw['method']
        # vehicle_type = kw['vehicle_type']
        # vehicle_color = kw['vehicle_color']
        # license_plate_no = kw['license_plate_no']
        # type_name1 = kw['v_type']
        # make_name1 = kw['v_make']
        # location_name1 = kw['v_location']
        # location_notes = kw['location_note']
        # invalid_product = False
        if order_id:
            order_data = request.env['sale.order'].sudo().search([('id', '=', int(order_id))])
            # if order_data.order_line:
            #     for pro in order_data.order_line:
            #         if pro.product_id.not_available_for_pickup:
            #             invalid_product = True
        # if invalid_product:
        #     val = {"status": "invalid_products"}
        #     return val

        # type_name = None
        # make_name = None
        # location_name = None
        # if type_name1:
        #     type_name = request.env['vehicle.type'].sudo().search([('type_name', '=', str(type_name1))]).id
        # if make_name1:
        #     make_name = request.env['vehicle.make'].sudo().search([('make_name', '=', str(make_name1))]).id
        # if location_name1:
        #     location_name = request.env['vehicle.location'].sudo().search(
        #         [('location_name', '=', str(location_name1))]).id
        if pickup_date == 'Today':
            pickup_date_val = datetime.datetime.now() + datetime.timedelta(hours=10, minutes=00)
        else:
            pickup_date_val = datetime.datetime.strptime(pickup_date, '%m/%d/%Y').date() + datetime.timedelta(hours=10,
                                                                                                              minutes=00)
        if pickup_time:
            time_val = datetime.datetime.strptime(pickup_time, '%H:%M').time()
            pick_time_val = time_val
            pickup_date_time = datetime.datetime.combine(pickup_date_val, time_val)
        ###########################################################################################
        order = request.env['sale.order'].sudo().search([('id', '=', int(order_id))])
        res_config_settings = request.env['ir.config_parameter'].sudo()
        today_date = fields.Datetime.today()
        today_day = today_date.strftime('%A')
        from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_sunday')
        from_time_2 = res_config_settings.get_param('website_sale_hour.time_from_pickup_monday')
        from_time_3 = res_config_settings.get_param('website_sale_hour.time_from_pickup_tuesday')
        from_time_4 = res_config_settings.get_param('website_sale_hour.time_from_pickup_wednesday')
        from_time_5 = res_config_settings.get_param('website_sale_hour.time_from_pickup_thursday')
        from_time_6 = res_config_settings.get_param('website_sale_hour.time_from_pickup_friday')
        from_time_7 = res_config_settings.get_param('website_sale_hour.time_from_pickup_saturday')
        to_time_1 = res_config_settings.get_param('website_sale_hour.time_to_pickup_sunday')
        to_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_monday')
        to_time_3 = res_config_settings.get_param('website_sale_hour.time_to_pickup_tuesday')
        to_time_4 = res_config_settings.get_param('website_sale_hour.time_to_pickup_wednesday')
        to_time_5 = res_config_settings.get_param('website_sale_hour.time_to_pickup_thursday')
        to_time_6 = res_config_settings.get_param('website_sale_hour.time_to_pickup_friday')
        to_time_7 = res_config_settings.get_param('website_sale_hour.time_to_pickup_saturday')
        list1 = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        list2 = [from_time_2, from_time_3, from_time_4, from_time_5, from_time_6, from_time_7, from_time_1]
        i = 1
        data = list(zip(list1, list2))
        next_date = False
        x = ''
        prep_time = order.preparation_time
        while True:
            next_date = fields.Datetime.today() + timedelta(days=i)
            w = next_date.weekday()
            m, n = data[w]
            time_vals = str(n).split('.')
            actual_time = next_date.replace(hour=int(time_vals[0]), minute=int(time_vals[1]), second=0)
            opening_time = actual_time + timedelta(minutes=prep_time)
            x = opening_time.strftime('%H:%M')
            break
            i += 1

        ################################################################################################
        if pickup_date and pickup_time and order_id:
            order = request.env['sale.order'].sudo().search([('id', '=', int(order_id))])
            pickup_date_string = pickup_date_time.strftime("%d/%m/%Y %H:%M")
            if order:
                order.sudo().write(
                    {'pickup_date': pickup_date_time,
                     'pickup_date_string': str(pickup_date_string),
                     # 'website_delivery_type': str(method),
                     # 'vehicle_type': type_name,
                     # 'approximate_location': location_name,
                     # 'vehicle_make': make_name,
                     # 'location_notes': str(location_notes),
                     # 'vehicle_color': str(vehicle_color),
                     # 'license_plate_no': str(license_plate_no)
                     })
            res_config_settings = request.env['ir.config_parameter'].sudo()
            min_delivery_time = res_config_settings.get_param('website_sale_hour.pickup_time')
            day_value = pickup_date_time.strftime('%A')
            time_from = ''
            time_to = ''
            day_pickup_time = ''
            if day_value == 'Sunday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_1) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_1) * 60, 60))
            elif day_value == 'Monday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_2) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_2) * 60, 60))
            elif day_value == 'Tuesday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_3) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_3) * 60, 60))
            elif day_value == 'Wednesday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_4) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_4) * 60, 60))
            elif day_value == 'Thursday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_5) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_5) * 60, 60))
            elif day_value == 'Friday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_6) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_6) * 60, 60))
            elif day_value == 'Saturday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_7) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_7) * 60, 60))

            future_order_from = res_config_settings.get_param('website_sale_hour.future_order_from')
            future_order_to = res_config_settings.get_param('website_sale_hour.future_order_to')
            future_order_from_type = res_config_settings.get_param('website_sale_hour.future_order_from_type')
            future_order_to_type = res_config_settings.get_param('website_sale_hour.future_order_to_type')

            future_order_from_hr = 0
            future_order_from_min = 0
            future_order_from_day = 0

            future_order_to_hr = 0
            future_order_to_min = 0
            future_order_to_day = 0

            if int(future_order_from) <= 0:
                pass
            elif future_order_from_type == 'minute':
                if int(future_order_from) > 0:
                    future_order_from_min = future_order_from
            elif future_order_from_type == 'hour':
                if int(future_order_from) > 0:
                    future_order_from_hr = future_order_from
            elif future_order_from_type == 'day':
                if int(future_order_from) > 0:
                    future_order_from_day = future_order_from

            if int(future_order_to) <= 0:
                pass
            elif future_order_to_type == 'minute':
                if int(future_order_to) > 0:
                    future_order_to_min = future_order_to
            elif future_order_to_type == 'hour':
                if int(future_order_to) > 0:
                    future_order_to_hr = future_order_to
            elif future_order_to_type == 'day':
                if int(future_order_to) > 0:
                    future_order_to_day = future_order_to

            days = [0, 1, 2, 3, 4, 5, 6]

            tz = pytz.timezone('Australia/Brisbane')
            earliest_time = ''

            min_pick_time = ''
            max_pick_time = ''
            if int(future_order_from_hr) > 0:
                min_pick_time = datetime.datetime.now() + datetime.timedelta(hours=10 + int(future_order_from_hr),
                                                                             minutes=00)
            elif int(future_order_from_min) > 0:
                min_pick_time = datetime.datetime.now() + datetime.timedelta(hours=10,
                                                                             minutes=00 + int(future_order_from_min))

            if int(future_order_to_hr) > 0:
                max_pick_time = datetime.datetime.now() + datetime.timedelta(hours=10 + int(future_order_to_hr),
                                                                             minutes=00)
            elif int(future_order_from_min) > 0:
                max_pick_time = datetime.datetime.now() + datetime.timedelta(hours=10,
                                                                             minutes=00 + int(future_order_to_min))

            if int(future_order_from_hr) and int(future_order_to_hr):
                t_min_hour = min_pick_time.hour
                t_min_minute = min_pick_time.minute

                t_max_hour = max_pick_time.hour
                t_max_minute = max_pick_time.minute

                data = "Please Select a pickup time between " + str(t_min_hour) + ":" + str(
                    t_min_minute) + " and " + str(t_max_hour) + ":" + str(t_max_minute)
                if pickup_date_time > min_pick_time and pickup_date_time < max_pick_time:
                    val = {"status": "valid_pickup", "warning": data}
                else:
                    val = {"status": "invalid_pickup", "warning": data}
                    return val

            earliest_time = ''
            min_delivery = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(min_delivery_time) * 60, 60))
            min_tim = min_delivery.split(':')
            min_hr = min_tim[0]
            min_time = min_tim[1]
            this_day1 = datetime.datetime.now() + datetime.timedelta(hours=10, minutes=00)
            if int(min_hr) > 0 and int(min_time) > 0:
                earliest_time = datetime.datetime.now() + datetime.timedelta(hours=10 + int(min_hr),
                                                                             minutes=int(min_time))
            elif int(min_hr) > 0:
                earliest_time = datetime.datetime.now() + datetime.timedelta(hours=10 + int(min_hr), minutes=30)
            elif int(min_time) > 0:
                earliest_time = datetime.datetime.now() + datetime.timedelta(hours=10, minutes=int(min_time))
            else:
                earliest_time = datetime.datetime.now() + datetime.timedelta(hours=10, minutes=30)

            this_day = this_day1.weekday()
            this_now = this_day1.time().strftime('%H.%M')
            # earliest_time_1 = earliest_time.time().strftime('%H.%M')
            this_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(this_now) * 60, 60))
            c_now = pickup_date_time.time().strftime('%H.%M')
            # c_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(c_now) * 60, 60))
            c_time = c_now.replace(".", ":")
            now = int(this_day)
            picking_time = pick_time_val.strftime('%H.%M')
            minutes = 0
            if min_hr:
                minutes = int(min_hr) * 60
            if min_time:
                minutes = minutes + int(min_time)
            # if pickup_date == 'Today':
            pickup_date_time_new = pickup_date_time + datetime.timedelta(days=1)
            difference_tym = pickup_date_time - this_day1
            tot_sec = difference_tym.total_seconds()
            tot_tym = tot_sec / 60
            if tot_tym <= 0:
                val = {"status": "invalid", 'time_hr': min_hr, 'time_minute': min_time}
                return val
            if int(minutes) > int(tot_tym):
                val = {"status": "invalid", 'time_hr': min_hr, 'time_minute': min_time}
                return val
            else:
                pass
            time_ok = False
            if c_time >= time_from and c_time <= time_to:
                pickup_date_string = pickup_date_time.strftime("%d/%m/%Y %H:%M")
                order.sudo().write({'pickup_date': pickup_date_time,
                                    'pickup_date_string': str(pickup_date_string),
                                    # 'website_delivery_type': method
                                    })
                time_ok = True
            else:
                pass
            return {'time_ok': time_ok, 'next_date': next_date.strftime("%d/%m/%Y"), 'opening_time': x}
        else:
            val = {"status": "none", 'next_date': next_date.strftime("%d/%m/%Y"), 'opening_time': x}
            return val

    @http.route('/order/time/range/delivery/type/kerb', csrf=False, type='json', auth="public")
    def CrustOrderTimeRangeKerb(self, **kw):

        pickup_date = kw['pickup_date']
        pickup_time = kw['pickup_time']
        order_id = kw['order_id']
        # delivery_type = kw['delivery_type']
        pickup_date_time = ''
        pickup_date_val = ''
        pick_time_val = ''
        picking = ''
        # method = kw['method']
        # vehicle_type = kw['vehicle_type']
        vehicle_color = kw['vehicle_color']
        license_plate_no = kw['license_plate_no']
        type_name1 = kw['v_type']
        make_name1 = kw['v_make']
        location_name1 = kw['v_location']
        location_notes = kw['location_note']
        # invalid_product = False
        if order_id:
            order_data = request.env['sale.order'].sudo().search([('id', '=', int(order_id))])
            # if order_data.order_line:
            #     for pro in order_data.order_line:
            #         if pro.product_id.not_available_for_pickup:
            #             invalid_product = True
        # if invalid_product:
        #     val = {"status": "invalid_products"}
        #     return val

        type_name = None
        make_name = None
        location_name = None
        if type_name1:
            type_name = request.env['vehicle.type'].sudo().search([('type_name', '=', str(type_name1))]).id
        if make_name1:
            make_name = request.env['vehicle.make'].sudo().search([('make_name', '=', str(make_name1))]).id
        if location_name1:
            location_name = request.env['vehicle.location'].sudo().search(
                [('location_name', '=', str(location_name1))]).id
        if pickup_date == 'Today':
            pickup_date_val = datetime.datetime.now() + datetime.timedelta(hours=10, minutes=00)
        else:
            pickup_date_val = datetime.datetime.strptime(pickup_date, '%m/%d/%Y').date() + datetime.timedelta(hours=10,
                                                                                                              minutes=00)
        if pickup_time:
            time_val = datetime.datetime.strptime(pickup_time, '%H:%M').time()
            pick_time_val = time_val
            pickup_date_time = datetime.datetime.combine(pickup_date_val, time_val)
        ###########################################################################################
        order = request.env['sale.order'].sudo().search([('id', '=', int(order_id))])
        res_config_settings = request.env['ir.config_parameter'].sudo()
        today_date = fields.Datetime.today()
        today_day = today_date.strftime('%A')
        from_time_1 = res_config_settings.get_param('website_sale_hour.time_from_pickup_sunday')
        from_time_2 = res_config_settings.get_param('website_sale_hour.time_from_pickup_monday')
        from_time_3 = res_config_settings.get_param('website_sale_hour.time_from_pickup_tuesday')
        from_time_4 = res_config_settings.get_param('website_sale_hour.time_from_pickup_wednesday')
        from_time_5 = res_config_settings.get_param('website_sale_hour.time_from_pickup_thursday')
        from_time_6 = res_config_settings.get_param('website_sale_hour.time_from_pickup_friday')
        from_time_7 = res_config_settings.get_param('website_sale_hour.time_from_pickup_saturday')
        to_time_1 = res_config_settings.get_param('website_sale_hour.time_to_pickup_sunday')
        to_time_2 = res_config_settings.get_param('website_sale_hour.time_to_pickup_monday')
        to_time_3 = res_config_settings.get_param('website_sale_hour.time_to_pickup_tuesday')
        to_time_4 = res_config_settings.get_param('website_sale_hour.time_to_pickup_wednesday')
        to_time_5 = res_config_settings.get_param('website_sale_hour.time_to_pickup_thursday')
        to_time_6 = res_config_settings.get_param('website_sale_hour.time_to_pickup_friday')
        to_time_7 = res_config_settings.get_param('website_sale_hour.time_to_pickup_saturday')
        list1 = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        list2 = [from_time_2, from_time_3, from_time_4, from_time_5, from_time_6, from_time_7, from_time_1]
        i = 1
        data = list(zip(list1, list2))
        next_date = False
        x = ''
        prep_time = order.preparation_time
        while True:
            next_date = fields.Datetime.today() + timedelta(days=i)
            w = next_date.weekday()
            m, n = data[w]
            if float(n):
                time_vals = str(n).split('.')
                actual_time = next_date.replace(hour=int(time_vals[0]), minute=int(time_vals[1]), second=0)
                opening_time = actual_time + timedelta(minutes=prep_time)
                x = opening_time.strftime('%H:%M')
                break
            i += 1

        ################################################################################################
        if pickup_date and pickup_time and order_id:
            order = request.env['sale.order'].sudo().search([('id', '=', int(order_id))])
            pickup_date_string = pickup_date_time.strftime("%d/%m/%Y %H:%M")
            if order:
                order.sudo().write(
                    {'pickup_date': pickup_date_time,
                     'pickup_date_string': str(pickup_date_string),
                     # 'website_delivery_type': str(method),
                     'vehicle_type': type_name,
                     'approximate_location': location_name,
                     'vehicle_make': make_name,
                     'location_notes': str(location_notes),
                     'vehicle_color': str(vehicle_color),
                     'license_plate_no': str(license_plate_no)
                     })
            res_config_settings = request.env['ir.config_parameter'].sudo()
            min_delivery_time = res_config_settings.get_param('website_sale_hour.pickup_time')
            day_value = pickup_date_time.strftime('%A')
            time_from = ''
            time_to = ''
            day_pickup_time = ''
            if day_value == 'Sunday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_1) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_1) * 60, 60))
            elif day_value == 'Monday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_2) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_2) * 60, 60))
            elif day_value == 'Tuesday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_3) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_3) * 60, 60))
            elif day_value == 'Wednesday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_4) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_4) * 60, 60))
            elif day_value == 'Thursday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_5) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_5) * 60, 60))
            elif day_value == 'Friday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_6) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_6) * 60, 60))
            elif day_value == 'Saturday':
                time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(from_time_7) * 60, 60))
                time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(to_time_7) * 60, 60))

            future_order_from = res_config_settings.get_param('website_sale_hour.future_order_from')
            future_order_to = res_config_settings.get_param('website_sale_hour.future_order_to')
            future_order_from_type = res_config_settings.get_param('website_sale_hour.future_order_from_type')
            future_order_to_type = res_config_settings.get_param('website_sale_hour.future_order_to_type')

            future_order_from_hr = 0
            future_order_from_min = 0
            future_order_from_day = 0

            future_order_to_hr = 0
            future_order_to_min = 0
            future_order_to_day = 0

            if int(future_order_from) <= 0:
                pass
            elif future_order_from_type == 'minute':
                if int(future_order_from) > 0:
                    future_order_from_min = future_order_from
            elif future_order_from_type == 'hour':
                if int(future_order_from) > 0:
                    future_order_from_hr = future_order_from
            elif future_order_from_type == 'day':
                if int(future_order_from) > 0:
                    future_order_from_day = future_order_from

            if int(future_order_to) <= 0:
                pass
            elif future_order_to_type == 'minute':
                if int(future_order_to) > 0:
                    future_order_to_min = future_order_to
            elif future_order_to_type == 'hour':
                if int(future_order_to) > 0:
                    future_order_to_hr = future_order_to
            elif future_order_to_type == 'day':
                if int(future_order_to) > 0:
                    future_order_to_day = future_order_to

            days = [0, 1, 2, 3, 4, 5, 6]

            tz = pytz.timezone('Australia/Brisbane')
            earliest_time = ''

            min_pick_time = ''
            max_pick_time = ''
            if int(future_order_from_hr) > 0:
                min_pick_time = datetime.datetime.now() + datetime.timedelta(hours=10 + int(future_order_from_hr),
                                                                             minutes=00)
            elif int(future_order_from_min) > 0:
                min_pick_time = datetime.datetime.now() + datetime.timedelta(hours=10,
                                                                             minutes=00 + int(future_order_from_min))

            if int(future_order_to_hr) > 0:
                max_pick_time = datetime.datetime.now() + datetime.timedelta(hours=10 + int(future_order_to_hr),
                                                                             minutes=00)
            elif int(future_order_from_min) > 0:
                max_pick_time = datetime.datetime.now() + datetime.timedelta(hours=10,
                                                                             minutes=00 + int(future_order_to_min))

            if int(future_order_from_hr) and int(future_order_to_hr):
                t_min_hour = min_pick_time.hour
                t_min_minute = min_pick_time.minute

                t_max_hour = max_pick_time.hour
                t_max_minute = max_pick_time.minute

                data = "Please Select a pickup time between " + str(t_min_hour) + ":" + str(
                    t_min_minute) + " and " + str(t_max_hour) + ":" + str(t_max_minute)
                if pickup_date_time > min_pick_time and pickup_date_time < max_pick_time:
                    val = {"status": "valid_pickup", "warning": data}
                else:
                    val = {"status": "invalid_pickup", "warning": data}
                    return val

            earliest_time = ''
            min_delivery = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(min_delivery_time) * 60, 60))
            min_tim = min_delivery.split(':')
            min_hr = min_tim[0]
            min_time = min_tim[1]
            this_day1 = datetime.datetime.now() + datetime.timedelta(hours=10, minutes=00)
            if int(min_hr) > 0 and int(min_time) > 0:
                earliest_time = datetime.datetime.now() + datetime.timedelta(hours=10 + int(min_hr),
                                                                             minutes=int(min_time))
            elif int(min_hr) > 0:
                earliest_time = datetime.datetime.now() + datetime.timedelta(hours=10 + int(min_hr), minutes=30)
            elif int(min_time) > 0:
                earliest_time = datetime.datetime.now() + datetime.timedelta(hours=10, minutes=int(min_time))
            else:
                earliest_time = datetime.datetime.now() + datetime.timedelta(hours=10, minutes=30)

            this_day = this_day1.weekday()
            this_now = this_day1.time().strftime('%H.%M')
            # earliest_time_1 = earliest_time.time().strftime('%H.%M')
            this_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(this_now) * 60, 60))
            c_now = pickup_date_time.time().strftime('%H.%M')
            # c_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(c_now) * 60, 60))
            c_time = c_now.replace(".", ":")
            now = int(this_day)
            picking_time = pick_time_val.strftime('%H.%M')
            minutes = 0
            if min_hr:
                minutes = int(min_hr) * 60
            if min_time:
                minutes = minutes + int(min_time)
            # if pickup_date == 'Today':
            pickup_date_time_new = pickup_date_time + datetime.timedelta(days=1)
            difference_tym = pickup_date_time - this_day1
            tot_sec = difference_tym.total_seconds()
            tot_tym = tot_sec / 60
            if tot_tym <= 0:
                val = {"status": "invalid", 'time_hr': min_hr, 'time_minute': min_time}
                return val
            if int(minutes) > int(tot_tym):
                val = {"status": "invalid", 'time_hr': min_hr, 'time_minute': min_time}
                return val
            else:
                pass
            time_ok = False
            if c_time >= time_from and c_time <= time_to:
                pickup_date_string = pickup_date_time.strftime("%d/%m/%Y %H:%M")
                order.sudo().write({'pickup_date': pickup_date_time,
                                    'pickup_date_string': str(pickup_date_string),
                                    # 'website_delivery_type': method
                                    })
                time_ok = True
            else:
                pass
            return {'time_ok': time_ok, 'next_date': next_date.strftime("%d/%m/%Y"), 'opening_time': x}
        else:
            val = {"status": "none", 'next_date': next_date.strftime("%d/%m/%Y"), 'opening_time': x}
            return val

    @http.route('/max/date', csrf=False, type='json', auth="public")
    def MaxPickupRange(self, **kw):

        res_config_settings = request.env['ir.config_parameter'].sudo()

        future_order_from = res_config_settings.get_param('website_sale_hour.future_order_from')
        future_order_to = res_config_settings.get_param('website_sale_hour.future_order_to')
        future_order_from_type = res_config_settings.get_param('website_sale_hour.future_order_from_type')
        future_order_to_type = res_config_settings.get_param('website_sale_hour.future_order_to_type')
        if future_order_to_type == 'day':
            if int(future_order_to) > 0:
                return future_order_to
            else:
                return False
        else:
            return False

    @http.route('/delivery/date', csrf=False, type='json', auth="public")
    def deliveryDateDetails(self, **kw):

        res_config_settings = request.env['ir.config_parameter'].sudo()

        sunday_from = res_config_settings.get_param('website_sale_hour.time_from_delivery_sunday')
        sunday_to = res_config_settings.get_param('website_sale_hour.time_to_delivery_sunday')
        monday_from = res_config_settings.get_param('website_sale_hour.time_from_delivery_monday')
        monday_to = res_config_settings.get_param('website_sale_hour.time_to_delivery_monday')
        tuesday_from = res_config_settings.get_param('website_sale_hour.time_from_delivery_tuesday')
        tuesday_to = res_config_settings.get_param('website_sale_hour.time_to_delivery_tuesday')
        wednesday_from = res_config_settings.get_param('website_sale_hour.time_from_delivery_wednesday')
        wednesday_to = res_config_settings.get_param('website_sale_hour.time_to_delivery_wednesday')
        thursday_from = res_config_settings.get_param('website_sale_hour.time_from_delivery_thursday')
        thursday_to = res_config_settings.get_param('website_sale_hour.time_to_delivery_thursday')
        friday_from = res_config_settings.get_param('website_sale_hour.time_from_delivery_friday')
        friday_to = res_config_settings.get_param('website_sale_hour.time_to_delivery_friday')
        saturday_from = res_config_settings.get_param('website_sale_hour.time_from_delivery_saturday')

        saturday_to = res_config_settings.get_param('website_sale_hour.time_to_delivery_saturday')

        current_uid = request.env.user
        tz = pytz.timezone(current_uid.tz or 'Australia/Brisbane')
        this_day1 = datetime.datetime.now(tz)
        day_value = this_day1.strftime('%A')
        time_from = ''
        time_to = ''
        if day_value == 'Sunday':
            time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(sunday_from) * 60, 60))
            time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(sunday_to) * 60, 60))
        elif day_value == 'Monday':
            time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(monday_from) * 60, 60))
            time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(monday_to) * 60, 60))
        elif day_value == 'Tuesday':
            time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(tuesday_from) * 60, 60))
            time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(tuesday_to) * 60, 60))
        elif day_value == 'Wednesday':
            time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(wednesday_from) * 60, 60))
            time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(wednesday_to) * 60, 60))
        elif day_value == 'Thursday':
            time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(thursday_from) * 60, 60))
            time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(thursday_to) * 60, 60))
        elif day_value == 'Friday':
            time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(friday_from) * 60, 60))
            time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(friday_to) * 60, 60))
        elif day_value == 'Saturday':
            time_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(saturday_from) * 60, 60))
            time_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(saturday_to) * 60, 60))

        days = [0, 1, 2, 3, 4, 5, 6]

        this_day_1 = this_day1.weekday()
        # this_time1 = datetime.datetime.now()
        # this_time = this_time1.strftime('%H:%M')

        tz = pytz.timezone('Australia/Brisbane')
        this_day1 = datetime.datetime.now(tz)
        this_day = this_day1.weekday()
        this_time2 = datetime.datetime.now(tz)
        this_time1 = this_time2.replace(tzinfo=None)
        this_timee = this_time1.strftime('%H:%M')
        this_time = this_timee

        if this_time >= time_from and this_time <= time_to:
            return {'open_time': "", 'status': True}
        else:
            open_time = ""
            if time_from > this_time and time_to > this_time:
                open_time = "Deliveries will be available on Today" + " from " + str(time_from) + " to " + str(time_to)
            elif time_from < this_time and time_to < this_time:
                time_from_data = ''
                time_to_data = ''
                day = ''
                if day_value == 'Sunday':
                    time_from_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(monday_from) * 60, 60))
                    time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(monday_to) * 60, 60))
                    day = 'Monday'
                    if time_from_data == '00:00' or time_to_data == '00:00':
                        time_from_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(tuesday_from) * 60, 60))
                        time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(tuesday_to) * 60, 60))
                        day = 'Tuesday'
                        if time_from_data == '00:00' or time_to_data == '00:00':
                            time_from_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(wednesday_from) * 60, 60))
                            time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(wednesday_to) * 60, 60))
                            day = 'Wednesday'
                            if time_from_data == '00:00' or time_to_data == '00:00':
                                time_from_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(thursday_from) * 60, 60))
                                time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(thursday_to) * 60, 60))
                                day = 'Thursday'
                                if time_from_data == '00:00' or time_to_data == '00:00':
                                    time_from_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(friday_from) * 60, 60))
                                    time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(friday_to) * 60, 60))
                                    day = 'Friday'
                                    if time_from_data == '00:00' or time_to_data == '00:00':
                                        time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(float(saturday_from) * 60, 60))
                                        time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(float(saturday_to) * 60, 60))
                                        day = 'Saturday'
                                        if time_from_data == '00:00' or time_to_data == '00:00':
                                            time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                                *divmod(float(sunday_from) * 60, 60))
                                            time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                                *divmod(float(sunday_to) * 60, 60))
                                            day = 'Sunday'

                elif day_value == 'Monday':
                    time_from_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(tuesday_from) * 60, 60))
                    time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(tuesday_to) * 60, 60))
                    day = 'Tuesday'
                    if time_from_data == '00:00' or time_to_data == '00:00':
                        time_from_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(wednesday_from) * 60, 60))
                        time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(wednesday_to) * 60, 60))
                        day = 'Wednesday'
                        if time_from_data == '00:00' or time_to_data == '00:00':
                            time_from_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(thursday_from) * 60, 60))
                            time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(thursday_to) * 60, 60))
                            day = 'Thursday'
                            if time_from_data == '00:00' or time_to_data == '00:00':
                                time_from_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(friday_from) * 60, 60))
                                time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(friday_to) * 60, 60))
                                day = 'Friday'
                                if time_from_data == '00:00' or time_to_data == '00:00':
                                    time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                        *divmod(float(saturday_from) * 60, 60))
                                    time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(saturday_to) * 60, 60))
                                    day = 'Saturday'
                                    if time_from_data == '00:00' or time_to_data == '00:00':
                                        time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(float(sunday_from) * 60, 60))
                                        time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(sunday_to) * 60, 60))
                                        day = 'Sunday'
                                        if time_from_data == '00:00' or time_to_data == '00:00':
                                            time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                                *divmod(float(monday_from) * 60, 60))
                                            time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                                *divmod(float(monday_to) * 60, 60))
                                            day = 'Monday'
                elif day_value == 'Tuesday':
                    time_from_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(wednesday_from) * 60, 60))
                    time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(wednesday_to) * 60, 60))
                    day = 'Wednesday'
                    if time_from_data == '00:00' or time_to_data == '00:00':
                        time_from_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(thursday_from) * 60, 60))
                        time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(thursday_to) * 60, 60))
                        day = 'Thursday'
                        if time_from_data == '00:00' or time_to_data == '00:00':
                            time_from_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(friday_from) * 60, 60))
                            time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(friday_to) * 60, 60))
                            day = 'Friday'
                            if time_from_data == '00:00' or time_to_data == '00:00':
                                time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod(float(saturday_from) * 60, 60))
                                time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(saturday_to) * 60, 60))
                                day = 'Saturday'
                                if time_from_data == '00:00' or time_to_data == '00:00':
                                    time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                        *divmod(float(sunday_from) * 60, 60))
                                    time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(sunday_to) * 60, 60))
                                    day = 'Sunday'
                                    if time_from_data == '00:00' or time_to_data == '00:00':
                                        time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(float(monday_from) * 60, 60))
                                        time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(float(monday_to) * 60, 60))
                                        day = 'Monday'
                                    if time_from_data == '00:00' or time_to_data == '00:00':
                                        time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(float(tuesday_from) * 60, 60))
                                        time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(float(tuesday_to) * 60, 60))
                                        day = 'Tuesday'
                elif day_value == 'Wednesday':
                    print("opopopo")
                    time_from_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(thursday_from) * 60, 60))
                    time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(thursday_to) * 60, 60))
                    day = 'Thursday'
                    if time_from_data == '00:00' or time_to_data == '00:00':
                        time_from_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(friday_from) * 60, 60))
                        time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(friday_to) * 60, 60))
                        day = 'Friday'
                        if time_from_data == '00:00' or time_to_data == '00:00':
                            time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                *divmod(float(saturday_from) * 60, 60))
                            time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(saturday_to) * 60, 60))
                            day = 'Saturday'
                            if time_from_data == '00:00' or time_to_data == '00:00':
                                time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod(float(sunday_from) * 60, 60))
                                time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(sunday_to) * 60, 60))
                                day = 'Sunday'
                                if time_from_data == '00:00' or time_to_data == '00:00':
                                    time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                        *divmod(float(monday_from) * 60, 60))
                                    time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                        *divmod(float(monday_to) * 60, 60))
                                    day = 'Monday'
                                if time_from_data == '00:00' or time_to_data == '00:00':
                                    time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                        *divmod(float(tuesday_from) * 60, 60))
                                    time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                        *divmod(float(tuesday_to) * 60, 60))
                                    day = 'Tuesday'
                                    if time_from_data == '00:00' or time_to_data == '00:00':
                                        time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(float(wednesday_from) * 60, 60))
                                        time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(float(wednesday_to) * 60, 60))
                                        day = 'Wednesday'
                elif day_value == 'Thursday':
                    time_from_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(friday_from) * 60, 60))
                    time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(friday_to) * 60, 60))
                    day = 'Friday'
                    if time_from_data == '00:00' or time_to_data == '00:00':
                        time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                            *divmod(float(saturday_from) * 60, 60))
                        time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(saturday_to) * 60, 60))
                        day = 'Saturday'
                        if time_from_data == '00:00' or time_to_data == '00:00':
                            time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                *divmod(float(sunday_from) * 60, 60))
                            time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(sunday_to) * 60, 60))
                            day = 'Sunday'
                            if time_from_data == '00:00' or time_to_data == '00:00':
                                time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod(float(monday_from) * 60, 60))
                                time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod(float(monday_to) * 60, 60))
                                day = 'Monday'
                            if time_from_data == '00:00' or time_to_data == '00:00':
                                time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod(float(tuesday_from) * 60, 60))
                                time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod(float(tuesday_to) * 60, 60))
                                day = 'Tuesday'
                                if time_from_data == '00:00' or time_to_data == '00:00':
                                    time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                        *divmod(float(wednesday_from) * 60, 60))
                                    time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                        *divmod(float(wednesday_to) * 60, 60))
                                    day = 'Wednesday'
                                    if time_from_data == '00:00' or time_to_data == '00:00':
                                        time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(float(thursday_from) * 60, 60))
                                        time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(float(thursday_to) * 60, 60))
                                        day = 'Thursday'
                elif day_value == 'Friday':
                    time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                        *divmod(float(saturday_from) * 60, 60))
                    time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(saturday_to) * 60, 60))
                    day = 'Saturday'
                    if time_from_data == '00:00' or time_to_data == '00:00':
                        time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                            *divmod(float(sunday_from) * 60, 60))
                        time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(sunday_to) * 60, 60))
                        day = 'Sunday'
                        if time_from_data == '00:00' or time_to_data == '00:00':
                            time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                *divmod(float(monday_from) * 60, 60))
                            time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                *divmod(float(monday_to) * 60, 60))
                            day = 'Monday'
                        if time_from_data == '00:00' or time_to_data == '00:00':
                            time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                *divmod(float(tuesday_from) * 60, 60))
                            time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                *divmod(float(tuesday_to) * 60, 60))
                            day = 'Tuesday'
                            if time_from_data == '00:00' or time_to_data == '00:00':
                                time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod(float(wednesday_from) * 60, 60))
                                time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod(float(wednesday_to) * 60, 60))
                                day = 'Wednesday'
                                if time_from_data == '00:00' or time_to_data == '00:00':
                                    time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                        *divmod(float(thursday_from) * 60, 60))
                                    time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                        *divmod(float(thursday_to) * 60, 60))
                                    day = 'Thursday'
                                    if time_from_data == '00:00' or time_to_data == '00:00':
                                        time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(float(friday_from) * 60, 60))
                                        time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(float(friday_to) * 60, 60))
                                        day = 'Friday'

                elif day_value == 'Saturday':
                    time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                        *divmod(float(sunday_from) * 60, 60))
                    time_to_data = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(sunday_to) * 60, 60))
                    day = 'Sunday'
                    if time_from_data == '00:00' or time_to_data == '00:00':
                        time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                            *divmod(float(monday_from) * 60, 60))
                        time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                            *divmod(float(monday_to) * 60, 60))
                        day = 'Monday'
                    if time_from_data == '00:00' or time_to_data == '00:00':
                        time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                            *divmod(float(tuesday_from) * 60, 60))
                        time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                            *divmod(float(tuesday_to) * 60, 60))
                        day = 'Tuesday'
                        if time_from_data == '00:00' or time_to_data == '00:00':
                            time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                *divmod(float(wednesday_from) * 60, 60))
                            time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                *divmod(float(wednesday_to) * 60, 60))
                            day = 'Wednesday'
                            if time_from_data == '00:00' or time_to_data == '00:00':
                                time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod(float(thursday_from) * 60, 60))
                                time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                    *divmod(float(thursday_to) * 60, 60))
                                day = 'Thursday'
                                if time_from_data == '00:00' or time_to_data == '00:00':
                                    time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                        *divmod(float(friday_from) * 60, 60))
                                    time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                        *divmod(float(friday_to) * 60, 60))
                                    day = 'Friday'
                                    if time_from_data == '00:00' or time_to_data == '00:00':
                                        time_from_data = '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(float(saturday_from) * 60, 60))
                                        time_to_data = '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(float(saturday_to) * 60, 60))
                                        day = 'Saturday'

                if time_from_data == '00:00':
                    open_time = "Deliveries aren’t available at the restaurant this week"
                else:
                    open_time = "Deliveries will be available on " + day + " from " + str(
                        time_from_data) + " to " + str(time_to_data)
            return {'open_time': open_time, 'status': False}

    @http.route('/pickup/type', csrf=False, type='json', auth="public")
    def CurbSidePickup(self, **kw):

        res_config_settings = request.env['ir.config_parameter'].sudo()
        curb_side_pickup = res_config_settings.get_param('website_sale_hour.curb_side_pickup')
        if curb_side_pickup:
            return True
        else:
            return False

    @http.route('/pickup/type/delivery', csrf=False, type='json', auth="public")
    def WebsiteDelivery(self, **kw):

        res_config_settings = request.env['ir.config_parameter'].sudo()
        website_delivery = res_config_settings.get_param('website_sale_hour.website_delivery')
        if website_delivery:
            return True
        else:
            return False

    @http.route('/get/vehicle/details', csrf=False, type='json', auth="public")
    def VehicleDetails(self, **kw):

        vehicle_type = request.env['vehicle.type'].sudo().search([])
        vehicle_make = request.env['vehicle.make'].sudo().search([])
        vehicle_location = request.env['vehicle.location'].sudo().search([])
        location = []
        make = []
        type = []
        if vehicle_type:
            for i in vehicle_type:
                type.append(i.type_name)
        if vehicle_make:
            for i in vehicle_make:
                make.append(i.make_name)
        if vehicle_location:
            for i in vehicle_location:
                location.append(i.location_name)

        vals = {'type': type, 'make': make, 'location': location}
        return vals

    @http.route(['/delivery/autofill/crust'], type='json', auth="public", website=True)
    def DeliveryAutofill(self, id=None, **kw):
        uid = request.session.uid
        if uid:
            employee = request.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
            login_id = employee.partner_id
            details = {"name": login_id.name, 'mobile': login_id.phone, 'email': login_id.email,
                       }
            # 'vcolor': login_id.vehicle_color, 'plate_no': login_id.license_plate_no
            return details
        else:
            return False

    @http.route(['/shop/delivery/type'], type='http', methods=['GET', 'POST'], auth="public", website=True,
                sitemap=False)
    def shopDeliveryType(self, **kw):
        # Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()
        if order:
            render_values = {
                'website_sale_order': order,
            }
            return request.render("order_location.order_delivery", render_values)
        else:
            return request.redirect("/")

    @http.route('/calculate/company/location', type='json', csrf=False, auth="none")
    def CalculateDistanceCompanyLocation(self, **kw):
        # Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        delivery_locations = request.env['res.company'].sudo().search([])
        d = []
        obj = False
        for i in delivery_locations:
            a = {
                'logo': "/web/image/res.company/%s/logo" % (i.id),
                'latitude': i.latitude,
                'longitude': i.longitude,
                'delivery_radius': i.delivery_radius,
                'name': i.name,
                'company': i.name,
                'company_id': i.id,
            }
            d.append(a)
        return d

    @http.route('/calculate/distance/info', type='json', csrf=False, auth="none")
    def CalculateDistanceInfo(self, **kw):
        # kw = request.httprequest.data
        distance = False
        latitude = kw['lat']
        longitude = kw['long']
        print(latitude)
        print(longitude)
        delivery_radius = 0
        valid = False
        nearest_location = []
        delivery_locations = request.env['res.company'].sudo().search([])
        for loc in delivery_locations:
            delivery_location = (loc.latitude, loc.longitude)
            partner_latitude_map = str(latitude)
            partner_longitude_map = str(longitude)
            if partner_latitude_map and partner_latitude_map:
                partner_loaction = (partner_latitude_map, partner_longitude_map)

                api_key = 'AIzaSyCP8gcIkivceoSrgmYTq0_XxTHd6l5rNFM'
                gmaps = googlemaps.Client(key=api_key)

                origin = (loc.latitude, loc.longitude)
                destinations = (partner_latitude_map, partner_longitude_map)

                actual_distance = []

                # for destination in destinations:
                result1 = \
                    gmaps.distance_matrix(origin, destinations, mode='driving')["rows"][0]["elements"][0]["distance"]["value"]
                print("ddd",result1)
                result = result1 / 1000
                actual_distance.append(result)



                convert_to_mile = loc.delivery_radius/1.609
                print("acttttttt",actual_distance[0],loc.delivery_radius)
                if actual_distance[0] <= loc.delivery_radius:

                    geolocator = Nominatim(user_agent="OnItBurgers")
                    location = geolocator.reverse(latitude + "," + longitude)
                    location_data = location.raw
                    nearest_location.append({
                        'company_name': loc.name,
                        'id': loc.id,
                        'distance': actual_distance[0],
                        'delivery_radius': delivery_radius,
                        'status': 'success',
                        'house_no': location_data.get('address').get('house_number', False),
                        'road': location_data.get('address').get('road', False),
                        'suburb': location_data.get('address').get('suburb', False),
                        'city': location_data.get('address').get('city', False),
                        'postcode': location_data.get('address').get('postcode', False),
                    })
                    valid = True
            #         break
            # else:
            #     valid = False

        if valid:
            # geolocator = Nominatim(user_agent="OnItBurgers")
            # location = geolocator.reverse(latitude + "," + longitude)
            # location_data = location.raw
            # data = {'status': 'success',
            #         'house_no': location_data.get('address').get('house_number', False),
            #         'road': location_data.get('address').get('road', False),
            #         'suburb': location_data.get('address').get('suburb', False),
            #         'city': location_data.get('address').get('city', False),
            #         'postcode': location_data.get('address').get('postcode', False),
            #         }
            # print("asdad", data)
            return json.dumps(nearest_location)
        else:
            data = {'status': 'failed', 'distance': delivery_radius}
            return json.dumps(data)

    @http.route('/calculate/distance/company', type='json', csrf=False, auth="none")
    def CalculateDistanceInfoCompany(self, **kw):
        # kw = request.httprequest.data
        latitude = kw['lat']
        longitude = kw['long']
        print(latitude)
        print(longitude)
        delivery_radius = 0
        valid = False
        company_info = request.env['res.company'].sudo().search([])
        # delivery_locations = request.env['delivery.location'].sudo().search([])
        company_list = []
        for company in company_info:
            # for location in company.delivery_location1:
            delivery_location = (company.latitude, company.longitude)
            partner_latitude_map = str(latitude)
            partner_longitude_map = str(longitude)
            if partner_latitude_map and partner_latitude_map:
                partner_loaction = (partner_latitude_map, partner_longitude_map)

                api_key = 'AIzaSyCP8gcIkivceoSrgmYTq0_XxTHd6l5rNFM'
                gmaps = googlemaps.Client(key=api_key)

                origin = (company.latitude, company.longitude)
                destinations = (partner_latitude_map, partner_longitude_map)
                print("distance",destinations)
                actual_distance = []

                # for destination in destinations:
                result = \
                    gmaps.distance_matrix(origin, destinations, mode='driving')["rows"][0]["elements"][0]["distance"][
                        "value"]
                result = result / 1000
                actual_distance.append(result)
                if actual_distance[0] <= company.delivery_radius:
                    a = {
                        'company': company.id,
                        'company_name': str(company.name) + "" + str(company.street) + "" + str(
                            company.street2) + "" + str(company.city),
                    }
                    company_list.append(a)

        return company_list

    @http.route('/order/location/company', type='json', csrf=False, auth="none")
    def CalculateDistanceLocationC(self, **kw):
        company = kw['company']
        street1 = kw['street1']
        street2 = kw['street2']
        city = kw['city']
        zip = kw['zip']
        order_id = kw['order_id']
        sale_order = request.env['sale.order'].sudo().search([('id', '=', int(order_id))], limit=1)
        obj = sale_order.sudo().write({
            'company_id': int(company),
            'street1': street1,
            'street2': street2,
            'city': city,
            'zip': zip,
        })
        if obj:
            return True
        else:
            return False
