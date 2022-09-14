from odoo import models, fields

class tasa_venta(models.Model):
    _name = 'odoo_emanuel.tasa_venta'
    _description = 'Tasa venta'

    tasa = fields.Float('Tasa de venta', digits=(16, 2))
   