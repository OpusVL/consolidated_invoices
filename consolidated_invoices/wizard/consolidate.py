# -*- coding: utf-8 -*-

from openerp.osv import orm, fields
from openerp.tools.translate import _


class consolidator(orm.TransientModel):
    _name = "consolidated.invoice.consolidation"
    _description = "Automatic Invoice Consolidation"


    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', change_default=True, readonly=True, required=True),
        'method': fields.selection([
            ('po', 'By Purchase Order Number'),
            ('po_for_selection', 'By Purchase Order Number on selected invoices'),
            ('period', 'By Period'),
            ('po_and_period', 'By Purchase Order Number and Period'),
        ], 'Method', help='Consolidate your invoices by...', required=True), # FIXME: add proper help text.
        'period': fields.selection([
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('endofmonth', 'Monthly - End of month'),
        ], 'Period', help=''),
        'dayofweek': fields.selection([
            ('monday', 'Monday'),
            ('tuesday', 'Tuesday'),
            ('wednesday', 'Wednesday'),
            ('thursday', 'Thursday'),
            ('friday', 'Friday'),
            ('saturday', 'Saturday'),
            ('sunday', 'Sunday'),
        ], 'Day of week', help=''),
        'day': fields.integer('Day of month'),
        'invoices': fields.many2many('account.invoice', string='Invoices'),
    }

    def default_get(self, cr, uid, fields, context=None):
        if not context:
            context = {}
        partner_id = context.get('partner_id', False)
        defaults = super(self.__class__, self).default_get(cr, uid, fields, context=context)
        defaults.update({ 'partner_id': partner_id })
        return defaults

    def consolidate_invoictes(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        result = mod_obj._get_id(cr, uid, 'consolidated_invoices', 'consolidated_invoice_form')
        id = mod_obj.read(cr, uid, result, ['res_id'])
        consolidated_invoice_obj = self.pool.get('account.consolidated.invoice')
        #invoice_id = consolidated_invoice_obj.create_for_invoices(cr, uid, invoice_ids, context=context)
        invoice_id = 1
        return {
            'name': _('Consolidated Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': id['res_id'],
            'res_model': 'account.consolidated.invoice',
            'res_id': invoice_id,
            'target': 'current',
            'type': 'ir.actions.act_window',
        }
