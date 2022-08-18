
from traceback import print_tb
from odoo import models, fields, api
from datetime import date, datetime
from odoo.exceptions import UserError

class account_payment_group (models.Model):
    _inherit = ['account.payment.group']

    es_cobro_servicios = fields.Boolean('Es cobro de servicios', default=True)
    deuda_cuotas_seleccionadas = fields.Float('Deuda cuotas seleccionadas', readonly=True, compute='_compute_deuda_seleccionada')
    linea_cuota_servicio_adquirido_ids = fields.Many2many('odoo_emanuel.linea_servicio_adquirido')#,'account_payment_linea_cuotas_servicio_adquirido_rel','linea_cuota_servicio_adquirido_id','account_payment_id',string = 'Cuota')
    diferencia_pago = fields.Float('Diferencia de pago', readonly=True, compute='_compute_diferencia_pago')
    
    @api.depends('linea_cuota_servicio_adquirido_ids')
    def _compute_deuda_seleccionada(self): 
        for rec in self:
                rec.deuda_cuotas_seleccionadas = sum(linea.saldo for linea in rec.linea_cuota_servicio_adquirido_ids)
        
    @api.depends('payments_amount','deuda_cuotas_seleccionadas')
    def _compute_diferencia_pago(self):
        for rec in self:    
            rec.diferencia_pago = rec.payments_amount - rec.deuda_cuotas_seleccionadas
        
    def post(self):  
        res = super(account_payment_group, self).post()
        if self.es_cobro_servicios:
            cuotas = self.linea_cuota_servicio_adquirido_ids
            monto_pagado_residual = self.payments_amount
            tasa_actual = self.env['odoo_emanuel.tasa'].search([])
            monto_recibo_cuota = self.env['odoo_emanuel.monto_recibo_cuota']
            for c in cuotas:
                if (float(c.saldo) <= float(monto_pagado_residual)):
                    vals = {
                        'linea_servicio_adquirido_id': c.id,
                        'recibo_id': self.id,
                        'monto': c.saldo        
                    }
                    monto_recibo_cuota.create(vals) 
                    c.pagado = True
                    monto_interes = c.saldo
                    c.saldo = 0
                    monto_pagado_residual = monto_pagado_residual - c.monto
                    c.fecha_pago = date.today()
                else:
                    monto_recibo_cuota = self.env['odoo_emanuel.monto_recibo_cuota']
                    vals = {
                        'linea_servicio_adquirido_id': c.id,
                        'recibo_id': self.id,
                        'monto': monto_pagado_residual       
                    }
                    monto_recibo_cuota.create(vals) 
                    c.saldo = c.saldo-monto_pagado_residual
                    monto_interes = monto_pagado_residual
                    monto_pagado_residual = 0
                if (self.payment_date > c.fecha_vencimiento) and not (c.servicio.es_servicio_interes):
                    dias = (self.payment_date - c.fecha_vencimiento).days
                    tasa_diaria = tasa_actual.tasa/30
                    interes = tasa_diaria*dias*monto_interes
                    if interes>0:
                        mes = date.today().month
                        if mes < 10:
                            mes = str(0)+str(mes)
                        periodo_actual = self.env['odoo_emanuel.periodo'].search([('mes','=',mes),('anio','=',date.today().year)])[0]
                        periodo_siguiente = periodo_actual.get_periodo_siguiente()
                        servicio_interes = self.env['odoo_emanuel.servicio_emanuel'].search([('es_servicio_interes','=',True)])                    
                        if not servicio_interes:
                            cuenta_servicio = self.env['account.account'].search([('code','=','1.1.3.01.010')], limit=1)
                            servicio_emanuel = self.env['odoo_emanuel.servicio_emanuel']
                            vals = {
                                'name' : 'Interes',
                                'es_servicio_interes' : True,
                                'es_servicio_costo_unico' : False,
                                'activo' : True,
                                'cuenta_contable' : cuenta_servicio.id,
                            }
                            servicio_interes = servicio_emanuel.create(vals)
                            #Creo servicio
                            servicio_adquirido = self.env['odoo_emanuel.servicio_adquirido']
                            vals = {
                                'servicio' : servicio_interes.id,
                                'partner_id' : self.partner_id.id,
                                'periodo_inicio' : periodo_siguiente.id,
                                'monto_total' : 0,
                                'entrega_inicial' : 0,
                                'monto_financiado' : 0,
                                'cantidad_cuotas' : 1
                            }
                            servicio_interes_partner = servicio_adquirido.create(vals)
                        else:
                            servicio_interes_partner = self.env['odoo_emanuel.servicio_adquirido'].search([('servicio','=',servicio_interes[0].id),('partner_id','=',self.partner_id.id)])
                            if not servicio_interes_partner:
                                servicio_adquirido = self.env['odoo_emanuel.servicio_adquirido']
                                vals = {
                                    'servicio' : servicio_interes.id,
                                    'partner_id' : self.partner_id.id,
                                    'periodo_inicio' : periodo_siguiente.id,
                                    'monto_total' : 0,
                                    'entrega_inicial' : 0,
                                    'monto_financiado' : 0,
                                    'cantidad_cuotas' : 1
                                }
                                servicio_interes_partner = servicio_adquirido.create(vals)
                        #Creo cuotas
                        linea_servicio_adquirido = self.env['odoo_emanuel.linea_servicio_adquirido']
                        vals = {
                            'servicio_adquirido_id' : servicio_interes_partner.id,
                            'nro_cuota' : 1,
                            'servicio' : servicio_interes.id,
                            'periodo' : periodo_siguiente.id,
                            'fecha_vencimiento' : datetime(int(periodo_siguiente.anio), int(periodo_siguiente.mes), 10).date(),
                            'monto' : float(interes),
                            'monto_interes' : 0,
                            'monto_capital' : 0,
                            'saldo' : float(interes),
                            'pagado' : False,
                            'descripcion' : f"Interes por cuota {c.periodo} del servicio {c.servicio.name}"
                        }
                        interes = linea_servicio_adquirido.create(vals)
                        recibo_cuota = self.env['odoo_emanuel.recibo_cuota']
                        vals = {
                            'linea_servicio_adquirido_id': interes.id,
                            'recibo_id': self.id,
                        }
                        recibo_cuota.create(vals)
            if (round(monto_pagado_residual,4)>0):
                raise UserError('Necesita imputar el total, seleccione mas cuotas.')
        return res
  
    def cancelar(self):
        res = super(account_payment_group, self).cancel()
        if self.es_cobro_servicios:
            cuotas = self.linea_cuota_servicio_adquirido_ids
            pagos = self.payment_ids
            # Pasa la linea de pago a cancelado
            for p in pagos:
                p.state = 'cancelled'
            # Pasa el estado del recibo a cancelado
            self.state='cancel'
            monto_pagado_residual = self.diferencia_pago+self.deuda_cuotas_seleccionadas
            linea_servicio_adquirido = self.env['odoo_emanuel.linea_servicio_adquirido']
            cuotas_interes = self.env['odoo_emanuel.recibo_cuota'].search([('recibo_id','=',self.id)])
            for i in cuotas_interes:
                linea_servicio_adquirido.search([('id','=',i.linea_servicio_adquirido_id.id)]).unlink()
                i.unlink() 
            for c in cuotas:
                if (len(cuotas)==1):
                    c.saldo=c.saldo+monto_pagado_residual
                else:
                    monto = self.env['odoo_emanuel.monto_recibo_cuota'].search([('linea_servicio_adquirido_id','=',c.id),('recibo_id','=',self.id)]).monto
                    c.saldo = c.saldo+monto
                c.pagado=False
        return res