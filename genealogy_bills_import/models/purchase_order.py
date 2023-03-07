# -*- coding: utf-8 -*-
from odoo import fields, api, models, _


class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    agent_claimed = fields.Integer(string="Agent Claimed")
    difference = fields.Integer(string="Difference")
    reason = fields.Char(string='Reason')
    file_name = fields.Char(string='File Name')
    agent_score = fields.Selection([('Avg', 'Avg'), ('Good', 'Good')],
                                   string="Agent Score")

    # @api.onchange('product_id')
    # def onchange_product_id(self):
    #     res = super(PurchaseOrderLineInherit, self).onchange_product_id()
    #     if self.order_id.is_csv:
    #         if self.product_id.seller_ids and self.order_id.partner_id in self.product_id.seller_ids.partner_id:
    #             for rec in self.product_id.seller_ids:
    #                 if self.agent_score == 'Avg':
    #                     self.price_unit = rec.price
    #                 elif self.agent_score == 'Good':
    #                     self.price_unit = rec.price2
    #     return res

    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLineInherit,
                    self)._prepare_account_move_line()
        if self.order_id.is_csv:
            res.update({'file_name': self.file_name,
                        'agent_claimed': self.agent_claimed,
                        'difference': self.difference,
                        'reason': self.reason,
                        'agent_score': self.agent_score,
                        })
        return res


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    is_csv = fields.Boolean(string='is csv entry', readonly=True)
    csv_reference = fields.Many2one('excel.import.custom',
                                    string='csv reference')
    project_id = fields.Many2one('project.project', string='project')
    sub_project_id = fields.Many2one('project.sub.project',
                                     domain="[('project_id', '=', project_id)]",
                                     string="Sub Project")

    # def action_create_invoice(self):
    #     res = super(PurchaseOrderInherit, self).action_create_invoice()
    #     return res

    def _prepare_invoice(self):
        res = super(PurchaseOrderInherit, self)._prepare_invoice()
        if self.is_csv:
            res.update({'is_csv': self.is_csv,
                        'csv_reference': self.csv_reference.id,
                        'project_id': self.project_id.id,
                        'sub_project_id': self.sub_project_id.id})
        return res


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    is_csv = fields.Boolean(string='is csv entry', readonly=True)
    csv_reference = fields.Many2one('excel.import.custom',
                                    string='csv reference')
    project_id = fields.Many2one('project.project', string='project')
    sub_project_id = fields.Many2one('project.sub.project',
                                     domain="[('project_id', '=', project_id)]",
                                     string="Sub Project")

    @api.model_create_multi
    def create(self, vals_list):
        """merge values before creating account move
        if purchase order is_csv true"""
        if vals_list[0].get('is_csv'):
            purchase_order = self.env['purchase.order'].search(
                [('name', '=', vals_list[0].get('invoice_origin'))])
            if purchase_order.is_csv:
                vals_list = self.prepare_vals_for_xl(vals_list)
        res = super(AccountMoveInherit, self).create(vals_list)
        return res

    def prepare_vals_for_xl(self, vals):
        """merge values before creating account move
        if purchase order is_csv true"""
        good_qty = 0
        avg_qty = 0
        good_dict = {}
        avg_dict = {}
        line = []
        good_files = []
        avg_files = []
        for val in vals[0].get('invoice_line_ids'):
            if val[2].get('agent_score') == 'Good':
                good_qty += val[2].get('quantity')
                good_files.append(val[2].get('file_name'))
                good_dict = {'display_type': val[2].get('display_type'),
                             'name': val[2].get('name'),
                             'product_id': val[2].get('product_id'),
                             'product_uom_id': val[2].get('product_uom_id'),
                             'quantity': good_qty,
                             'price_unit': val[2].get('price_unit'),
                             'tax_ids': val[2].get('tax_ids'),
                             'file_name': good_files,
                             'purchase_line_id': val[2].get(
                                 'purchase_line_id'),
                             'agent_claimed': val[2].get('agent_claimed'),
                             'difference': val[2].get('difference'),
                             'reason': val[2].get('reason'),
                             'agent_score': val[2].get('agent_score'),
                             'analytic_distribution': val[2].get(
                                 'analytic_distribution'),
                             'sequence': val[2].get('sequence')}
            elif val[2].get('agent_score') == 'Avg':
                avg_qty += val[2].get('quantity')
                avg_files.append(val[2].get('file_name'))
                avg_dict = {'display_type': val[2].get('display_type'),
                            'name': val[2].get('name'),
                            'product_id': val[2].get('product_id'),
                            'product_uom_id': val[2].get('product_uom_id'),
                            'quantity': avg_qty,
                            'price_unit': val[2].get('price_unit'),
                            'tax_ids': val[2].get('tax_ids'),
                            'file_name': avg_files,
                            'purchase_line_id': val[2].get(
                                'purchase_line_id'),
                            'agent_claimed': val[2].get('agent_claimed'),
                            'difference': val[2].get('difference'),
                            'reason': val[2].get('reason'),
                            'agent_score': val[2].get('agent_score'),
                            'analytic_distribution': val[2].get(
                                'analytic_distribution'),
                            'sequence': val[2].get('sequence')}
        good = (0, 0, good_dict)
        avg = (0, 0, avg_dict)
        if good[2]:
            line.append(good)
        if avg[2]:
            line.append(avg)
        vals[0].update({'invoice_line_ids': line})
        return vals


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    agent_claimed = fields.Integer(string="Agent Claimed")
    difference = fields.Integer(string="Difference")
    reason = fields.Char(string='Reason')
    file_name = fields.Char(string='File Name')
    agent_score = fields.Selection([('Avg', 'Avg'), ('Good', 'Good')],
                                   string="Agent Score")
