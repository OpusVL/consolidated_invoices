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

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        # FIXME: implement validation of the invoices here.
        res = super(invoice_merge, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        return res

    def create_consolidated_invoice(self, cr, uid, ids, context=None):
        # FIXME: create the new consolidated invoice.
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        result = mod_obj._get_id(cr, uid, 'account', 'invoice_form')
        id = mod_obj.read(cr, uid, result, ['res_id'])
        return {
            'domain': "[('id','in', [" + ','.join(map(str, allinvoices.keys())) + "])]",
            'name': _('Consolidated Invoice'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.consolidated.invoice',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'search_view_id': id['res_id']
        }
