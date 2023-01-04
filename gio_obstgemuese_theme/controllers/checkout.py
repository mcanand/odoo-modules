# Company: giordano.ch AG
# Copyright by: giordano.ch AG
# https://giordano.ch/


from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class WebsiteSaleInherit(WebsiteSale):
    @http.route("/process/checkout/page",type="http",auth="public")
    def process_checkout_custom(self, **post):
        order = request.website.sale_get_order()
        values = self.checkout_values(**post)
        values.update({"website_sale_order": order})
        template = "gio_obstgemuese_theme.custom_checkout_obst"
        redirection = self.checkout_redirection(order)
        if redirection:
            return request.redirect("/shop")
        order_partner_id = order.partner_id.id
        user_partner_id = request.website.user_id.sudo().partner_id.id
        values.update({
            "order_partner_id": order_partner_id,
             "user_partner_id": user_partner_id,
        })
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:

            return request.render(template,values)
        render_values = self._get_shop_payment_values(order, **post)
        render_values["only_services"] = order and order.only_services or False

        if render_values["errors"]:
            render_values.pop("acquirers", "")
            render_values.pop("tokens", "")
        values.update(render_values)
        redirection = self.checkout_check_address(order)
        if redirection:
            return redirection

        if post.get("express"):
            return request.redirect("/shop/confirm_order")

        # Avoid useless rendering if called in ajax
        if post.get("xhr"):
            return "ok"
        return request.render(template, values)
