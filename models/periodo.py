from odoo import models, fields, api
from odoo.exceptions import ValidationError

meses=[
        ('01','01'),
        ('02','02'),
        ('03','03'),
        ('04','04'),
        ('05','05'),
        ('06','06'),
        ('07','07'),
        ('08','08'),
        ('09','09'),
        ('10','10'),
        ('11','11'),
        ('12','12'),
    ]

año=[
        ('2010','2010'),
        ('2011','2011'),
        ('2012','2012'),
        ('2013','2013'),
        ('2014','2014'),
        ('2015','2015'),
        ('2016','2016'),
        ('2017','2017'),
        ('2018','2018'),
        ('2019','2019'),
        ('2020','2020'),
        ('2021','2021'),
        ('2022','2022'),
        ('2023','2023'),
        ('2024','2024'),
        ('2025','2025'),
        ('2026','2026'),
        ('2027','2027'),
        ('2028','2028'),
        ('2029','2029'),
        ('2030','2030'),
        ('2031','2031'),
        ('2032','2032'),
        ('2033','2033'),
        ('2034','2034'),
        ('2035','2035'),
        ('2036','2036'),
        ('2037','2037'),
        ('2038','2038'),
        ('2039','2039'),
        ('2040','2040'),
    ]

class periodo(models.Model):
    _name = 'odoo_emanuel.periodo'
    _description = 'Periodo'
    _rec_name = 'periodo_name'

    periodo_name = fields.Char('Nombre', compute='_compute_periodo_name', store=True)
    mes = fields.Selection(meses)
    anio = fields.Selection(año, 'Año')

    @api.depends('mes','anio')
    def _compute_periodo_name(self):
        for periodo in self:
            periodo.periodo_name = '%s / %s' % (periodo.mes, periodo.anio)

    
    def get_periodo_siguiente(self):
        Periodo = self.env['odoo_emanuel.periodo']
        if int(self.mes)<int(12): 
            m_nuevo = int(self.mes)+1
            a_nuevo = int(self.anio)
        else:
            m_nuevo = 1
            a_nuevo = int(self.anio)+1
        if m_nuevo < 10:
            m_nuevo = str(0)+str(m_nuevo)
        periodo = Periodo.search([('mes','=',m_nuevo),('anio','=',a_nuevo)])[0]
        return periodo

    def es_menor_igual(self, hasta):
        print(int(self.mes))
        print(int(hasta.mes))
        if (self.anio < hasta.anio) or ((self.anio == hasta.anio) and (int(self.mes) <= int(hasta.mes))):
            return True
        return False

    @api.constrains('mes','anio')
    def _check_unico(self):
        if self.env['odoo_emanuel.periodo'].search([('anio','=',self.anio),('mes','=',self.mes),('id','!=', self.id)]):
            raise ValidationError('El periodo debe ser unico')