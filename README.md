# Consolidated Invoices

## Purpose

This module is designed to group up a set of invoices/refunds so that their 
total value can be seen and they can all be approved/cancelled/paid as a job 
lot.

These are designed to be restricted to a single partner at a time.

Creation can be done by 3 means,

* Invoice list, tick several invoices and select the create consolidated 
  invoice option. 
* From a customer select create consolidated invoice from the extra actions.
  This will allow draft invoices for the customer to be grouped by various
  criteria to potentially create multiple consolidated invoices.
* From the consolidated invoices menu item itself, then manually add the 
  invoices/refunds to the consolidated invoice.

The consolidated invoice will not prevent the individual invoices from being
modified.  It will allow you to confirm/pay them all in bulk (actually marking
the payments against each of the individual invoices).

Issues:

* No tests
* Possible bug after creating a consolidated invoice with the UI going a 
  little funny, new item appears but isn't editable.

# Copyright and License

Copyright (C) 2014 OpusVL

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

If you require assistance, support, or further development of this
software, please contact OpusVL using the details below:

Telephone: +44 (0)1788 298 410
Email: community@opusvl.com
Web: http://opusvl.com

