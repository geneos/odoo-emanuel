from dataclasses import fields
from pyexpat import model


class periodo(model.Model):
    _name = 'odoo_emanuel.periodo'
    _description = 'Periodo'
    _rec_name = 'name'

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

    mes = fields.Selection(meses)
    año = fields.Selection(año)