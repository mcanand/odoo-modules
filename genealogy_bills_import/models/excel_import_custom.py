# -*- coding: utf-8 -*-
from odoo import fields, models, _, api


class XlImportCustom(models.Model):
    _name = 'excel.import.custom'

    name = fields.Char(string="Name", readonly=True, required=True,
                       default='new')
    product_id = fields.Many2one('product.product', string="product",
                                 required=True)

    project_id = fields.Many2one('project.project', required=True)
    sub_project_id = fields.Many2one('project.sub.project', required=True,
                                     domain="[('project_id', '=', project_id)]")
    analytic_distribution = fields.Json(required=True)
    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get(
            "Percentage Analytic"),
    )
    total_payable_record = fields.Integer(
        string="Total net payable page/record", store=True,
        compute='_compute_total_payable_record')
    total_claimed_record = fields.Integer(
        string="Total agent claimed page/record", store=True,
        compute='_compute_total_claimed_record')
    total_amount = fields.Float(string="Total Amount", store=True,
                                compute='_compute_total_amount')
    sale_data_entry_ids = fields.One2many('sale.data.entries',
                                          'excel_import_custom_id',
                                          string="entries")
    state = fields.Selection(
        [('draft', 'Draft'), ('ready', 'Ready'), ('done', 'Done')],
        default='draft')
    purchase_order_count = fields.Integer(compute='compute_count_purchase')

    # @api.onchange('project_id')
    # def onchange_project_id(self):
    #     if self.project_id:
    #         return {
    #             'domain': {'sub_project_id': self.project_id.sub_project_ids}}

    @api.depends('purchase_order_count')
    def compute_count_purchase(self):
        """compute purchase order count"""
        orders = self.env['purchase.order'].search(
            [('csv_reference', '=', self.id)])
        self.write({'purchase_order_count': len(orders)})

    @api.depends('sale_data_entry_ids.payable')
    def _compute_total_payable_record(self):
        """compute total payable records from sale_data_entry_ids.payable"""
        total = 0
        for rec in self.sale_data_entry_ids:
            total += rec.payable
        self.write({'total_payable_record': total})

    @api.depends('sale_data_entry_ids.claimed')
    def _compute_total_claimed_record(self):
        """compute total claimed records from sale_data_entry_ids.payable"""
        total = 0
        for rec in self.sale_data_entry_ids:
            total += rec.claimed
        self.write({'total_claimed_record': total})

    @api.depends('sale_data_entry_ids.amount')
    def _compute_total_amount(self):
        """compute total amount from sale_data_entry_ids.amount"""
        total = 0
        for rec in self.sale_data_entry_ids:
            total += rec.amount
        self.write({'total_amount': total})

    def import_excel(self):
        """excel file import function return transient model to upload
        excel file"""
        return {
            'name': 'Upload',
            'type': 'ir.actions.act_window',
            'res_model': 'excel.upload',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    def validate(self):
        """Validate imported values and create purchase order and
        confirm then create a bill for corresponding order"""
        vals = {'refer_id': self.id,
                'product_id': self.product_id.id,
                'analytic_distribution': self.analytic_distribution,
                'project_id': self.project_id.id,
                'sub_project_id': self.sub_project_id.id}
        grouped_records = self.env['sale.data.entries'].read_group(
            [('excel_import_custom_id', '=', self.id)],
            fields=['vendor_id'], groupby=['vendor_id'])
        for rec in grouped_records:
            vals.update({'vendor_id': rec['vendor_id'][0]})
            vendor_entry = self.env['sale.data.entries'].search_read(
                [('excel_import_custom_id', '=', self.id),
                 ('vendor_id', '=', rec['vendor_id'][0])])
            order = self.create_purchase_order(vals, vendor_entry)
            order.button_confirm()
            order.action_create_invoice()
        self.write({'state': 'done'})
        for val in self.sale_data_entry_ids:
            val.write({'state': 'done'})

    def create_purchase_order(self, vals, vendor_entry):
        """create a new purchase order and order_line for corresponding
        values one by one"""
        purchase = self.env['purchase.order']
        p_order = purchase.create({'partner_id': vals.get('vendor_id'),
                                   'csv_reference': vals.get('refer_id'),
                                   'project_id': vals.get('project_id'),
                                   'sub_project_id': vals.get('sub_project_id'),
                                   'is_csv': True})
        for rec in vendor_entry:
            p_order.order_line.create(
                {'order_id': p_order.id,
                 'product_id': int(vals.get('product_id')),
                 'product_qty': rec['payable'],
                 'qty_received': rec['payable'],
                 'agent_claimed': rec['claimed'],
                 'difference': rec['difference'],
                 'reason': rec['reason'],
                 'analytic_distribution': vals.get('analytic_distribution'),
                 'agent_score': rec['agent_score'],
                 'price_unit': rec['agent_rate'],
                 'file_name': rec['file_name']})
        return p_order

    def cancel_entries(self):
        """delete imported entries in sale_data_entry_ids
        state changes to draft"""
        entries = self.sale_data_entry_ids
        for rec in entries:
            rec.unlink()
        self.write({'state': 'draft'})

    # def delete_record(self):
    #     if self.state == 'draft':
    #         self.unlink()

    def get_purchase_orders(self):
        """Redirect to purchase order for imported entry"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Purchase Orders",
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('csv_reference', '=', self.id)],
            'context': "{'create': False}"
        }
