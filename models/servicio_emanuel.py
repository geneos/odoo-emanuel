# -*- coding: utf-8 -*-

from email.policy import default
from typing_extensions import Required
from odoo import models, fields, api


class servicio_emanuel(models.Model):
    _name = 'odoo_emanuel.servicio_emanuel'
    _description = 'Servicios Emanuel'
    _rec_name = 'name'

    name = fields.Char("Nombre del Servicio", required=True)
    es_servicio_interes = fields.Boolean('Es Servicio de Interés', default=False)
    es_servicio_costo_unico = fields.Boolean('Es Servicio de Costo Unico', default=False)
    costo_unico_servicio = fields.Many2one('odoo_emanuel.linea_costo_unico')
    activo = fields.Boolean('Activo', default=True)

class linea_costo_unico(models.Model):
    _name = 'odoo_emanuel.linea_costo_unico'
    _description = 'Linea de Costo Unico'
    _rec_name = 'name'

    periodo_desde = fields.Many2one('odoo_emanuel.periodo', required=True)
    periodo_hasta = fields.Many2one('odoo_emanuel.periodo', required=True)
    costo = fields.Float('Costo',required=True)