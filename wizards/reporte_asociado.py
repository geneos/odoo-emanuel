from datetime import date
from queue import Empty
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReporteServicioWizard(models.TransientModel):
    _name = "odoo_emanuel.reporte_asociado"
    _description = "Reporte de asociado"
    
    asociado =fields.Many2one('res.partner','Asociado', required=True)
    servicio=fields.Many2many('odoo_emanuel.servicio_emanuel',string='Servicio')
    vencido = fields.Boolean('Cuotas impagas vencidas')
    por_vencer = fields.Boolean('Cuotas impagas')
    pagado = fields.Boolean('Cuotas pagas')

    def imprimir_reporte(self):
        asociado = self.asociado
        # obtengo los servicios adquiridos del asociado que aparecen en la lista de
        # servicios elegidos

        if self.servicio:
            fields=[
                 'linea_servicio_adquirido_ids',
               ]
            domain=[('id','in',[self.servicio.id])]
            servicios_adquiridos = asociado.servicio_adquirido_ids.search([('servicio.id','in',[self.servicio.id])])
        else:
            servicios_adquiridos = asociado.servicio_adquirido_ids

        # informacion a imprimir
        docs = []

        # por cada servicio
        for s in servicios_adquiridos:
            # por cada cuota
            for c in s.linea_servicio_adquirido_ids:
                if not c.pagado:
                    if self.vencido:
                        if c.fecha_vencimiento < date.today():

                            docs.append({
                                'cuota': c.nro_cuota,
                                'servicio': s.servicio.name,
                                'saldo': round(c.saldo,2),
                                'estado': 'vencido'
                            })

                        elif self.por_vencer:

                            docs.append({
                                'cuota': c.nro_cuota,
                                'servicio': s.servicio.name,
                                'saldo': round(c.saldo,2),
                                'estado':'a vencer'
                            })

                elif self.pagado:

                    docs.append({
                                'cuota': c.nro_cuota,
                                'servicio': s.servicio.name,
                                'saldo': round(c.saldo,2),
                                'estado': 'pagada'
                            })

        data = {
            'asociado': asociado.name,
            'docs':docs,
        }
        return self.env.ref('odoo_emanuel.servicios_asociado').report_action(self, data=data)
