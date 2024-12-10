# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict
from odoo import api, Command, fields, models, _
from contextlib import ExitStack, contextmanager


class AccountMove(models.Model):
    _inherit = "account.move"

    is_employee_advance = fields.Boolean("Is Advance", change_default=True, )
    related_advance_id = fields.Many2one('account.move', string="Related Advance",
                                         domain=[('move_type', '=', 'in_invoice'), ('is_employee_advance', '=', True)])
    hr_expense_sheet_count = fields.Integer("Expense Sheet Count", compute='_compute_hr_expense_sheet_count', )

    department_id = fields.Many2one(
        "hr.department",
        string="Department",
        compute="_compute_department",
        store=True,
        readonly=False
    )

    @api.depends("user_id", "user_id.department_id")
    def _compute_department(self):
        """
        Compute and store the department_id based on the user_id's department.
        """
        for record in self:
            if record.user_id and record.user_id.department_id:
                # Set department_id to the user's department
                record.department_id = record.user_id.department_id
            else:
                # Clear the department_id if no department is assigned
                record.department_id = False

    def _compute_hr_expense_sheet_count(self):
        for record in self:
            record.hr_expense_sheet_count = self.env['hr.expense.sheet'].search_count(
                [('advance_id', '=', record.id)])

    @contextmanager
    def _sync_tax_lines(self, container):
        AccountTax = self.env['account.tax']
        fake_base_line = AccountTax._prepare_base_line_for_taxes_computation(None)

        def get_base_lines(move):
            return move.line_ids.filtered(lambda line: line.display_type in ('product', 'epd', 'rounding', 'cogs'))

        def get_tax_lines(move):
            return move.line_ids.filtered('tax_repartition_line_id')

        def get_value(record, field):
            return self.env['account.move.line']._fields[field].convert_to_write(record[field], record)

        def get_tax_line_tracked_fields(line):
            return ('amount_currency', 'balance')

        def get_base_line_tracked_fields(line):
            grouping_key = AccountTax._prepare_base_line_grouping_key(fake_base_line)
            if line.move_id.is_invoice(include_receipts=True):
                extra_fields = ['price_unit', 'quantity', 'discount']
            else:
                extra_fields = ['amount_currency']
            return list(grouping_key.keys()) + extra_fields

        def field_has_changed(values, record, field):
            return get_value(record, field) != values.get(record, {}).get(field)

        def get_changed_lines(values, records, fields=None):
            return (
                record
                for record in records
                if record not in values
                   or any(
                field_has_changed(values, record, field) for field in values[record] if not fields or field in fields)
            )

        def any_field_has_changed(values, records, fields=None):
            return any(record for record in get_changed_lines(values, records, fields))

        def is_write_needed(line, values):
            return any(
                self.env['account.move.line']._fields[fname].convert_to_write(line[fname], self) != values[fname]
                for fname in values
            )

        moves_values_before = {
            move: {
                field: get_value(move, field)
                for field in ('currency_id', 'partner_id', 'move_type')
            }
            for move in container['records']
            if move.state == 'draft'
        }
        base_lines_values_before = {
            move: {
                line: {
                    field: get_value(line, field)
                    for field in get_base_line_tracked_fields(line)
                }
                for line in get_base_lines(move)
            }
            for move in container['records']
        }
        tax_lines_values_before = {
            move: {
                line: {
                    field: get_value(line, field)
                    for field in get_tax_line_tracked_fields(line)
                }
                for line in get_tax_lines(move)
            }
            for move in container['records']
        }
        yield

        to_delete = []
        to_create = []
        for move in container['records']:
            # if move.state != 'draft':  # block yahmone@smeintellect.com
            #     continue

            tax_lines = get_tax_lines(move)
            base_lines = get_base_lines(move)
            move_tax_lines_values_before = tax_lines_values_before.get(move, {})
            move_base_lines_values_before = base_lines_values_before.get(move, {})
            if (
                    move.is_invoice(include_receipts=True)
                    and (
                    field_has_changed(moves_values_before, move, 'currency_id')
                    or field_has_changed(moves_values_before, move, 'move_type')
            )
            ):
                # Changing the type of an invoice using 'switch to refund' feature or just changing the currency.
                round_from_tax_lines = False
            elif changed_lines := list(get_changed_lines(move_base_lines_values_before, base_lines)):
                # A base line has been modified.
                round_from_tax_lines = (
                    # The changed lines don't affect the taxes.
                        all(not line.tax_ids and not move_base_lines_values_before.get(line, {}).get('tax_ids') for line
                            in changed_lines)
                        # Keep the tax lines amounts if an amount has been manually computed.
                        or any_field_has_changed(move_tax_lines_values_before, tax_lines)
                )

                # If the move has been created with all lines including the tax ones and the balance/amount_currency are provided on
                # base lines, we don't need to recompute anything.
                if (
                        round_from_tax_lines
                        and any(line[field] for line in changed_lines for field in ('amount_currency', 'balance'))
                ):
                    continue
            elif any(line not in base_lines for line, values in move_base_lines_values_before.items() if
                     values['tax_ids']):
                # Removed a base line affecting the taxes.
                round_from_tax_lines = any_field_has_changed(move_tax_lines_values_before, tax_lines)
            else:
                continue

            base_lines_values, tax_lines_values = move._get_rounded_base_and_tax_lines(
                round_from_tax_lines=round_from_tax_lines)
            AccountTax._add_accounting_data_in_base_lines_tax_details(base_lines_values, move.company_id,
                                                                      include_caba_tags=move.always_tax_exigible)
            tax_results = AccountTax._prepare_tax_lines(base_lines_values, move.company_id, tax_lines=tax_lines_values)

            for base_line, to_update in tax_results['base_lines_to_update']:
                line = base_line['record']
                if is_write_needed(line, to_update):
                    line.write(to_update)

            for tax_line_vals in tax_results['tax_lines_to_delete']:
                to_delete.append(tax_line_vals['record'].id)

            for tax_line_vals in tax_results['tax_lines_to_add']:
                to_create.append({
                    **tax_line_vals,
                    'display_type': 'tax',
                    'move_id': move.id,
                })

            for tax_line_vals, grouping_key, to_update in tax_results['tax_lines_to_update']:
                line = tax_line_vals['record']
                if is_write_needed(line, to_update):
                    line.write(to_update)

        if to_delete:
            self.env['account.move.line'].browse(to_delete).with_context(dynamic_unlink=True).unlink()
        if to_create:
            self.env['account.move.line'].create(to_create)
