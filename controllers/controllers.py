# -*- coding: utf-8 -*-
# from odoo import http


# class Odoo-emanuel(http.Controller):
#     @http.route('/odoo-emanuel/odoo-emanuel/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo-emanuel/odoo-emanuel/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo-emanuel.listing', {
#             'root': '/odoo-emanuel/odoo-emanuel',
#             'objects': http.request.env['odoo-emanuel.odoo-emanuel'].search([]),
#         })

#     @http.route('/odoo-emanuel/odoo-emanuel/objects/<model("odoo-emanuel.odoo-emanuel"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo-emanuel.object', {
#             'object': obj
#         })
