from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

MASS_MAILING_BUSINESS_MODELS = [
    'crm.lead',
    'event.registration',
    'hr.applicant',
    'res.partner',
    'event.track',
    'sale.order',
    'mailing.list',
    'mailing.contact',
    'loyalist.contacts',
]


class MassMailing(models.Model):
    """ MassMailing models a wave of emails for a mass mailign campaign.
    A mass mailing is an occurence of sending emails. """
    _inherit = 'mailing.mailing'

    mailing_model_id = fields.Many2one(
        'ir.model', string='Recipients Model', ondelete='cascade', required=True,
        domain=[('model', 'in', MASS_MAILING_BUSINESS_MODELS)],
        default=lambda self: self.env.ref('mass_mailing.model_mailing_list').id)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    loyalist_contacts = fields.Many2one(string="loyalist contacts")
    loyalist_boolean = fields.Boolean(string="Loyalist Boolean", compute='get_details_for_filter')

    @api.model
    def get_details_for_filter(self):
        check_loyalist = self.env['loyalist.contacts'].search([('loyalist_contact', '=', self.id)])
        if not check_loyalist:
            loyalist_contacts = self.env['loyalist.contacts'].sudo().create({
                'loyalist_contact': self.id,
            })
            self.loyalist_boolean = True
        else:
            self.loyalist_boolean = False

    def click_btn_contact(self):
        print("x")


class Loyalist(models.Model):
    _name = 'loyalist.contacts'

    loyalist_contact = fields.Many2one()

    # @api.depends('loyalist_contact')
    # @api.model
    # def _get_partner(self):
    #     partner = self.env['res.partner'].search([('user_id','=',True)])
    #     self.loyalist_contact = partner
    #     return partner
