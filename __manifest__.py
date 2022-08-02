# -*- coding: utf-8 -*-
{
    "name": "odoo_emanuel",
    'version': '13.0.1.0.0',
    'category': 'Tools',
    'sequence': 14,
    'author': 'GENEOS',
    'website': 'www.geneos.com.ar',
    'license': 'AGPL-3',
    'summary': '',
    "depends": [
        "base",
        "sale", 
        "sale_management",
    ],
    'external_dependencies': {
    },
    'data': [
        'security/ir.model.access.csv',
        'views/servicio_emanuel_views.xml',
        'views/servicio_adquirido_views.xml',
        'views/account_payment_views.xml',
        'views/res_partner_views.xml',
        'views/templates.xml',
        'views/tasa.xml',
        'views/periodo.xml',
        'report/asociado.xml',
        'wizards/reporte_asociado.xml',
        'report/servicio_cobros.xml',
        'wizards/reporte_servicio_cobro.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}