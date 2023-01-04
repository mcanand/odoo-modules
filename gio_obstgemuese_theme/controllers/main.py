# Company: giordano.ch AG
# Copyright by: giordano.ch AG
# https://giordano.ch/

import logging

from odoo import _, http
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.mass_mailing.controllers import main
from odoo.exceptions import UserError
from odoo.http import request, route

_logger = logging.getLogger(__name__)


class AboutUsPage(http.Controller):
    @http.route("/about", type="http", website=True, auth="public")
    def about_us_redirect(self):
        return request.render("gio_obstgemuese_theme.about_us_obst")


class ProductsSearching(http.Controller):
    @http.route("/get/products", type="json", auth="public")
    def products_search(self, search_key):
        product_template = request.env["product.template"].sudo()
        if search_key:
            products = product_template.search([("name", "ilike", search_key)])
            vals = []
            for rec in products:
                val = {
                    "image": rec.image_1920,
                    "name": rec.name,
                    "price": rec.list_price,
                }
                vals.append(val)
            return vals


class ImpressumPageController(http.Controller):
    @http.route("/impressum/", type="http", auth="public", website=True)
    def show_impressum_webpage(self, **kw):
        return http.request.render("gio_obstgemuese_theme.impressum_page", {})


class ObCartCustom(http.Controller):
    @http.route("/remove/order/line", type="json", auth="public", website=True)
    def remove_sale_order_line(self, line_id):
        sale_order_line = request.env["sale.order.line"].sudo()
        order_line = sale_order_line.search([("id", "=", int(line_id))])
        if order_line:
            order_line.unlink()
            return True
        else:
            return False

    @http.route("/get/cart/values", type="json", auth="public", website=True)
    def get_sale_cart(self):
        order = request.website.sale_get_order()
        vals = []
        variants = []
        for line in order.order_line:
            val = {
                "product_name": line.product_id.name,
                "line_id": line.id,
                "product_img": line.product_id.image_1920,
                "qty": line.product_uom_qty,
                "price": line.price_unit,
                "symbol": line.currency_id.symbol,
            }
            for rec in line.product_id.product_template_attribute_value_ids:
                variants.append((rec.display_name).split(":")[1])
            val.update({"variant": variants})
            vals.append(val)
        return vals


class ProductDetails(http.Controller):
    @http.route("/get/product/details", type="json", auth="public")
    def get_product_details(self, product_id):
        product = (
            request.env["product.product"]
            .sudo()
            .search([("id", "=", product_id)], limit=1)
        )
        for rec in product:
            vals = {
                "name": rec.name,
                "price": rec.lst_price,
                "image": rec.image_1920,
                "description": rec.product_tmpl_id.description_sale,
            }
            return vals


class PanoramaConfig(http.Controller):
    @http.route("/get/panorama/config", type="json", auth="public")
    def get_panorama_config(self):
        record = request.env["panorama.view.config"].sudo().search([], limit=1)
        vals = []
        config = {
            "panorama_image": record.panorama_image,
            "auto_rotate": record.auto_rotate,
            "auto_rotate_value": record.auto_rotate_value,
        }
        for rec in record.hotspot_ids:
            hotspot_ids = {
                "pitch": rec.pitch,
                "yaw": rec.yaw,
                "product_id": rec.product_id.id,
            }
            vals.append(hotspot_ids)
        return config, vals


class RegistrationConfirmPassword(AuthSignupHome):
    def _prepare_signup_values(self, qcontext):
        key_vals = ("login", "name", "password")
        values = {key: qcontext.get(key) for key in key_vals}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        supported_lang_codes = [
            code for code, _ in request.env["res.lang"].get_installed()
        ]
        lang = request.context.get("lang", "")
        if lang in supported_lang_codes:
            values["lang"] = lang
        return values

    def get_partner_salutation(self, salutation):
        contact_title = request.env["res.partner.title"].sudo()
        if salutation == "women":
            shortcut = ("shortcut", "=", "Miss")
            salutation_id = contact_title.search([shortcut]).id
            return salutation_id
        elif salutation == "mister":
            shortcut = ("shortcut", "=", "Mr.")
            salutation_id = contact_title.search([shortcut]).id
            return salutation_id

    def get_country_id(self, val):
        country = request.env["res.country"].sudo()
        country_id = country.search([("code", "=", val)]).id or False
        return country_id

    def concat_name(self, first_name, last_name):
        return first_name + " " + last_name

    @http.route("/web/signup", type="http", auth="public", website=True)
    def web_auth_signup(self, *args, **kw):
        res = super(RegistrationConfirmPassword, self).web_auth_signup()
        salutation = kw.get("salutation")
        salutation_id = self.get_partner_salutation(salutation)
        res_partner = request.env["res.partner"].sudo()
        country = self.get_country_id(kw.get("country"))
        name = self.concat_name(kw.get("name"), kw.get("last_name"))
        partner = res_partner.search([("email", "=", kw.get("login"))])
        if partner:
            values = {
                "name": name,
                "type": "contact",
                "street": kw.get("street"),
                "city": kw.get("location"),
                "zip": kw.get("postcode"),
                "country_id": country,
                "title": salutation_id,
            }
            partner.write(values)
            if kw.get("delivery_name"):
                del_name = self.concat_name(
                    kw.get("delivery_name"), kw.get("delivery_last_name")
                )
                del_country = self.get_country_id(kw.get("delivery_country"))
                vals = {
                    "name": del_name,
                    "type": "delivery",
                    "street": kw.get("street"),
                    "city": kw.get("location"),
                    "zip": kw.get("zip"),
                    "country_id": del_country,
                }
                child = res_partner.create(vals)
                partner.write({"child_ids": child})
        return res


class MassMailController(main.MassMailController):
    @route("/web_mailing/subscribe", type="json", website=True, auth="public")
    def subscribe(self, cargobike, performance, list_id, email, **post):

        if not request.env["ir.http"]._verify_request_recaptcha_token(
            "website_mass_mailing_subscribe"
        ):
            return {
                "toast_type": "danger",
                "toast_content": _("Suspicious activity detected"),
            }
        mailing_contact_sub = request.env["mailing.contact.subscription"]
        ContactSubscription = mailing_contact_sub.sudo()
        Contacts = request.env["mailing.contact"].sudo()
        name, email = Contacts.get_name_email(email)
        lst_id = ("list_id", "=", int(list_id))
        email_id = ("contact_id.email", "=", email)
        subscription = ContactSubscription.search([lst_id, email_id], limit=1)
        if not subscription:
            # inline add_to_list as we've already called half of it
            contact_id = Contacts.search([("email", "=", email)], limit=1)
            if not contact_id:
                contact_id = Contacts.create(
                    {
                        "name": name,
                        "email": email,
                        "cargo_bike": cargobike,
                        "performance": performance,
                    }
                )
            ContactSubscription.create(
                {
                    "contact_id": contact_id.id,
                    "list_id": int(list_id),
                }
            )
        elif subscription.opt_out:
            subscription.opt_out = False
        # add email to session
        request.session["mass_mailing_email"] = email
        return {
            "toast_type": "success",
            "toast_content": _("Thanks for subscribing!"),
        }
