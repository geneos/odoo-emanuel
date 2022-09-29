from datetime import date
from queue import Empty
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class ReporteCuotaCostoUnicoWizard(models.TransientModel):
    _name = "odoo_emanuel.servicio_emanuel_cuota_costo_unico"
    _description = "Cuota servicio de costo unico"
    
    servicio = fields.Many2one('odoo_emanuel.servicio_emanuel',string='Servicio')
    asociado = fields.Many2one('res.partner','Asociado')
    periodo = fields.Many2one('odoo_emanuel.periodo','Periodo', required=True)

    def generar_asiento_costo_unico(self, partner, monto):
        journal = self.env['account.journal'].search([('code', '=', 'Vario')], limit=1)
        cuenta = self.env['account.account'].search([('code','=','4.1.1.01.020')], limit=1)
        move = self.env['account.move'].create({
            'type': 'entry',
            'date': date.today(),
            'state': 'draft',
            'journal_id': journal.id,
            'line_ids': [
                (0, 0, {
                    'name':'Deuda por servicio costo unico',
                    'account_id': self.servicio.cuenta_contable.id,
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
        move.post()

    def generas_cuotas(self):
    
        periodo = self.periodo
        asociado = self.asociado
        servicio = self.servicio

        # Modelo lineas servicios adquiridos
        lineas_servicios_adquiridos = self.env['odoo_emanuel.linea_servicio_adquirido']

        # si seleccionaron un asociado
        if asociado:
            # si el asociado esta dado de baja da error
            if asociado.baja:
                raise ValidationError('Este asociado esta dado de baja, no se le puede generar la cuota')
            # busco este servicio en los servicios adquiridos del asociado
            servicio = self.env['odoo_emanuel.servicio_adquirido'].search([('servicio','=',self.servicio.id),('partner_id','=',asociado.id)])
            # si no existe el servicio
            if not servicio:
                # lo creo
                servicio_adquirido = self.env['odoo_emanuel.servicio_adquirido']   
                vals = {
                    'servicio' : self.servicio.id,
                    'partner_id' : asociado.id,
                    'periodo_inicio' : periodo.id,
                    'monto_total' : 0,
                    'entrega_inicial' : 0,
                    'monto_financiado' : 0,
                    'cantidad_cuotas' : 1
                }
                servicio = servicio_adquirido.create(vals)
            # me fijo si tiene una cuota creada para este periodo
            cuotas = self.env['odoo_emanuel.linea_servicio_adquirido'].search([('servicio_adquirido_id','=',servicio.id),('periodo','=',periodo.id)])
            if len(cuotas)!=0:
                raise ValidationError('Este asociado ya tiene generada la cuota del periodo seleccionado.')
            # Calculo el numero de cuota
            cuota = len(lineas_servicios_adquiridos.search([('servicio_adquirido_id','=', servicio.id)]))+1
            # Busco el precio del servicio
            precio = self.servicio.costo_unico_servicio.filtered(lambda x: x.periodo_desde.es_menor_igual(periodo) and not x.periodo_hasta.es_menor_igual(periodo)).costo
            if not precio:
                raise ValidationError('Debe especificar el precio del periodo actual para este servicio')
            # Fecha de vencimiento
            periodo_vencimiento = periodo.get_periodo_siguiente()
            fecha_vencimiento = date(int(periodo_vencimiento.anio), int(periodo_vencimiento.mes), 10)
            # Creo la cuota
            cuota = {
                    'servicio_adquirido_id':servicio.id,
                    'nro_cuota': cuota,
                    'servicio': self.servicio.id,
                    'periodo': periodo.id,
                    'fecha_vencimiento': fecha_vencimiento,
                    'monto': precio,
                    'monto_interes': 0,
                    'monto_capital': precio,
                    'saldo':precio,
                    'pagado': False
                    }
            lineas_servicios_adquiridos.create(cuota)
            self.generar_asiento_costo_unico(asociado,precio)
        else: 
            cuotas = self.env['odoo_emanuel.linea_servicio_adquirido'].search([('servicio','=',self.servicio.id),('periodo','=',periodo.id)])
            if len(cuotas)==0:
                # Busco todos los asociados con que no estan dados de baja
                asociados = self.env['res.partner'].search([('baja','=',False)])
                # Por cada asociado
                for a in asociados:
                    # Si el asociado no tiene este servicio creado
                    servicio = a.servicio_adquirido_ids.filtered(lambda x: x.servicio == self.servicio)
                    if not any(servicio):
                        # Lo creo
                        servicio_adquirido = self.env['odoo_emanuel.servicio_adquirido']
                        vals = {
                            'servicio' : self.servicio.id,
                            'partner_id' : a.id,
                            'periodo_inicio' : periodo.id,
                            'monto_total' : 0,
                            'entrega_inicial' : 0,
                            'monto_financiado' : 0,
                            'cantidad_cuotas' : 1
                        }
                        servicio = servicio_adquirido.create(vals)
                    # Calculo el numero de cuota
                    cuota = len(lineas_servicios_adquiridos.search([('servicio_adquirido_id','=', servicio.id)]))+1
                    # Busco el precio del servicio
                    precio = self.servicio.costo_unico_servicio.filtered(lambda x: x.periodo_desde.es_menor_igual(periodo) and not x.periodo_hasta.es_menor_igual(periodo)).costo
                    if not precio:
                        raise ValidationError('Debe especificar el precio del periodo actual para este servicio')
                    # Fecha de vencimiento
                    periodo_vencimiento = periodo.get_periodo_siguiente()
                    fecha_vencimiento = date(int(periodo_vencimiento.anio), int(periodo_vencimiento.mes), 10)
                    # Creo la cuota
                    cuota = {
                            'servicio_adquirido_id':servicio.id,
                            'nro_cuota': cuota,
                            'servicio': self.servicio.id,
                            'periodo': periodo.id,
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
                raise ValidationError('Las cuotas de este periodo ya fueron generadas')