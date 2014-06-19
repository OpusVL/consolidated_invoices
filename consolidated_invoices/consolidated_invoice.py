# -*- coding: utf-8 -*-
from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp
import re
import time


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

    def _get_journal(self, cr, uid, context=None):
        if context is None:
            context = {}
        type_inv = context.get('type', 'out_invoice')
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_id = context.get('company_id', user.company_id.id)
        type2journal = {'out_invoice': 'sale', 'in_invoice': 'purchase', 'out_refund': 'sale_refund', 'in_refund': 'purchase_refund'}
        journal_obj = self.pool.get('account.journal')
        domain = [('company_id', '=', company_id)]
        if isinstance(type_inv, list):
            domain.append(('type', 'in', [type2journal.get(type) for type in type_inv if type2journal.get(type)]))
        else:
            domain.append(('type', '=', type2journal.get(type_inv, 'sale')))
        res = journal_obj.search(cr, uid, domain, limit=1)
        return res and res[0] or False

    def _get_currency(self, cr, uid, context=None):
        res = False
        journal_id = self._get_journal(cr, uid, context=context)
        if journal_id:
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
            res = journal.currency and journal.currency.id or journal.company_id.currency_id.id
        return res

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for ci in self.browse(cr, uid, ids, context=context):
            res[ci.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0
            }
            for invoice in [l.invoice_id for l in ci.invoice_links]:
                refund = re.match('.*refund$', invoice.type)
                for line in invoice.invoice_line:
                    if refund:
                        res[ci.id]['amount_untaxed'] -= line.price_subtotal
                    else:
                        res[ci.id]['amount_untaxed'] += line.price_subtotal
                for line in invoice.tax_line:
                    if refund:
                        res[ci.id]['amount_tax'] -= line.amount
                    else:
                        res[ci.id]['amount_tax'] += line.amount
                res[ci.id]['amount_total'] = res[ci.id]['amount_tax'] + res[ci.id]['amount_untaxed']
        return res

    _name = 'account.consolidated.invoice'
    _description = 'Consolidated invoice'
    _order = "id desc"
    _columns = {
        'name': fields.char('Reference', size=64, select=True, readonly=True, states={'draft': [('readonly',False)]}),
        'line_text': fields.text('Line Text', required=True),
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
        'partner_id': fields.many2one('res.partner', 'Partner', change_default=True, readonly=True, required=True, states={'draft':[('readonly',False)]}, track_visibility='always'),
        'company_id': fields.many2one('res.company', 'Company', required=True, change_default=True, readonly=True, states={'draft':[('readonly',False)]}),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)]}, track_visibility='always'),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft':[('readonly',False)]}),

        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Subtotal', track_visibility='always',
            store={
                'account.consolidated.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_links'], 20),
                'account.invoice': (_get_invoices, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Tax',
            store={
                'account.consolidated.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_links'], 20),
                'account.invoice': (_get_invoices, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'account.consolidated.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_links'], 20),
                'account.invoice': (_get_invoices, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
    }
    _defaults = {
        'state': 'draft',
        'journal_id': _get_journal,
        'currency_id': _get_currency,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=c),
    }

    # go from canceled state to draft state
    def action_cancel_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        self.delete_workflow(cr, uid, ids)
        self.create_workflow(cr, uid, ids)
        account_inv_obj = self.pool.get('account.invoice')
        inv_ids = account_inv_obj.search(cr, uid, [('state','=','cancel'), ('consolidated_invoice_link.consolidated_invoice_id', 'in', ids)], context=None)
        account_inv_obj.action_cancel_draft(cr, uid, inv_ids, *args)
        return True

    def action_date_assign(self, cr, uid, ids, *args):
        account_inv_obj = self.pool.get('account.invoice')
        inv_ids = account_inv_obj.search(cr, uid, [('consolidated_invoice_link.consolidated_invoice_id', 'in', ids)], context=None)
        account_inv_obj.action_date_assign(cr, uid, inv_ids, *args)
        return True

    def invoice_validate(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'open'}, context=context)
        account_inv_obj = self.pool.get('account.invoice')
        inv_ids = account_inv_obj.search(cr, uid, [('state','=','draft'), ('consolidated_invoice_link.consolidated_invoice_id', 'in', ids)], context=context)
        account_inv_obj.invoice_validate(cr, uid, inv_ids, context=context)
        return True

    def confirm_paid(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state':'paid'}, context=context)
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'cancel'})
        account_inv_obj = self.pool.get('account.invoice')
        inv_ids = account_inv_obj.search(cr, uid, [('consolidated_invoice_link.consolidated_invoice_id', 'in', ids)], context=context)
        account_inv_obj.action_cancel(cr, uid, inv_ids, context=context)
        return True

    def move_line_id_payment_get(self, cr, uid, ids, *args):
        # FIXME: implement this.
        return []

    def test_paid(self, cr, uid, ids, *args):
        # FIXME: implement this.
        return False

    def onchange_journal_id(self, cr, uid, ids, journal_id=False, context=None):
        result = {}
        if journal_id:
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
            currency_id = journal.currency and journal.currency.id or journal.company_id.currency_id.id
            company_id = journal.company_id.id
            result = {'value': {
                    'currency_id': currency_id,
                    'company_id': company_id,
                    }
                }
        return result

    def invoice_print(self, cr, uid, ids, context=None):
        """This function prints the invoice.
        """
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        return self.pool['report'].get_action(cr, uid, ids,
            'consolidated_invoices.report_consolidated_invoice', context=context)

    def create_for_invoices(self, cr, uid, ids, context=None):
        """
        This creates a consolidated invoice for a set of invoices.
        """
        account_pool = self.pool.get('account.invoice')
        invoices = account_pool.browse(cr, uid, ids, context=context)
        journal_id = invoices[0].journal_id.id
        reference = invoices[0].reference or 'REF'
        partner = invoices[0].partner_id
        partner_id = partner.id
        company_id = invoices[0].company_id.id
        currency_id = invoices[0].currency_id.id
        partner_name = partner.name

        new_obj = {
            'line_text': "Consolidated Invoice for %s" % partner_name,
            # /opt/odoo/openerp/osv/orm.py +3794
            'invoice_links': [(0, False, {'invoice_id':i}) for i in ids],
            'reference': reference,
            'state': 'draft',
            'date_invoice': time.strftime('%Y-%m-%d'),
            'currency_id': currency_id,
            'journal_id': journal_id,
            'company_id': company_id,
            'partner_id': partner_id,
        }
        invoice_ids = self.create(cr, uid, new_obj, context=context)
        return invoice_ids

