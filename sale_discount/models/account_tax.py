from odoo import api, models
from odoo.tools import frozendict


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.model
    def _prepare_tax_base_line_dict(
            self,
            base_line,
            partner=None,
            currency=None,
            product=None,
            taxes=None,
            price_unit=None,
            quantity=None,
            discount=None,
            account=None,
            analytic_distribution=None,
            price_subtotal=None,
            is_refund=False,
            rate=None,
            handle_price_include=True,
            extra_context=None,
    ):
        """Prepare tax base line values and include the fixed discount in the calculation."""
        res = super(AccountTax, self)._prepare_tax_base_line_dict(
            base_line=base_line,
            partner=partner,
            currency=currency,
            product=product,
            taxes=taxes,
            price_unit=price_unit,
            quantity=quantity,
            discount=discount,
            account=account,
            analytic_distribution=analytic_distribution,
            price_subtotal=price_subtotal,
            is_refund=is_refund,
            rate=rate,
            handle_price_include=handle_price_include,
            extra_context=extra_context,
        )

        # Adjust discount if a fixed discount is applied
        # if base_line._name == "account.move.line" and base_line.discount_fixed:
            # discount_amount = base_line.discount_fixed
            # Ensure discount is correctly applied to the subtotal
            # res["discount"] = base_line._compute_discount_percentage()
        if 'discount_fixed' in base_line and base_line['quantity'] > 0:
            base_line['price_unit'] -= base_line['discount_fixed'] / base_line['quantity']
            # Adjust the price_subtotal based on the fixed discount
            # if 'price_subtotal' in res:
                # res['price_subtotal'] -= discount_amount  # Subtract fixed discount from subtotal
                # res['price_total'] = res['price_subtotal']  # Update total to reflect the discount
            taxes_computation_fixed = base_line['tax_ids']._get_tax_details(
                price_unit=base_line['price_unit'],
                quantity=base_line['quantity'],
                precision_rounding=base_line['currency_id'].rounding,
                rounding_method=base_line.get('rounding_method', None),
                product=base_line['product_id'],
                special_mode=base_line['special_mode'],
            )

            base_line['tax_details'] = taxes_computation_fixed
            # return res
        return res

    @api.model
    def _prepare_base_line_for_taxes_computation(self, record, **kwargs):
        """ Override the parent method to update the discount_fixed line while keeping the rest unchanged. """

        # Call the parent method to get the existing base line
        base_line = super()._prepare_base_line_for_taxes_computation(record, **kwargs)

        # Override only the 'discount_fixed' field in the base line
        base_line['discount_fixed'] = self._get_base_line_field_value_from_record(
            record, 'discount_fixed', kwargs, 0.0
        )

        return base_line

    @api.model
    def _add_tax_details_in_base_line(self, base_line, company, rounding_method=None):
        """
        Override to incorporate `discount_fixed` while calling the existing logic.
        """
        res=super()._add_tax_details_in_base_line(base_line,company,rounding_method=None)
        # Handle `discount_fixed` adjustment
        #
        if 'discount' in base_line and base_line.get('quantity',0)>0:
            # Ensure adjusted price_unit reflects the discount
            base_line['price_unit'] *= (1 - (base_line['discount'] / 100.0))
        if 'discount_fixed' in base_line and base_line.get('quantity', 0) > 0:
            # Ensure adjusted price_unit reflects the discount fixed
            base_line['price_unit'] -= (base_line['discount_fixed'] / base_line['quantity'])


        # Recompute tax details based on the adjusted price_unit
        taxes_computation = base_line['tax_ids']._get_tax_details(
            price_unit=base_line['price_unit'],
            quantity=base_line['quantity'],
            precision_rounding=base_line['currency_id'].rounding,
            rounding_method=rounding_method or company.tax_calculation_rounding_method,
            product=base_line['product_id'],
            special_mode=base_line['special_mode'],
        )

        # Update the tax details for adding tax field in the sale order
        base_line['tax_details'] = taxes_computation
        rate = base_line['rate']
        tax_details = base_line['tax_details'] = {
            'raw_total_excluded_currency': taxes_computation['total_excluded'],
            'raw_total_excluded': taxes_computation['total_excluded'] / rate if rate else 0.0,
            'raw_total_included_currency': taxes_computation['total_included'],
            'raw_total_included': taxes_computation['total_included'] / rate if rate else 0.0,
            'taxes_data': [],
        }
        if company.tax_calculation_rounding_method == 'round_per_line':
            tax_details['raw_total_excluded'] = company.currency_id.round(tax_details['raw_total_excluded'])
            tax_details['raw_total_included'] = company.currency_id.round(tax_details['raw_total_included'])
        for tax_data in taxes_computation['taxes_data']:
            tax_amount = tax_data['tax_amount'] / rate if rate else 0.0
            base_amount = tax_data['base_amount'] / rate if rate else 0.0
            if company.tax_calculation_rounding_method == 'round_per_line':
                tax_amount = company.currency_id.round(tax_amount)
                base_amount = company.currency_id.round(base_amount)
            tax_details['taxes_data'].append({
                **tax_data,
                'raw_tax_amount_currency': tax_data['tax_amount'],
                'raw_tax_amount': tax_amount,
                'raw_base_amount_currency': tax_data['base_amount'],
                'raw_base_amount': base_amount,
            })
        return res

    @api.model
    def _dispatch_negative_lines(self, base_lines, sorting_criteria=None, additional_dispatching_method=None):
        """
        This method tries to dispatch the amount of negative lines on positive ones with the same tax, resulting in
        a discount for these positive lines. Additionally, it now accounts for fixed discounts in the calculation.

        :param base_lines: A list of python dictionaries created using the '_prepare_base_line_for_taxes_computation' method.
        :param sorting_criteria: Optional list of criteria to sort the candidate for a negative line
        :param additional_dispatching_method: Optional method to transfer additional information (like tax amounts).
                                              It takes as arguments:
                                                  - neg_base_line: the negative line being dispatched
                                                  - candidate: the positive line that will get discounted by neg_base_line
                                                  - is_zero: if the neg_base_line is nulled by the candidate

        :return: A dictionary in the following form:
            {
                'result_lines': Remaining list of positive lines, with their potential increased discount
                'orphan_negative_lines': A list of remaining negative lines that failed to be distributed
                'nulled_candidate_lines': list of previously positive lines that have been nulled (with the discount)
            }
        """

        def dispatch_tax_amounts(neg_base_line, candidate, is_zero):
            def get_tax_key(tax_data):
                return frozendict({'tax': tax_data['tax'], 'is_reverse_charge': tax_data['is_reverse_charge']})

            base_line_fields = (
            'raw_total_excluded_currency', 'raw_total_excluded', 'raw_total_included_currency', 'raw_total_included')
            tax_data_fields = (
            'raw_base_amount_currency', 'raw_base_amount', 'raw_tax_amount_currency', 'raw_tax_amount')

            if is_zero:
                for field in base_line_fields:
                    candidate['tax_details'][field] += neg_base_line['tax_details'][field]
                    neg_base_line['tax_details'][field] = 0.0
            else:
                for field in base_line_fields:
                    neg_base_line['tax_details'][field] += candidate['tax_details'][field]
                    candidate['tax_details'][field] = 0.0

            for tax_data in neg_base_line['tax_details']['taxes_data']:
                tax_key = get_tax_key(tax_data)
                other_tax_data = next(x for x in candidate['tax_details']['taxes_data'] if get_tax_key(x) == tax_key)

                if is_zero:
                    for field in tax_data_fields:
                        other_tax_data[field] += tax_data[field]
                        tax_data[field] = 0.0
                else:
                    for field in tax_data_fields:
                        tax_data[field] += other_tax_data[field]
                        other_tax_data[field] = 0.0

        # Initialize the result structure
        results = {
            'result_lines': [],
            'orphan_negative_lines': [],
            'nulled_candidate_lines': [],
        }

        # Start processing the base lines
        for line in base_lines:
            line.setdefault('discount_amount', line['discount_amount_before_dispatching'])
            line.setdefault('discount_fixed', 0.0)  # Ensure the discount_fixed is initialized

            # Adjust based on the gross price and fixed discount
            if line['currency_id'].compare_amounts(line['gross_price_subtotal'], 0) < 0.0:
                results['orphan_negative_lines'].append(line)
            else:
                results['result_lines'].append(line)

        for neg_base_line in list(results['orphan_negative_lines']):
            candidates = [
                candidate
                for candidate in results['result_lines']
                if (
                        neg_base_line['currency_id'] == candidate['currency_id']
                        and neg_base_line['partner_id'] == candidate['partner_id']
                        and neg_base_line['tax_ids'] == candidate['tax_ids']
                )
            ]

            sorting_criteria = sorting_criteria or self._get_negative_lines_sorting_candidate_criteria()
            sorted_candidates = sorted(candidates, key=lambda candidate: tuple(
                method(candidate, neg_base_line) for method in sorting_criteria))

            # Dispatch fixed and dynamic discounts.
            for candidate in sorted_candidates:
                net_price_subtotal = neg_base_line['gross_price_subtotal'] - neg_base_line['discount_amount'] - \
                                     neg_base_line['discount_fixed']
                other_net_price_subtotal = candidate['gross_price_subtotal'] - candidate['discount_amount'] - candidate[
                    'discount_fixed']
                discount_to_distribute = min(other_net_price_subtotal, -net_price_subtotal)

                if candidate['currency_id'].is_zero(discount_to_distribute):
                    continue

                candidate['discount_amount'] += discount_to_distribute
                neg_base_line['discount_amount'] -= discount_to_distribute

                remaining_to_distribute = neg_base_line['gross_price_subtotal'] - neg_base_line['discount_amount'] - \
                                          neg_base_line['discount_fixed']
                is_zero = neg_base_line['currency_id'].is_zero(remaining_to_distribute)

                dispatch_tax_amounts(neg_base_line, candidate, is_zero)
                if additional_dispatching_method:
                    additional_dispatching_method(neg_base_line, candidate, discount_to_distribute, is_zero)

                remaining_amount = candidate['discount_amount'] - candidate['gross_price_subtotal']
                if candidate['currency_id'].is_zero(remaining_amount):
                    results['result_lines'].remove(candidate)
                    results['nulled_candidate_lines'].append(candidate)

                if is_zero:
                    results['orphan_negative_lines'].remove(neg_base_line)
                    break

        return results







