from odoo import models, api, fields
from odoo.http import request
import datetime
import calendar
from dateutil.relativedelta import relativedelta
import numpy as np
import random


class Employee(models.Model):
    _inherit = 'res.users'

    @api.model
    def get_measat_dashboard(self):
        uid = request.session.uid

        cr = self.env.cr
        employee = self.env['res.users'].sudo().search_read([('id', '=', uid)], limit=1)

        # Pending Order Count
        pending_orders_count = len(self.env['sale.order'].search(
            [('partner_id.is_distributor', '=', True), ('order_line.product_id.categ_id.name', '=', 'Prepaid Voucher'),
             ('state', '=', 'draft')]))

        # Pending Order Table

        query = """select so.name as so,pt.name  as voucher_plan,product_uom_qty as qty,price_unit as value,so.amount_total as total,
invoice_payment_state,rp.distributor_discount as discount,rp.name as p_name from sale_order as so
                                join sale_order_line as sol  on  sol.order_id = so.id 
                                left join account_move as am on am.ref = so.name
                                left join res_partner as rp on rp.id = so.partner_id
                                left join product_product as pp on pp.id = sol.product_id
                                left join product_template as pt on pt.id = pp.product_tmpl_id
                                left join product_category as pc on pc.id = pt.categ_id
                                where so.state = 'draft' and pc.name='Prepaid Voucher'"""

        self._cr.execute(query)
        orders = self._cr.dictfetchall()

        distributor_query = """select r_p.name as name from res_users as r_u
                                           join res_partner as r_p ON r_u.partner_id = r_p.id
                                           where r_p.is_distributor = 'True'"""

        self._cr.execute(distributor_query)
        distributor = self._cr.dictfetchall()

        # Total Sale amount
        this_month_sales = 0.0
        month = datetime.date.today().month
        month_sale_order = []
        sales_amt = self.env['sale.order'].sudo().search([])
        for rec in sales_amt:
            if rec.date_order.month == month:
                month_sale_order.append(rec)
        for val in month_sale_order:
            this_month_sales += val.amount_total

        # Latest Jobs
        distributors = self.env['res.partner'].search([('is_distributor', '=', True)])
        latest_jobs = []
        jobs = self.env['measat.tbl.sites'].sudo().search([], order="id desc")
        for val in jobs:
            for dist in distributors:
                if val.installer_id.id == dist.id:
                    latest_jobs.append(val)
        count = 0
        latest = []
        for lat_job in latest_jobs:
            if count < 5:
                print(lat_job)
                latest.append({
                    'job_id': lat_job.id,
                    'cme_id': lat_job.cme_id,
                    'date': lat_job.install_date,
                    'distributor': lat_job.installer_id.name
                })
                count += 1

            else:
                break

        month_booking_dataset = [0, 1, 2, 3, 4, 5, 6]
        print(latest,"latest")

        if employee:
            data = {
                'uid': uid,
                # 'colors': b_color,
                # 'd_name': d_name,
                'month_booking_dataset': month_booking_dataset,
                'pending_orders_count': pending_orders_count,
                'this_month_sales': this_month_sales,
                'latest_jobs': latest,
                'orders': orders,
                'distributor': distributor,
            }
            employee[0].update(data)
        return employee

    @api.model
    def get_sales_employee(self):
        distributor_no = self.env['res.partner'].search([('is_distributor', '=', True)])
        b_color = []
        for rec in distributor_no:
            color = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])]
            b_color.append(color)
        d_name = distributor_no.mapped('name')
        month = 12
        month_sale_order = []
        this_month_sales = []
        sales_amt = self.env['sale.order'].sudo().search([])
        count = 0
        for rec in sales_amt:
            if count <= 12:
                this_month_sales.append(rec.amount_total)
                count = count + 1
            else:
                break
        print(this_month_sales)
        distributors = self.env['res.partner'].search([('is_distributor', '=', True)])
        month_sale_order = []
        sales_amt = self.env['sale.order'].sudo().search([])
        count = 0
        year = fields.Date.today().year
        for rec in sales_amt:
            if rec.date_order.year == year:
                month_sale_order.append(rec)
        for val in month_sale_order:
            if count <= 12:
                this_month_sales.append(val.amount_total)
                count = count + 1

        r = [b_color, d_name,this_month_sales]

        return r

    @api.model
    def get_sales_distributor(self):
        distributors = self.env['res.partner'].search([('is_distributor', '=', True)])
        names = distributors.mapped('name')
        month_sale_order = []
        sales_amt = self.env['sale.order'].sudo().search([])
        count = 0
        year = fields.Date.today().year
        this_month_sales=[]
        for rec in sales_amt:
            if rec.date_order.year == year :
                if rec.partner_id.is_distributor:
                  month_sale_order.append(rec)
        for val in month_sale_order:
            if count <= 12:
                this_month_sales.append(val.amount_total)
                count = count + 1
        v = [this_month_sales,names]
        return v