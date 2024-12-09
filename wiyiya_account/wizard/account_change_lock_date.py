from odoo import api, models, fields, _
from odoo.addons.account.models.company import SOFT_LOCK_DATE_FIELDS, LOCK_DATE_FIELDS


class AccountChangeLockDate(models.TransientModel):
    """
    This wizard is used to change the lock date
    """
    _inherit = 'account.change.lock.date'

    def _get_changes_needing_exception(self):
        self.ensure_one()

        return {
            field: self[field]
            for field in SOFT_LOCK_DATE_FIELDS
            if self.env.company[field] and (not self[field]) #  or self[field] < self.env.company[field]
        }
