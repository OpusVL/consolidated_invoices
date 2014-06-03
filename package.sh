#!/bin/sh

# Accepts further arguments on the command line for zip(1).

zip "$@" -r consolidated_invoices consolidated_invoices