class consolidated_invoice_link(osv.osv):

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for ci in self.browse(cr, uid, ids, context=context):
            res[ci.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0
            }
            invoice = ci.invoice_id
            refund = re.match('.*refund$', invoice.type)
            for line in invoice.invoice_line:
                if refund:
                    res[ci.id]['amount_untaxed'] -= line.price_subtotal
                else:
                    res[ci.id]['amount_untaxed'] += line.price_subtotal
            for line in invoice.tax_line:
                if refund:
                    res[ci.id]['amount_tax'] -= line.amount
                else:
                    res[ci.id]['amount_tax'] += line.amount
            res[ci.id]['amount_total'] = res[ci.id]['amount_tax'] + res[ci.id]['amount_untaxed']
        return res

    def _get_invoices(self, cr, uid, ids, context=None):
        # this function is passed a list of invoices that have changed.  
        # this function then returns the list of consolidated invoices they are
        # on so that they can be recalculated.
        result = {}
        for invoice in self.pool.get('account.invoice').browse(cr, uid, ids, context=context):
            if invoice.consolidated_invoice_link:
                for inv_id in [ i.id for i in invoice.consolidated_invoice_link ]:
                    result[inv_id] = True
        return result.keys()

    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            ci_link = line.invoice_id.consolidated_invoice_link
            if ci_link:
                result[ci_link[0].id] = True
        return result.keys()

    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            ci_link = tax.invoice_id.consolidated_invoice_link
            if ci_link:
                result[ci_link[0].id] = True
        return result.keys()


    _name = 'account.consolidated.invoice.link'
    _description = 'Consolidated invoice'
    _columns = {
        'consolidated_invoice_id': fields.many2one('account.consolidated.invoice', 'Consolidated Invoice Reference', ondelete='cascade', select=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', ondelete='cascade', select=True, required=True),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Invoice Total',
            store={
                'account.consolidated.invoice.link': (lambda self, cr, uid, ids, c={}: ids, ['invoice_id'], 20),
                'account.invoice': (_get_invoices, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
    }


class account_invoice(osv.osv):

    _inherit = "account.invoice"

    _columns = {
        'consolidated_invoice_link': fields.one2many('account.consolidated.invoice.link', 'invoice_id', 'Consolidated Invoice')
    }
