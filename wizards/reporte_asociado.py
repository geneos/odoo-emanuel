from datetime import date
from queue import Empty
from odoo import api, fields, models, _
from odoo.exceptions import UserError


tipos=[
        ('1','Cuotas impagas vencidas'),
        ('2','Cuotas impagas por vencer'),
        ('3','Cuotas pagas'),
    ]

class ReporteServicioWizard(models.TransientModel):
    _name = "odoo_emanuel.reporte_asociado"
    _description = "Reporte de asociado"
    
    asociado =fields.Many2one('res.partner','Asociado', required=True)
    servicio=fields.Many2many('odoo_emanuel.servicio_emanuel',string='Servicio')
    tipo = fields.Selection(tipos)

    def imprimir_reporte(self):
        asociado = self.asociado
        # obtengo los servicios adquiridos del asociado que aparecen en la lista de
        # servicios elegidos

        if self.servicio:
            servicios_adquiridos = asociado.servicio_adquirido_ids.search([('servicio.id','in',[self.servicio.id])])
        else:
            servicios_adquiridos = asociado.servicio_adquirido_ids

        # informacion a imprimir
        docs = []
        total = 0
        # por cada servicio
        for s in servicios_adquiridos:
            # por cada cuota
            if self.tipo == '1':    
                titulo = "Informe de cuotas impagas vencidas"
                columna = "Fecha vencimiento"
                lista = s.linea_servicio_adquirido_ids.filtered(lambda x: not x.pagado and x.fecha_vencimiento < date.today()).sorted(key=lambda x: x.fecha_vencimiento)
            elif self.tipo == '2':
                titulo = "Informe de cuotas impagas por vencer"
                columna = "Fecha vencimiento"
                lista = s.linea_servicio_adquirido_ids.filtered(lambda x: not x.pagado and x.fecha_vencimiento > date.today()).sorted(key=lambda x: x.fecha_vencimiento)
            else:
                titulo = "Informe de cuotas pagas"
                columna = "Fecha de pago"
                lista = s.linea_servicio_adquirido_ids.filtered(lambda x: x.pagado).sorted(key=lambda x: x.fecha_pago)
            for c in lista:
                if self.tipo == '3':
                    docs.append({
                        'periodo': c.periodo.periodo_name,
                        'servicio': s.servicio.name,
                        'fecha': c.fecha_pago.strftime("%d/%m/%Y"),
                        'saldo': round(c.saldo,2),
                    })
                else:
                    docs.append({
                        'periodo': c.periodo.periodo_name,
                        'servicio': s.servicio.name,
                        'fecha': c.fecha_vencimiento.strftime("%d/%m/%Y"),
                        'saldo': round(c.saldo,2),
                    })
                total+=c.saldo

        data = {
            'titulo':titulo,
            'columna': columna,
            'nombre': asociado.name,
            'direccion': asociado.street,
            'cond_iva': asociado.l10n_ar_afip_responsibility_type_id.name,
            'cuit': asociado.vat,
            'docs':docs,
            'total':round(total,2)
        }
        return self.env.ref('odoo_emanuel.servicios_asociado').report_action(self, data=data)
