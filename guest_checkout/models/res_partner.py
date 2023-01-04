from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ResPartnerAccountReceivablePayable(models.Model):
    _inherit = 'res.partner'

    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
                                                  string="Account Payable",
                                                  domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
                                                  help="This account will be used instead of the default one as the payable account for the current partner",
                                                  required=False)
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
                                                     string="Account Receivable",
                                                     domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
                                                     help="This account will be used instead of the default one as the receivable account for the current partner",
                                                     required=False)

    def create(self, vals_list):
        res = super(ResPartnerAccountReceivablePayable, self).create(vals_list)
        payable = self.env['account.account'].search([('internal_type', '=', 'payable'), ('deprecated', '=', False)],
                                                     limit=1)
        receivable = self.env['account.account'].search(
            [('internal_type', '=', 'receivable'), ('deprecated', '=', False)], limit=1)
        if payable and receivable:
            res.write({'property_account_payable_id': payable.id,
                       'property_account_receivable_id': receivable.id})

        return res
