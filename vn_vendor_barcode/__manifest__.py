# -*- coding: utf-8 -*-
{
    'name': 'Scan Vendor Barcode',
    'version': '17.0',
    'category': 'Inventory',
    "price": 38,
    'currency': 'EUR',
    'sequence': 10,
    'summary': 'Store and Scan Vendor Barcode for receipts and deliveries.'
               ' System automatically select Lot based on Barcode',
    'author': "DooGooD",
    'website': "https://www.doogood.in/",
    'depends': ['base','purchase','stock'],
    'data': [
            'report/stock_vn_report_views.xml',
            'report/report_vn_lot_barcode.xml',
            'views/stock_move_views.xml',
            'views/stock_picking_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False
}