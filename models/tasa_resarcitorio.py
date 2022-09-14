from odoo import models, fields

class tasa_resarcitorio(models.Model):
    _name = 'odoo_emanuel.tasa_resarcitorio'
    _description = 'Tasa resarcitorio'

    tasa = fields.Float('Tasa de resarcitorio', digits=(16, 2))
   