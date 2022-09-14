# -*- coding: utf-8 -*-

from dataclasses import field
from email.policy import default
from datetime import date
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class servicio_emanuel(models.Model):
    _name = 'odoo_emanuel.servicio_emanuel'
    _description = 'Servicios Emanuel'
    _rec_name = 'name'

    name = fields.Char("Nombre del Servicio", required=True)
    es_servicio_interes = fields.Boolean('Es Servicio de Interés', default=False)
    es_servicio_costo_unico = fields.Boolean('Es Servicio de Costo Unico', default=False)
    costo_unico_servicio = fields.One2many('odoo_emanuel.linea_costo_unico', 'servicio_emanuel_id', 'Costo historico')
    activo = fields.Boolean('Activo', default=True)
    cuenta_contable = fields.Many2one('account.account', 'Cuenta contable', required=True)
    
    def generar_asiento_costo_unico(self, partner, monto):
        journal = self.env['account.journal'].search([('code', '=', 'Vario')], limit=1)
        cuenta = self.env['account.account'].search([('code','=','4.1.1.01.020')], limit=1)
        #cuenta_servicio = self.env['account.account'].search([('code','=','1.1.3.01.010')], limit=1)
        move = self.env['account.move'].create({
            'type': 'entry',
            'date': date.today(),
            'state': 'draft',     # DESPUES VA A SER PUBLICADO
            'journal_id': journal.id,
            'line_ids': [
                (0, 0, {
                    'name':'Deuda por servicio costo unico',
                    'account_id': self.cuenta_contable.id, #cuenta_servicio.id, 
                    'partner_id': partner.id,
                    'debit': monto,
                    'credit': 0.0,
                    'journal_id': journal.id, 
                }),
                (0, 0, {
                    'name':'Venta por servicio',
                    'account_id': cuenta.id,
                    'partner_id': partner.id,
                    'debit': 0.0,
                    'credit': monto,
                    'journal_id': journal.id,
                }),
            ],
        })


    def generas_cuotas(self):
        mes = date.today().month
        if mes < 10:
            mes = str(0)+str(mes)
        periodo_actual = self.env['odoo_emanuel.periodo'].search([('mes','=',mes),('anio','=',date.today().year)])[0]
        cuotas = self.env['odoo_emanuel.linea_servicio_adquirido'].search([('servicio','=',self.id),('periodo','=',periodo_actual.id)])
        if len(cuotas)==0:
            # Busco todos los asociados con servicios adquiridos
            asociados = self.env['res.partner'].search([('servicio_adquirido_ids','!=',False)])
            # Modelo lineas servicios adquiridos
            lineas_servicios_adquiridos = self.env['odoo_emanuel.linea_servicio_adquirido']
            # Por cada asociado
            for a in asociados:
                for s in a.servicio_adquirido_ids:
                    activo = any(s.linea_servicio_adquirido_ids.filtered(lambda x: not x.pagado))
                if activo:
                    # Si el asociado no tiene este servicio creado
                    servicio = a.servicio_adquirido_ids.filtered(lambda x: x.servicio == self.id)
                    if not any(servicio):
                        # Lo creo
                        servicio_adquirido = self.env['odoo_emanuel.servicio_adquirido']
                        vals = {
                            'servicio' : self.id,
                            'partner_id' : a.id,
                            'periodo_inicio' : periodo_actual.id,
                            'monto_total' : 0,
                            'entrega_inicial' : 0,
                            'monto_financiado' : 0,
                            'cantidad_cuotas' : 1
                        }
                        servicio = servicio_adquirido.create(vals)
                    # Calculo el numero de cuota
                    cuota = len(lineas_servicios_adquiridos.search([('servicio_adquirido_id','=', servicio.id)]))+1
                    # Busco el precio del servicio
                    precio = self.costo_unico_servicio.filtered(lambda x: x.periodo_desde.es_menor_igual(periodo_actual) and not x.periodo_hasta.es_menor_igual(periodo_actual)).costo
                    if not precio:
                        raise ValidationError('Debe especificar el precio del periodo actual para este servicio')
                    # Fecha de vencimiento
                    periodo_vencimiento = periodo_actual.get_periodo_siguiente()
                    fecha_vencimiento = date(int(periodo_vencimiento.anio), int(periodo_vencimiento.mes), 10)
                    # Creo la cuota
                    cuota = {
                            'servicio_adquirido_id':servicio.id,
                            'nro_cuota': cuota,
                            'servicio': self.id,
                            'periodo': periodo_actual.id,
                            'fecha_vencimiento': fecha_vencimiento,
                            'monto': precio,
                            'monto_interes': 0,
                            'monto_capital': precio,
                            'saldo':precio,
                            'pagado': False
                            }
                    lineas_servicios_adquiridos.create(cuota)
                    self.generar_asiento_costo_unico(a,precio)
        else:
            raise ValidationError('Las cuotas de este mes ya fueron generadas')

class linea_costo_unico(models.Model):
    _name = 'odoo_emanuel.linea_costo_unico'
    _description = 'Linea de Costo Unico'

    servicio_emanuel_id = fields.Many2one('odoo_emanuel.servicio_emanuel', string="Servicio Emanuel", required=True)
    periodo_desde = fields.Many2one('odoo_emanuel.periodo', required=True)
    periodo_hasta = fields.Many2one('odoo_emanuel.periodo', required=True)
    costo = fields.Float('Costo',required=True)
 
    @api.onchange('periodo_desde','periodo_hasta')
    def _check_desde_hasta(self):
        if (self.periodo_desde and self.periodo_hasta):
            if self.periodo_hasta.es_menor_igual(self.periodo_desde):
                periodo_hasta=None
                raise ValidationError('La fecha desde tiene que ser anterior a la fecha hasta.')