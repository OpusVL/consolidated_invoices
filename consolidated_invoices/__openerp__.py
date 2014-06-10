# -*- coding: utf-8 -*-

{
    'name': 'Consolidated Invoices',
    'version': '0.01',
    'category': 'Invoices',
    'description': """
    This module allows invoices to be consolidated.
    """,
    'author': 'OpusVL',
    'website': 'http://www.opusvl.com',
    'depends': ['sale', 'purchase', 'account_payment', 'account_accountant'],
    'init_xml': [],
    'update_xml': [
        'security/ir.model.access.csv',
        'consolidated_invoice_view.xml'
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
