# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 OpusVL. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
from openerp.tools.translate import _


class invoice_merge(orm.TransientModel):
    _name = "consolidated.invoice.selection"
    _description = "Consolidated Invoice Selection"

    def _validate_criteria(self, cr, uid, context):
        if context.get('active_model', '') == 'account.invoice':
            ids = context['active_ids']
            inv_obj = self.pool.get('account.invoice')
            invs = inv_obj.read(cr, uid, ids, ['account_id', 'state', 'type', 'company_id',
                                               'partner_id', 'currency_id', 'journal_id'])
            # FIXME: ensure the invoices aren't on an existing consolidated invoice.
            for d in invs:
                if d['state'] != 'draft':
                    raise orm.except_orm(_('Warning'), _('At least one of the selected invoices is %s!') % d['state'])
                if (d['company_id'] != invs[0]['company_id']):
                    raise orm.except_orm(_('Warning'), _('Not all invoices are at the same company!'))
                if (d['partner_id'] != invs[0]['partner_id']):
                    raise orm.except_orm(_('Warning'), _('Not all invoices are for the same partner!'))
                if (d['currency_id'] != invs[0]['currency_id']):
                    raise orm.except_orm(_('Warning'), _('Not all invoices are at the same currency!'))
                if (d['journal_id'] != invs[0]['journal_id']):
                    raise orm.except_orm(_('Warning'), _('Not all invoices are at the same journal!'))
        return

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(invoice_merge, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        self._validate_criteria(cr, uid, context)
        return res

    def create_consolidated_invoice(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        result = mod_obj._get_id(cr, uid, 'account', 'invoice_form')
        id = mod_obj.read(cr, uid, result, ['res_id'])
        consolidated_invoice_obj = self.pool.get('account.consolidated.invoice')
        invoice_id = consolidated_invoice_obj.create_for_invoices(cr, uid, ids, context=context)
        return {
            'domain': "[('id','=', %d)]" % invoice_id,
            'name': _('Consolidated Invoice'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.consolidated.invoice',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'search_view_id': id['res_id']
        }
