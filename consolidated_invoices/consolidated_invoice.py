# -*- coding: utf-8 -*-
from openerp.osv import fields, osv, orm


class consolidated_invoice(osv.osv):

    _name = 'account.consolidated.invoice'
    #_inherit = []
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
