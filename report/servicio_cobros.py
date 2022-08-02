from odoo import api, fields, models

class ReporteCobrosDeudas(models.AbstractModel):
    _name = 'report.odoo_emanuel.servicios_cobro_template'
    
    @api.model
    def _get_report_values(self,docids, data=None):
        #return self.env.ref('odoo_emanuel.servicios_vencer_vencido').report_action(self, data=data)
        
        return{
            'data': data,
        }