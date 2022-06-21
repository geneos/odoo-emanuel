from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    servicio_adquirido_ids = fields.One2many(comodel_name='odoo_emanuel.servicio_adquirido', inverse_field='partner_id', string='Servicios')
