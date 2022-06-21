from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    servicio_adquirido_ids = fields.One2many('odoo_emanuel.servicio_adquirido', 'partner_id', string='Servicios')
