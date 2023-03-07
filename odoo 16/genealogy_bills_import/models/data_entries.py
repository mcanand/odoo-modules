# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class SaleDataEntries(models.Model):
    _name = 'sale.data.entries'

    sl_no = fields.Integer(string="Sl No")
    file_name = fields.Char(string='File Name')
    psn = fields.Char(string="PSN")
    vendor_id = fields.Many2one('res.partner', string="Vendor",
                                compute="get_vendor_by_psn", store=True)
    payable = fields.Float(string='Net Payable Page/Record')
    agent_score = fields.Selection([('Avg', 'Avg'), ('Good', 'Good')],
                                   string="Agent Score")
    agent_rate = fields.Float(string="Agent Rate", store=True,
                              compute="get_agent_rate")
    claimed = fields.Float(string="Agent Claimed Page/Record")
    amount = fields.Float(string="Net Amount", store=True,
                          compute='_compute_amount')
    difference = fields.Integer(string="Difference", store=True,
                                compute='_compute_difference')
    reason = fields.Char(string="Reason")
    excel_import_custom_id = fields.Many2one('excel.import.custom')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Validated')],
                             default='draft')

    @api.depends('agent_score', 'agent_rate')
    def get_agent_rate(self):
        """get agent rate from corresponding products vendor price if
        agent rate is 'Avg' chooses price and if 'Good' then chooses Price2"""
        for rec in self:
            if rec.excel_import_custom_id.product_id.seller_ids:
                if rec.vendor_id in rec.excel_import_custom_id.product_id.seller_ids.partner_id:
                    for val in rec.excel_import_custom_id.product_id.seller_ids:
                        if rec.agent_score == "Avg":
                            rec.agent_rate = val.price
                        elif rec.agent_score == "Good":
                            rec.agent_rate = val.price2
                else:
                    raise ValidationError(
                        _("Please remember to add price list for "
                          "Vendor '"+rec.vendor_id.name+"' in product '"
                          + rec.excel_import_custom_id.product_id.name + "'"))

    @api.depends('psn')
    def get_vendor_by_psn(self):
        res_partner = self.env['res.partner']
        for rec in self:
            partner = res_partner.search([('psn', '=', rec.psn)], limit=1)
            if partner:
                rec.write({'vendor_id': partner.id})
            else:
                raise ValidationError(
                    _("Couldn't find a vendor, Please check PSN number " + rec.psn))

    @api.depends('payable', 'claimed')
    def _compute_difference(self):
        """compute difference of agent claimed page/record minus
         net payable page/record"""
        for rec in self:
            diff = rec.claimed - rec.payable
            rec.write({'difference': diff})

    @api.depends('payable', 'agent_rate')
    def _compute_amount(self):
        """calculate total amount of net payable page/record * agent_rate"""
        for rec in self:
            total = rec.payable * rec.agent_rate
            rec.write({'amount': total})
