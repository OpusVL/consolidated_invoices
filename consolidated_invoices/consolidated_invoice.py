# -*- coding: utf-8 -*-
from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp


class consolidated_invoice(osv.osv):

    def _get_invoices(self, cr, uid, ids, context=None):
        # this function is passed a list of invoices that have changed.  
        # this function then returns the list of consolidated invoices they are
        # on so that they can be recalculated.
        result = {}
        for invoice in self.pool.get('account.invoice').browse(cr, uid, ids, context=context):
            if invoice.consolidated_invoice_link:
                for inv_id in [ i.consolidated_invoice_id.id for i in invoice.consolidated_invoice_link ]:
                    result[inv_id] = True
        return result.keys()

    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            ci_link = line.invoice_id.consolidated_invoice_link
            if ci_link:
                result[ci_link[0].consolidated_invoice_id.id] = True
        return result.keys()

    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            ci_link = tax.invoice_id.consolidated_invoice_link
            if ci_link:
                result[ci_link[0].consolidated_invoice_id.id] = True
        return result.keys()

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for ci in self.browse(cr, uid, ids, context=context):
            res[ci.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0
            }
            for invoice in [l.invoice_id for l in ci.invoice_links]:
                for line in invoice.invoice_line:
                    res[ci.id]['amount_untaxed'] += line.price_subtotal
                for line in invoice.tax_line:
                    res[ci.id]['amount_tax'] += line.amount
                res[ci.id]['amount_total'] = res[ci.id]['amount_tax'] + res[ci.id]['amount_untaxed']
        return res

    _name = 'account.consolidated.invoice'
    _description = 'Consolidated invoice'
    _order = "id desc"
    _columns = {
        'name': fields.char('Reference', size=64, select=True, readonly=True, states={'draft': [('readonly',False)]}),
        'reference': fields.char('Invoice Reference', size=64, help="The partner reference of this invoice."),
        'invoice_links': fields.one2many('account.consolidated.invoice.link', 'consolidated_invoice_id', 'Invoices', readonly=True, states={'draft':[('readonly',False)]}),
        'comment': fields.text('Additional Information'),
        'state': fields.selection([
            ('draft','Draft'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Cancelled'),
            ],'Status', select=True, readonly=True, track_visibility='onchange',
            help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Invoice. \
            \n* The \'Open\' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice. \
            \n* The \'Paid\' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled. \
            \n* The \'Cancelled\' status is used when user cancel invoice.'),
        'date_invoice': fields.date('Invoice Date', readonly=True, states={'draft':[('readonly',False)]}, select=True, help="Keep empty to use the current date"),
        'company_id': fields.many2one('res.company', 'Company', required=True, change_default=True, readonly=True, states={'draft':[('readonly',False)]}),

        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Subtotal', track_visibility='always',
            store={
                'account.invoice': (_get_invoices, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Tax',
            store={
                'account.invoice': (_get_invoices, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'account.invoice': (_get_invoices, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
    }
    _defaults = {
        'state': 'draft',
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=c),
    }

    # go from canceled state to draft state
    def action_cancel_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        self.delete_workflow(cr, uid, ids)
        self.create_workflow(cr, uid, ids)
        return True

    def action_date_assign(self, cr, uid, ids, *args):
        # FIXME: implement this.
        return True

    def invoice_validate(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'open'}, context=context)
        return True

    def confirm_paid(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state':'paid'}, context=context)
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        # FIXME: implement this.
        return True

    def move_line_id_payment_get(self, cr, uid, ids, *args):
        # FIXME: implement this.
        return []

    def test_paid(self, cr, uid, ids, *args):
        # FIXME: implement this.
        return False


class consolidated_invoice_link(osv.osv):
    _name = 'account.consolidated.invoice.link'
    _description = 'Consolidated invoice'
    _columns = {
        'consolidated_invoice_id': fields.many2one('account.consolidated.invoice', 'Consolidated Invoice Reference', select=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', select=True, required=True),
    }


class account_invoice(osv.osv):

    _inherit = "account.invoice"

    _columns = {
        'consolidated_invoice_link': fields.one2many('account.consolidated.invoice.link', 'invoice_id', 'Consolidated Invoice')
    }
