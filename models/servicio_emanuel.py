# -*- coding: utf-8 -*-

from dataclasses import field
from email.policy import default
#from typing_extensions import Required
from odoo import models, fields, api


class servicio_emanuel(models.Model):
    _name = 'odoo_emanuel.servicio_emanuel'
    _description = 'Servicios Emanuel'
    _rec_name = 'name'

    name = fields.Char("Nombre del Servicio", required=True)
    es_servicio_interes = fields.Boolean('Es Servicio de Interés', default=False)
    es_servicio_costo_unico = fields.Boolean('Es Servicio de Costo Unico', default=False)
    costo_unico_servicio = fields.One2many('odoo_emanuel.linea_costo_unico', 'servicio_emanuel_id', 'Costo historico')
    activo = fields.Boolean('Activo', default=True)
    cuenta_contable = fields.Many2one('account.account', 'Cuenta contable')

class linea_costo_unico(models.Model):
    _name = 'odoo_emanuel.linea_costo_unico'
    _description = 'Linea de Costo Unico'

    servicio_emanuel_id = fields.Many2one('odoo_emanuel.servicio_emanuel', string="Servicio Emanuel", required=True)
    periodo_desde = fields.Many2one('odoo_emanuel.periodo', required=True)
    periodo_hasta = fields.Many2one('odoo_emanuel.periodo', required=True)
    costo = fields.Float('Costo',required=True)