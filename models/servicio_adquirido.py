# -*- coding: utf-8 -*-

from email.policy import default
from odoo import models, fields, api


class servicio_adquirido(models.Model):
    _name = 'odoo_emanuel.servicio_adquirido'
    _description = 'Servicio adquirido'

    servicio = fields.Many2one('servicio_emanuel','Servicio')
    asociado = fields.Many2many('res.partner','Asociado')
    periodo_inicio = fields.Many2one('periodo')
    monto_total = fields.Float('Monto total')
    cantidad_cuotas = fields.Integer('Cantidad de cuotas')

class linea_servicio_adquirido(models.Model):
    _name = 'odoo_emanuel.linea_servicio_adquirido'
    _description = 'Linea servicio adquirido'

    nro_cuota = fields.Char('Cuota',size=7)
    servicio = fields.Many2one('servicio_emanuel','Servicio')
    fecha_vencimiento = fields.Date('Fecha de vencimiento')
    monto = fields.Float('Monto')
    saldo = fields.Float('Saldo')
    fecha_pago = fields.Date('Fecha de pago')
    pagado = fields.Boolean('Esta pago')