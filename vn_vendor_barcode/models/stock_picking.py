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
from odoo import api, fields, models, _


class StockPicking(models.Model):
    """Inherit stock_picking to add barcode field"""
    _inherit = 'stock.picking'

    vendor_barcode = fields.Char(string='Barcode', help="Barcode for Scanning Product")

    @api.onchange('vendor_barcode')
    def _onchange_barcode(self):
        """Function to add Quantity when entering a Barcode."""
        match = False
        if self.vendor_barcode and self.move_ids_without_package:
            lot_ids = self.env['stock.lot'].search(
                [('vendor_barcode', '=', self.vendor_barcode),
                 ('product_id', 'in', self.move_ids_without_package.product_id.ids)
                 ], limit=1)
            if not lot_ids:
                warning_mess = {
                    'title': _('Warning !'),
                    'message': _('No Lot available for this Barcode to Line Products! barcode= ' + self.vendor_barcode)
                }
                self.vendor_barcode = None
                return {'warning': warning_mess}

            bc_lot_id = self.env['stock.lot'].search(
                [('vendor_barcode', '=', self.vendor_barcode),
                 ], limit=1)
            move_ids = self.env['stock.move'].search(
                [('picking_id', '=', self.id.origin),
                 ('product_id', '=', bc_lot_id.product_id.id)
                 ], limit=1)

            for line in move_ids:
                lot_id = self.env['stock.lot'].search(
                    [('vendor_barcode', '=', self.vendor_barcode),
                     ('product_id', '=', line.product_id.id)
                     ], limit=1)
                if not lot_id:
                    warning_mess = {
                        'title': _('Warning !'),
                        'message': _('No Lot available for this Barcode! barcode= ' + self.vendor_barcode)
                    }
                    self.vendor_barcode = None
                    return {'warning': warning_mess}

                if lot_id.product_qty <= 0:
                    warning_mess = {
                        'title': _('Warning !'),
                        'message': _('No stock for this Lot! barcode= ' + self.vendor_barcode)
                    }
                    self.vendor_barcode = None
                    return {'warning': warning_mess}
                if self.vendor_barcode and not lot_id:
                    warning_mess = {
                        'title': _('Warning !'),
                        'message': _('No product is available for this barcode = ' )
                    }
                    self.vendor_barcode = None
                    return {'warning': warning_mess}

                if lot_id.vendor_barcode == self.vendor_barcode:
                    demand_qty = line.product_uom_qty
                    move_line_qty = sum(line.move_line_ids.filtered(lambda m: m.move_id != line.ids[0]).mapped('quantity'))

                    if demand_qty <= move_line_qty:
                        warning_mess = {
                            'title': _('Warning !'),
                            'message': _('Demand quantity already achieved!')
                        }
                        self.vendor_barcode = None
                        return {'warning': warning_mess}

                    if self.vendor_barcode and not lot_id:
                        warning_mess = {
                            'title': _('Warning !'),
                            'message': _('No product is available for this barcode' )
                        }
                        self.vendor_barcode = None
                        return {'warning': warning_mess}
                    move_line_vals_list = []
                    # line.quantity += 1
                    match = True

                    existing_line_id = self.env['stock.move.line'].search(
                        [('lot_id', '=', lot_id.id),
                         ('move_id', '=', line.ids[0])])

                    if existing_line_id:
                        existing_line_id.quantity = (existing_line_id.quantity + 1)
                        self.vendor_barcode = None
                    else:
                        move_line_vals = {
                            'lot_id': lot_id.id,
                            'lot_name': lot_id.name,
                            'owner_id': self.owner_id.id,
                            'move_id': line.ids[0],
                            'product_id': line.product_id.id,
                            'product_uom_id': line.product_uom.id,
                            'location_id': line.location_id.id,
                            'location_dest_id': line.location_dest_id.id,
                            'picking_id': line.picking_id.id,
                            'company_id': line.company_id.id,
                            'quantity': 1,
                            'vendor_barcode': self.vendor_barcode
                        }
                        move_line_vals_list.append(move_line_vals)
                        self.env['stock.move.line'].create(move_line_vals_list)
                        self.vendor_barcode = None

        if self.vendor_barcode and not match:
            warning_mess = {
                    'title': _('Warning !'),
                    'message': _('This product is not available in the order.'
                                 'You can add this product by clicking the'
                                 ' "Add an item" and scan')
                }
            self.vendor_barcode = None
            return {'warning': warning_mess}
