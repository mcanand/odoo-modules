from odoo import api, fields, models, _, tools


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    country_id = fields.Many2one('res.country', string="Country")
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Char(string='State')

    def _get_website_registration_allowed_fields(self):
        return {'name', 'phone', 'email', 'mobile', 'event_id', 'partner_id', 'event_ticket_id', 'country_id'
            , 'street', 'street2', 'zip', 'city', 'state_id', 'offer', 'newsletter'}


class UsersInherit(models.Model):
    _inherit = 'res.users'

    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Char(string='State')
    receive_offer = fields.Boolean(string="Receive Offer")
    newsletter = fields.Boolean(string="subscribed to newsletter",
                                store=True,
                                readonly=False)
    # patient_seq = fields.Char()

    def create(self, vals_list):
        res = super().create(vals_list)
        mailing_contact = self.env['mailing.contact']
        contact = mailing_contact.search(
            [('mobile', '=', vals_list.get('mobile')), ('email', '=', vals_list.get('email'))])
        if contact:
            return res
        if not contact and vals_list.get('newsletter') == 'True':
            vals = {'name': vals_list.get('name'),
                    'mobile': vals_list.get('mobile'),
                    'email': vals_list.get('email'),
                    }
            con = mailing_contact.create(vals)
            con.subscription_list_ids.write({'list_id': 1, 'conact_id': con.id})
        return res


class MailingContactInherit(models.Model):
    _inherit = 'mailing.contact'

    mobile = fields.Char(string='Mobile Number')
