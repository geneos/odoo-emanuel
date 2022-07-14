
from traceback import print_tb
from odoo import models, fields, api
from datetime import date, datetime

class account_payment_group (models.Model):
    _inherit = ['account.payment.group']

    es_cobro_servicios = fields.Boolean('Es cobro de servicios', default=True)
    deuda_cuotas_seleccionadas = fields.Float('Deuda cuotas seleccionadas', readonly=True, compute='_compute_deuda_seleccionada')
    #linea_cuota_servicio_adquirido_ids = fields.One2many('odoo_emanuel.linea_servicio_adquirido','account_payment_ids',string = 'Cuota')
    linea_cuota_servicio_adquirido_ids = fields.Many2many('odoo_emanuel.linea_servicio_adquirido')#,'account_payment_linea_cuotas_servicio_adquirido_rel','linea_cuota_servicio_adquirido_id','account_payment_id',string = 'Cuota')
    diferencia_pago = fields.Float('Diferencia de pago', readonly=True, compute='_compute_diferencia_pago')

    @api.depends('linea_cuota_servicio_adquirido_ids')
    def _compute_deuda_seleccionada(self):
        for rec in self:
            rec.deuda_cuotas_seleccionadas = sum(linea.saldo for linea in rec.linea_cuota_servicio_adquirido_ids)
            #for linea in rec.linea_cuota_servicio_adquirido_ids:#._origin:
            #    rec.deuda_cuotas_seleccionadas += linea.saldo

    @api.depends('payments_amount','deuda_cuotas_seleccionadas')
    def _compute_diferencia_pago(self):
        for rec in self:
            rec.diferencia_pago = rec.payments_amount - rec.deuda_cuotas_seleccionadas

    def post(self):  
        res = super(account_payment_group, self).post()
        #res['deuda_cuota_seleccionadas'] = foo
        cuotas = self.linea_cuota_servicio_adquirido_ids
        monto_pagado_residual = self.payments_amount
        tasa_actual = self.env['odoo_emanuel.tasa'].search([])
        for c in cuotas:
            #import pdb
            #pdb.set_trace()
            if (float(c.saldo) <= float(monto_pagado_residual)):
                c.pagado = True
                monto_interes = c.saldo
                c.saldo = 0
                monto_pagado_residual = monto_pagado_residual - c.monto
                c.fecha_pago = date.today()
            else:
                c.saldo = c.saldo-monto_pagado_residual
                monto_interes = monto_pagado_residual
                monto_pagado_residual = 0
            #c.save
            if (self.payment_date > c.fecha_vencimiento) and not (c.servicio.es_servicio_interes):
                
                dias = (self.payment_date - c.fecha_vencimiento).days
                tasa_diaria = tasa_actual.tasa/30
                interes = tasa_diaria*dias*monto_interes
                import pdb
                pdb.set_trace()
                if interes>0:
                    mes = date.today().month
                    if mes < 10:
                        mes = str(0)+str(mes)
                    periodo_actual = self.env['odoo_emanuel.periodo'].search([('mes','=',mes),('anio','=',date.today().year)])[0]
                    periodo_siguiente = periodo_actual.get_periodo_siguiente()
                    servicio_interes = self.env['odoo_emanuel.servicio_emanuel'].search([('es_servicio_interes','=',True)])
                    servicio_interes_partner = self.env['odoo_emanuel.servicio_adquirido'].search([('servicio','=',servicio_interes[0].id),('partner_id','=',self.partner_id.id)])
                    
                    if not servicio_interes_partner:
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
                    linea_servicio_adquirido.create(vals)                   
        return res