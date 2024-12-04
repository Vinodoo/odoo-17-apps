from collections import defaultdict

from odoo import _, api, fields, tools, models
from odoo.exceptions import UserError, ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    vendor_barcode = fields.Char(string='Barcode')

    def _prepare_new_lot_vals(self):
        self.ensure_one()
        return {
            'name': self.lot_name,
            'product_id': self.product_id.id,
            'company_id': self.company_id.id,
            'vendor_barcode': self.vendor_barcode,
        }


class StockLot(models.Model):
    _inherit = 'stock.lot'

    vendor_barcode = fields.Char(string='Barcode')


class ProductLabelLayout(models.TransientModel):
    _inherit = 'lot.label.layout'

    def process(self):
        self.ensure_one()
        xml_id = 'vn_vendor_barcode.action_report_vn_lot_label_inherit'
        if self.print_format == 'zpl':
            xml_id = 'stock.label_lot_template'
        if self.label_quantity == 'lots':
            docids = self.move_line_ids.lot_id.ids
        else:
            uom_categ_unit = self.env.ref('uom.product_uom_categ_unit')
            quantity_by_lot = defaultdict(int)
            for move_line in self.move_line_ids:
                if not move_line.lot_id:
                    continue
                if move_line.product_uom_id.category_id == uom_categ_unit:
                    quantity_by_lot[move_line.lot_id.id] += int(move_line.quantity)
                else:
                    quantity_by_lot[move_line.lot_id.id] += 1
            docids = []
            for lot_id, qty in quantity_by_lot.items():
                docids.append([lot_id] * qty)
        report_action = self.env.ref(xml_id).report_action(docids, config=False)
        report_action.update({'close_on_report_download': True})
        return report_action
