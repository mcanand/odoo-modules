from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PanoramaViewConfig(models.Model):
    _name = "panorama.view.config"
    _description = "panorama view configuration obst"

    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active", default=False)
    auto_rotate = fields.Boolean(string="Auto Rotate")
    auto_rotate_value = fields.Integer(string="Auto Rotate Value")
    panorama_image = fields.Binary()
    hotspot_ids = fields.One2many("panorama.view.hotspot", "hotspots")

    @api.constrains("active")
    def _check_active_config(self):
        if self.search_count([("active", "=", True)]) > 1:
            raise ValidationError(_("Only one active record at a time."))


class PanoramaViewHotspot(models.Model):
    _name = "panorama.view.hotspot"
    _description = "panorama view configuration Hotspots"

    pitch = fields.Float()
    yaw = fields.Float()
    product_id = fields.Many2one("product.product")
    hotspots = fields.Many2one("panorama.view.config")

    def select_pitch_yaw(self):
        view_id = self.env.ref("gio_obstgemuese_theme.panorama_hotspot_wizard")
        return {
            "type": "ir.actions.act_window",
            "name": _("Panorama Wizard View"),
            "res_model": "panorama.hotspot.wizard",
            "target": "new",
            "view_id": view_id.id,
            "view_mode": "form",
            "context": {
                "default_rec_id": self.id,
                "default_name": self.product_id.name,
            },
        }


class PanoramaWizard(models.TransientModel):
    _name = "panorama.hotspot.wizard"

    name = fields.Char()
    rec_id = fields.Integer(string="record_id")

    def action_done(self, pitch, yaw, rec_id):
        panorama_line = self.env["panorama.view.hotspot"]
        record = panorama_line.search([("id", "=", rec_id)])
        if record:
            rec = record.write({"pitch": pitch, "yaw": yaw})
            return rec
