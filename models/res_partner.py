from datetime import date
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    baja = fields.Boolean('Dado de baja', default=False)
    servicio_adquirido_ids = fields.One2many('odoo_emanuel.servicio_adquirido', 'partner_id', string='Servicios')
