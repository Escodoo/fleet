# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class FleetVehicleInspection(models.Model):

    _inherit = 'fleet.vehicle.inspection'

    repair_product_ids = fields.One2many(
        'fleet.vehicle.inspection.repair.line',
        'inspection_id',
        string='Inspection Repair Products',
        readonly=True,
    )
    amount_total = fields.Float('Total', compute='_amount_total', store=True)

    repair_order_count = fields.Integer(
        compute='_compute_repair_order_count',
        string='# Service Orders'
    )

    ## TODO: implementar controle que permite a criação de mais de uma ordem de reparo desde que todas estejam canceladas
    # create_repair_order_visibility = fields.Boolean(
    #     compute='_compute_create_repair_order_visibility'
    # )
    #
    # @api.depends('create_repair_order_visibility')
    # def _compute_create_repair_order_visibility(self):
    #     for record in self:
    #         record.create_invoice_visibility = lambda any(
    #             record.repair_ids.mapped(
    #                 'create_invoice_visibility'
    #             )
    #         )

    @api.multi
    def _compute_repair_order_count(self):
        for record in self:
            record.repair_order_count = self.env['repair.order'].search_count(
                [('fleet_vehicle_inspection_id', '=', record.id)])

    @api.one
    @api.depends('repair_product_ids.price_subtotal', 'repair_product_ids.product_id')
    def _amount_total(self):
        total = sum(repair_product_id.price_subtotal for repair_product_id in self.repair_product_ids)
        self.amount_total = total

    def action_create_repair_order(self):
        repair_orders = self.env['repair.order']
        for record in self:
            repair_order = record.env['repair.order'].create({
                'fleet_vehicle_inspection_id': record.id,
                'name': record.name or '',
                'product_id': record.vehicle_id.product_id.id or False,
                'product_uom': record.vehicle_id.product_id.uom_id.id or False,

                # TODO: Implementar no módulo fleet_stock
                'location_id': record.vehicle_id.current_stock_location_id.id or False,

                'lot_id': record.vehicle_id.lot_id.id or '',
                'product_qty': 1,
                'invoice_method': 'none',
                'partner_id':
                    record.driver_id.id or False,
            })

            for product in record.repair_product_ids:
                if product.type == 'service':
                    product.env['repair.fee'].create({
                        'repair_id': repair_order.id,
                        'product_id': product.product_id.id,
                        'name': product.product_id.name,
                        'product_uom_qty': product.product_uom_qty,
                        'product_uom': product.product_uom.id,
                        'price_unit': product.price_unit,
                    })

                elif product.type in ['consu', 'stock']:
                    args = repair_order.company_id and [('company_id', '=', repair_order.company_id.id)] or []
                    warehouse = product.env['stock.warehouse'].search(args, limit=1)
                    location_id = warehouse.lot_stock_id.id
                    location_dest_id = product.env['stock.location'].search([('usage', '=', 'production')],
                                                                              limit=1).id
                    product.env['repair.line'].create({
                        'repair_id': repair_order.id,
                        'type' : 'add',
                        'product_id': product.product_id.id,
                        'name': product.product_id.name,
                        'product_uom_qty': product.product_uom_qty,
                        'product_uom': product.product_uom.id,
                        'price_unit': product.price_unit,
                        'location_id': location_id,
                        'location_dest_id': location_dest_id,
                    })
                else:
                    pass

                record.repair_id = repair_order.id
            repair_orders |= repair_order

        return repair_orders

    @api.multi
    def action_view_repair_order(self):
        for record in self:
            repair_ids = self.env['repair.order'].search(
                [('fleet_vehicle_inspection_id', '=', record.id)])
            action = self.env.ref(
                'repair.action_repair_order_tree').read()[0]
            if len(repair_ids) == 1:
                action['views'] = [(
                    self.env.ref('repair.view_repair_order_form').id,
                    'form')]
                action['res_id'] = repair_ids.ids[0]
            else:
                action['domain'] = [('id', 'in', repair_ids.ids)]
            return action
