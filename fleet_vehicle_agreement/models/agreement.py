# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Agreement(models.Model):

    _inherit = "agreement"

    vehicle_ids = fields.Many2many(
        comodel_name="fleet.vehicle",
        relation="fleet_vehicle_agreement_rel",
        column1="agreement_id",
        column2="vehicle_id",
        string="Vehicle",
        domain=[],
        context={},
        help="Vehicles related to this agreement",
        copy=False,
    )

    fleet_vehicle_ids = fields.Many2many(
        'fleet.vehicle', compute='_compute_fleet_vehicle_ids',
        string='Fleet Vehicles associated to this agreement')

    @api.multi
    def _compute_fleet_vehicle_ids(self):
        for rec in self:
            vehicles = self.env['fleet.vehicle']
            pickings = self.env['stock.picking'].search([
                ('state', '=', 'done'),
                ('picking_type_code', '=', 'outgoing'),
                ('sale_id', '=', rec.sale_ids.id)
            ])
            if pickings:
                for picking in pickings:
                    for move_line in picking.move_line_ids:
                        if move_line.lot_id.fleet_vehicle_id:
                            vehicles |= move_line.lot_id.fleet_vehicle_id
            rec.fleet_vehicle_ids = vehicles
