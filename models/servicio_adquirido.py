# -*- coding: utf-8 -*-

import datetime
from email.policy import default
import string
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date

class servicio_adquirido(models.Model):
    _name = 'odoo_emanuel.servicio_adquirido'
    _description = 'Servicio adquirido'

    servicio = fields.Many2one('odoo_emanuel.servicio_emanuel','Servicio',required=True)
    #es_servicio_costo_unico = fields.Boolean('Costo unico')
    partner_id = fields.Many2one('res.partner','Asociado',required=True)
    periodo_inicio = fields.Many2one('odoo_emanuel.periodo',required=True)
    monto_total = fields.Float('Monto total',required=True, digits=(16, 2))
    entrega_inicial = fields.Float('Entrega inicial',required=True, digits=(16, 2))
    monto_financiado = fields.Float('Monto financiado', readonly=True, digits=(16, 2))
    cantidad_cuotas = fields.Integer('Cantidad de cuotas',required=True)
    linea_servicio_adquirido_ids = fields.One2many('odoo_emanuel.linea_servicio_adquirido', 'servicio_adquirido_id', 'Cuotas', ondelete='cascade')
    
    # @api.onchange('servicio')
    # def _onchange_servicio(self):
    #     for record in self:
    #         record.es_servicio_costo_unico = record.servicio.es_servicio_costo_unico

    def cancelar_servicio(self, monto):
        journal = self.env['account.journal'].search([('code', '=', 'Vario')], limit=1)
        cuenta = self.env['account.account'].search([('code','=','4.1.1.01.020')], limit=1)
        #cuenta_servicio = self.env['account.account'].search([('code','=','1.1.3.01.010')], limit=1)
        move = self.env['account.move'].create({
            'type': 'entry',
            'date': date.today(),
            'state': 'draft',
            'journal_id': journal.id,
            'line_ids': [
                (0, 0, {
                    'name':'Deuda por servicio',
                    'account_id': self.servicio.cuenta_contable.id, #cuenta_servicio.id, 
                    'partner_id': self.partner_id.id,
                    'debit': 0.0,
                    'credit': monto,
                    'journal_id': journal.id, 
                }),
                (0, 0, {
                    'name':'Venta por servicio',
                    'account_id': cuenta.id,
                    'partner_id': self.partner_id.id,
                    'debit': monto,
                    'credit': 0.0,
                    'journal_id': journal.id,
                }),
            ],
        })
        move.post()

    def action_cancelar_servicio(self):

        impago_cuotas = 0
        impago_interes = 0

        # CANCELO LAS LINEAS DEL SERVICIO ADQUIRIDO

        for l in self.linea_servicio_adquirido_ids:
            if not l.pagado:
                # Solo cancelamos las imapaga
                l.cancelado = True
                impago_cuotas += l.saldo

        # CANCELO LAS CUOTAS DE INTERES

        # Busco todos los recibos que tiene el servicio adquirido en alguna de sus lineas
        recibos = self.env['account.payment.group'].search([('linea_cuota_servicio_adquirido_ids.servicio_adquirido_id','=',self.id)])
        # Busco todos los recibo_cuota que se crearon a partir de los recibos anteriores
        recibo_cuota = self.env['odoo_emanuel.recibo_cuota'].search([('recibo_id','in',[recibos.id])])
        # Por cada recibo_cuota busco la cuota de interes
        interes = self.env['odoo_emanuel.linea_servicio_adquirido']
        for r in recibo_cuota:
            i = interes.search([('id','=',r.linea_servicio_adquirido_id.id)])
            if not i.pagado:
                i.cancelado = True
                impago_interes += i.saldo

        monto = impago_interes+impago_cuotas
        self.cancelar_servicio(monto)

    def generar_asiento(self):
        journal = self.env['account.journal'].search([('code', '=', 'Vario')], limit=1)
        cuenta = self.env['account.account'].search([('code','=','4.1.1.01.020')], limit=1)
        #cuenta_servicio = self.env['account.account'].search([('code','=','1.1.3.01.010')], limit=1)
        move = self.env['account.move'].create({
            'type': 'entry',
            'date': date.today(),
            'state': 'draft',
            'journal_id': journal.id,
            'line_ids': [
                (0, 0, {
                    'name':'Deuda por servicio',
                    'account_id': self.servicio.cuenta_contable.id, #cuenta_servicio.id, 
                    'partner_id': self.partner_id.id,
                    'debit': self.monto_financiado,
                    'credit': 0.0,
                    'journal_id': journal.id, 
                }),
                (0, 0, {
                    'name':'Venta por servicio',
                    'account_id': cuenta.id,
                    'partner_id': self.partner_id.id,
                    'debit': 0.0,
                    'credit': self.monto_financiado,
                    'journal_id': journal.id,
                }),
            ],
        })
        move.post()

    def action_generar_lineas_servicio_adquirido(self):       
        self.ensure_one()
        if (self.linea_servicio_adquirido_ids):
            raise UserError('Ya fueron creadas las cuotas.')
        self.monto_financiado = self.monto_total - self.entrega_inicial
        Tasa = self.env['odoo_emanuel.tasa_venta']
        tasa = Tasa.search([])[0]
        if (float(tasa.tasa) == 0):
            raise UserError('La tasa de venta no puede ser 0.')
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
                    'monto': valor_cuota,
                    'monto_interes': interes,
                    'monto_capital': capital,
                    'saldo':valor_cuota,
                    'pagado': False
                    }
            self.env['odoo_emanuel.linea_servicio_adquirido'].create(cuota)            
            periodo_actual = periodo_actual.get_periodo_siguiente()
        self.monto_financiado = valor_cuota*self.cantidad_cuotas
        if not self.servicio.es_servicio_costo_unico:
            self.generar_asiento()

    def write(self,values):
        override_write = super(servicio_adquirido,self).write(values)
        
        return override_write
        
class linea_servicio_adquirido(models.Model):
    _name = 'odoo_emanuel.linea_servicio_adquirido'
    _description = 'Linea servicio adquirido'

    servicio_adquirido_id = fields.Many2one('odoo_emanuel.servicio_adquirido', string="Servicio Adquirido", required=True,readonly=True)
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
    cancelado = fields.Boolean('Cancelado',readonly=True,default=False)
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

class recibo_cuota(models.Model):
    _name = 'odoo_emanuel.recibo_cuota'
    _description = 'Historico recibo cuota'

    linea_servicio_adquirido_id = fields.Many2one('odoo_emanuel.linea_servicio_adquirido',string='Linea servicio adquirido')
    recibo_id = fields.Many2one('account.payment.group',string='Recibo')