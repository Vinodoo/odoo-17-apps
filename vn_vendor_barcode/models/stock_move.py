# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import api, fields, models


class StockPickingOperation(models.Model):
    """Inherit stock_move to add barcode field"""
    _inherit = 'stock.move'

    vendor_barcode = fields.Char(string='Barcode', help="Barcode for Scanning Lot")

    def _action_assign(self, force_qty=False):
        super(StockPickingOperation, self)._action_assign()
        self.with_context(prefetch_fields=False).mapped('move_line_ids').unlink()

    @api.onchange('vendor_barcode')
    def _onchange_barcode_scan(self):
        """Function to add product in line when entering a Barcode."""
        if self.vendor_barcode:
            lot = self.env['stock.lot'].search(
                [('vendor_barcode', '=', self.vendor_barcode)])
            self.product_id = lot.product_id.id

    @api.onchange('product_id')
    def _onchange_product(self):
        """Function to add barcode in line when choosing a Product."""
        if self.product_id.barcode:
            self.write({'vendor_barcode': self.product_id.barcode})
