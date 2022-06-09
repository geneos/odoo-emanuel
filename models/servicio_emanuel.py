# -*- coding: utf-8 -*-

from email.policy import default
from odoo import models, fields, api


class servicio_emanuel(models.Model):
    _name = 'odoo_emanuel.servicio_emanuel'
    _description = 'Servicios Emanuel'
    _rec_name = 'name'

    name = fields.Char("Nombre del Servicio", required=True)
    es_servicio_interes = fields.Boolean('Es Servicio de Interés', default=False)
    activo = fields.Boolean('Activo', default=True)
