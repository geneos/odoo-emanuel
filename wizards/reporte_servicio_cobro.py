from queue import Empty
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReporteServicioWizard(models.TransientModel):
    _name = "odoo_emanuel.reporte_servicio_cobro"
    _description = "Reporte de servicio corbrados"
    
    servicio=fields.Many2one('odoo_emanuel.servicio_emanuel',string='Servicio')
    fecha_desde = fields.Date('Fecha desde', required=True)
    fecha_hasta = fields.Date('Fecha hasta', required=True)

    def imprimir_reporte(self):
        recibos=self.env['account.payment.group']
        if not self.servicio.id:
            domain=[
                 ('payment_date','>=',self.fecha_desde),
                 ('payment_date','<=',self.fecha_hasta),
                 ('state','=','posted'),
                ]
        else:
            domain=[
                 ('payment_date','>',self.fecha_desde),
                 ('payment_date','<=',self.fecha_hasta),
                 ('state','=','posted'),
                 ('linea_cuota_servicio_adquirido_ids.servicio.id','=',self.servicio.id),
                ]
        campos=[
                'payment_date',
                'linea_cuota_servicio_adquirido_ids',
                'id',
                'partner_id',
                'name'
                ]
        recibos_filtrados = recibos.search_read(domain,campos, order='payment_date')

        total=0
        docs=[]

        monto_rebibo_cuota = self.env['odoo_emanuel.monto_recibo_cuota']
        linea = self.env['odoo_emanuel.linea_servicio_adquirido']

        campos=[
                'monto',
                ]

        for r in recibos_filtrados:
            for l in r['linea_cuota_servicio_adquirido_ids']:
                linea_cuota = linea.search([('id','=',l)])
                if linea_cuota.cancelado == False:
                    if ((self.servicio.id and linea_cuota.servicio.id == self.servicio.id) or (not self.servicio.id)):
                        domain=[
                        ('linea_servicio_adquirido_id','=',l),
                        ('recibo_id','=',r['id']),
                        ]
                        monto = monto_rebibo_cuota.search_read(domain,campos)
                        if not monto:
                            monto = 0
                        else:
                            monto=monto[0]['monto']   
                        docs.append({
                            'asociado':r['partner_id'][1],
                            'servicio': linea.search([('id','=',l)]).servicio.name,
                            'cuota': linea.search([('id','=',l)]).periodo.periodo_name,
                            'fecha': r['payment_date'].strftime("%d/%m/%Y"),
                            'monto': round(monto,2)
                        })
                        total+=monto

        data = {
            'docs':docs,
            'total': round(total,2),
        }

        return self.env.ref('odoo_emanuel.servicios_cobro').report_action(self, data=data)

