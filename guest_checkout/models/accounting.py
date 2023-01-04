from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ResPartnerAccountReceivablePayable(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        """Automatically send invoice email"""
        res = super(ResPartnerAccountReceivablePayable, self).action_post()
        if self:
            template = self.env.ref(self._get_mail_template(), raise_if_not_found=False)
            template.send_mail(self.id, force_send=True)
        return res