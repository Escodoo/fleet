# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicle(models.Model):

    _inherit = "fleet.vehicle"

    agreement_ids = fields.Many2many(
        comodel_name="agreement",
        relation="fleet_vehicle_agreement_rel",
        column1="vehicle_id",
        column2="agreement_id",
        string="Agreements",
        domain=[],
        context={},
        help="Agreements",
        copy=False,
    )

    agreement_id = fields.Many2one(
        string="Agreement",
        comodel_name="agreement",
        compute="_compute_agreement_id",
        compute_sudo=True,
    )

    def _compute_agreement_id(self):
        agreement_id = self.env['agreement']
        for rec in self:
            stock_move_lines = self.env['stock.move.line'].search([
                ('state', '=', 'done'),
                ('picking_id.picking_type_code', '=', 'outgoing'),
                ('product_id', '=', rec.product_id.id),
                ('lot_id', '=', rec.lot_id.id)
            ])
            for stock_move_line in stock_move_lines:
                agreement = stock_move_line.picking_id.sale_id.agreement_id
                if agreement.end_date and agreement.end_date >= fields.Datetime.now() or not agreement.end_date:
                    agreement_id = agreement
            if agreement_id:
                rec.agreement_id = agreement_id[0]
