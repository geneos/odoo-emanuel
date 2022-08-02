# -*- coding: utf-8 -*-

import datetime
from email.policy import default
import string
from odoo import models, fields, api
from odoo.exceptions import UserError
#from odoo_emanuel.models.account_payment import account_payment

class servicio_adquirido(models.Model):
    _name = 'odoo_emanuel.servicio_adquirido'
    _description = 'Servicio adquirido'

    servicio = fields.Many2one('odoo_emanuel.servicio_emanuel','Servicio',required=True)
    partner_id = fields.Many2one('res.partner','Asociado',required=True)
    periodo_inicio = fields.Many2one('odoo_emanuel.periodo',required=True)
    monto_total = fields.Float('Monto total',required=True)
    entrega_inicial = fields.Float('Entrega inicial',required=True)
    monto_financiado = fields.Float('Monto financiado', readonly=True)
    cantidad_cuotas = fields.Integer('Cantidad de cuotas',required=True)
    linea_servicio_adquirido_ids = fields.One2many('odoo_emanuel.linea_servicio_adquirido', 'servicio_adquirido_id', 'Cuotas')

    #def _compute_partner_id(self):
       
    #    self.partner_id = self.env.context.get('params').get('id')
        
    def action_generar_lineas_servicio_adquirido(self):
        
        
        self.ensure_one()
        if (self.linea_servicio_adquirido_ids):
            raise UserError('Ya fueron creadas las cuotas.')
        self.monto_financiado = self.monto_total - self.entrega_inicial
        Tasa = self.env['odoo_emanuel.tasa']
        tasa = Tasa.search([])[0]
        tasa_actual = float(tasa.tasa) / float(100)
        periodo_actual = self.periodo_inicio
        balance = self.monto_financiado     
        for i in range(1, self.cantidad_cuotas+1):
            fecha_vencimiento = datetime.date(int(periodo_actual.anio), int(periodo_actual.mes), 10)
            valor_cuota = self.monto_financiado * ( ( (tasa_actual * (1+tasa_actual)**self.cantidad_cuotas) ) / ( ( (1+tasa_actual)**self.cantidad_cuotas)-1) )
            if i == self.cantidad_cuotas:
                interes = balance * (tasa_actual)
                capital = (valor_cuota - interes)
                balance = balance - capital
            else:
                interes = balance * (tasa_actual)
                capital = valor_cuota - interes
                balance = balance - capital           
            cuota = {
                    'servicio_adquirido_id':self.id,
                    'nro_cuota':i,
                    'servicio': self.servicio.id,
                    'periodo': periodo_actual.id,
                    'fecha_vencimiento': fecha_vencimiento,
                    'monto': round(valor_cuota,2),
                    'monto_interes': round(interes,2),
                    'monto_capital': round(capital,2),
                    'saldo':round(valor_cuota,2),
                    #'fecha_pago':,
                    'pagado': False
                    }
            self.env['odoo_emanuel.linea_servicio_adquirido'].create(cuota)            
            periodo_actual = periodo_actual.get_periodo_siguiente()
            
class linea_servicio_adquirido(models.Model):
    _name = 'odoo_emanuel.linea_servicio_adquirido'
    _description = 'Linea servicio adquirido'

    servicio_adquirido_id = fields.Many2one('odoo_emanuel.servicio_adquirido', string="Servicio Adquirido", required=True,readonly=True)
    #account_payment_ids = fields.Many2one('account.payment.group',string='Account payment ids')
    #account_payment_ids = fields.Many2many('account.payment.group','account_payment_linea_cuotas_servicio_adquirido_rel','account_payment_id','linea_cuota_servicio_adquirido_id', compute_sudo=True)
    nro_cuota = fields.Char('Cuota',size=7,readonly=True)
    servicio = fields.Many2one('odoo_emanuel.servicio_emanuel','Servicio',readonly=True)
    periodo = fields.Many2one('odoo_emanuel.periodo',required=True, readonly=True)
    fecha_vencimiento = fields.Date('Fecha de vencimiento',readonly=True)
    monto = fields.Float('Monto',readonly=True)
    monto_interes = fields.Float('Monto interes',readonly=True)
    monto_capital = fields.Float('Monto capital',readonly=True)
    saldo = fields.Float('Saldo',readonly=True)
    fecha_pago = fields.Date('Fecha de pago',readonly=True)
    pagado = fields.Boolean('Esta pago',readonly=True)
    descripcion = fields.Char('Descripcion',readonly=True, compute = '_compute_descripcion')

    def _compute_descripcion(self):
        if not self.servicio.es_servicio_interes:
            self.descripcion = str(self.servicio.name)+": Pago cuota "+str(self.nro_cuota)+" del periodo "+str(self.periodo)

class monto_recibo_cuota(models.Model):
    _name = 'odoo_emanuel.monto_recibo_cuota'
    _description = 'Historico monto recibo cuota'

    linea_servicio_adquirido_id = fields.Many2one('odoo_emanuel.linea_servicio_adquirido',string='Linea servicio adquirido')
    recibo_id = fields.Many2one('account.payment.group',string='Recibo')
    monto = fields.Float('Monto pagado')
    