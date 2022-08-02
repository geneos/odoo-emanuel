from odoo import api, fields, models

class ReporteAsociado(models.AbstractModel):
    _name = 'report.odoo_emanuel.servicios_asociado_template'
    
    @api.model
    def _get_report_values(self,docids, data=None): 
        return{
            'data': data,
        }