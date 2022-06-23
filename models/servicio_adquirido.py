# -*- coding: utf-8 -*-

from email.policy import default
from odoo import models, fields, api

class servicio_adquirido(models.Model):
    _name = 'odoo_emanuel.servicio_adquirido'
    _description = 'Servicio adquirido'

    servicio = fields.Many2one('servicio_emanuel','Servicio',required=True)
    partner_id = fields.Many2one('res.partner','Asociado',required=True)
    periodo_inicio = fields.Many2one('periodo',required=True)
    monto_total = fields.Float('Monto total',required=True)
    entrega_inicial = fields.Float('Entrega inicial',required=True)
    cantidad_cuotas = fields.Integer('Cantidad de cuotas',required=True)
    linea_servicio_adquirido_ids = fields.One2many('odoo_emanuel.linea_servicio_adquirido', 'servicio_adquirido_id', 'Cuotas')

    #def action_generar_lineas_servicio_adquirido(self):
    #    for account in self.browse(self.env.context['active_ids']):
    #        account.copy()
class linea_servicio_adquirido(models.Model):
    _name = 'odoo_emanuel.linea_servicio_adquirido'
    _description = 'Linea servicio adquirido'

    servicio_adquirido_id = fields.Many2one('odoo_emanuel.servicio_adquirido', string="Servicio Adquirido", required=True,readonly=True)
    nro_cuota = fields.Char('Cuota',size=7,readonly=True)
    servicio = fields.Many2one('servicio_emanuel','Servicio',readonly=True)
    fecha_vencimiento = fields.Date('Fecha de vencimiento',readonly=True)
    monto = fields.Float('Monto',readonly=True)
    monto_interes = fields.Float('Monto interes',readonly=True)
    monto_capital = fields.Float('Monto capital',readonly=True)
    saldo = fields.Float('Saldo',readonly=True)
    fecha_pago = fields.Date('Fecha de pago',readonly=True)
    pagado = fields.Boolean('Esta pago',readonly=True)

