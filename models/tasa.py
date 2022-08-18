from odoo import models, fields

class tasa(models.Model):
    _name = 'odoo_emanuel.tasa'
    _description = 'Tasa'
    _rec_name = 'tasa'

    tasa = fields.Float('Tasa')
   