# -*- coding: utf-8 -*-

from email.policy import default
from odoo import models, fields, api


class servicio_emanuel(models.Model):
    _name = 'odoo_emanuel.servicio_emanuel'
    _description = 'odoo_emanuel.servicio_emanuel'

    name = fields.Char("Nombre del Servicio", required=True)
    activo = fields.Boolean('Activo', default=True)
