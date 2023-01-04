# Company: giordano.ch AG
# Copyright by: giordano.ch AG
# https://giordano.ch/

import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PortalAccount(http.Controller):
    @http.route("/account/save/Fl_name_picture", type="json", auth="user")
    def save_first_last_name_picture(self, **kw):
        partner = request.env.user.partner_id
        name = self.concat_name(kw.get("first_name"), kw.get("last_name"))
        if kw.get("image"):
            img = kw.get("image").split(",")[1]
            values = {"name": name, "image_1920": img}
        else:
            values = {
                "name": name,
            }
        if partner.sudo().write(values):
            return True

    def concat_name(self, first, last):
        return first + " " + last

    @http.route("/change/password", type="json", auth="user")
    def portal_change_password(self, **kw):
        res_users = request.env["res.users"].sudo()
        password = kw.get("password")
        new_pw = kw.get("conf_password")
        access = self.portal_authenticate(password, res_users)
        uid = request.uid
        if access:
            change_pw = self.update_password(res_users, uid, new_pw)
            return "change" if change_pw else "nochange"
        else:
            return "error"

    def update_password(self, res_users, uid, new_pw):
        ctx = res_users._crypt_context()
        hash_password = ctx.hash if hasattr(ctx, "hash") else ctx.encrypt
        query = "UPDATE res_users SET password=%s WHERE id=%s"
        request.cr.execute(query, (hash_password(new_pw), uid))
        return True

    @http.route("/change/email", type="json", auth="user")
    def portal_change_email(self, **kw):
        res_users = request.env["res.users"].sudo()
        email = kw.get("conf_new_email")
        check_login = self.check_exist_login(email, res_users)
        if not check_login:
            res_partner = request.env["res.partner"].sudo()
            password = kw.get("password")
            access = self.portal_authenticate(password, res_users)
            if access:
                vals = {
                    "res_users": res_users,
                    "res_partner": res_partner,
                    "email": email,
                }
                email_change = self.change_email(vals)
                return "change" if email_change else "nochange"
            else:
                return "error"
        else:
            return "exist"

    def change_email(self, vals):
        uid = request.uid
        partner_id = request.env.user.partner_id.id
        user = vals.get("res_users").search([("id", "=", uid)])
        partner = vals.get("res_partner").search([("id", "=", partner_id)])
        user_val = user.write({"login": vals.get("email")})
        partner_val = partner.write({"email": vals.get("email")})
        return user_val and partner_val if user_val and partner_val else False

    def check_exist_login(self, email, res_users):
        return (
            res_users.search([("login", "=", email)])
            if res_users.search([("login", "=", email)])
            else False
        )

    def portal_authenticate(self, password, res_users):
        uid = request.uid
        assert password
        request.cr.execute(
            "SELECT COALESCE(password, '') FROM res_users WHERE id=%s", [uid]
        )
        [hashed] = request.cr.fetchone()
        crypt = res_users._crypt_context()
        valid, replacement = crypt.verify_and_update(password, hashed)
        if replacement is not None:
            res_users._set_encrypted_password(request.uid, replacement)
        if not valid:
            return False
        else:
            return True
