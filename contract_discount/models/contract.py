# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.exceptions import ValidationError

from openerp.tools.translate import _

from openerp.osv import fields as old_fields


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = "account.analytic.invoice.line"

    @api.one
    @api.depends('price_unit', 'quantity', 'discount')
    def _amount_line(self):
        self.price_subtotal = self.quantity * (self.price_unit * (1 - (self.discount or 0.0) / 100.0))

    price_subtotal = fields.Float(
        compute='_amount_line',
        string='Sub Total',
        digits=dp.get_precision('Account'))

    discount = fields.Float(
        string='Discount (%)',
        digits=dp.get_precision('Discount'),
        copy=True,
        help='Discount that is applied in generated invoices.'
        ' It should be less or equal to 100')

    @api.one
    @api.constrains('discount')
    def _check_discount(self):
        if self.discount > 100:
            raise ValidationError(_("Discount should be less or equal to 100"))


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _prepare_invoice_line(self, line, fiscal_position):
        res = super(AccountAnalyticAccount, self)._prepare_invoice_line(
            line, fiscal_position)
        res['discount'] = line.discount or 0
        return res
