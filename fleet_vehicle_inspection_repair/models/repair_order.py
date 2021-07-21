# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class RepairOrder(models.Model):

    _inherit = 'repair.order'

    fleet_vehicle_inspection_id = fields.Many2one('fleet.vehicle.inspection', string='Fleet Vehicle Inspection')

    # @api.multi
    # def action_view_repair_order(self):
    #     '''
    #     This function returns an action that displays a full Repair Order
    #     form when viewing an Repair Order from a inspection.
    #     '''
    #     action = self.env.ref('repair.action_repair_order_tree').\
    #         read()[0]
    #     repair_order = self.env['repair.order'].search([('id', '=', self.id)])
    #     action['views'] = [(self.env.ref('repair.' +
    #                                      'view_repair_order_form').id, 'form')]
    #     action['res_id'] = repair_order.id
    #     return action
