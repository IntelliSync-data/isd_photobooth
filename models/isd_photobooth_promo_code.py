# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IsdPhotoboothPromoCode(models.Model):
    _name = 'isd.photobooth.promo.code'
    _description = 'Photo Booth Promo Code'
    _order = 'create_date desc'
    _rec_name = 'code'

    code = fields.Char('Code', required=True, index=True)
    promotion_id = fields.Many2one(
        'isd.photobooth.promotion', string='Promotion',
        required=True, ondelete='cascade',
    )
    status = fields.Selection([
        ('used', 'Used'),
        ('unused', 'Unused'),
    ], string='Status', default='unused', required=True)
    used_time = fields.Datetime('Used Time', readonly=True)

    # Soft delete
    deleted_on = fields.Datetime('Deleted On', readonly=True, copy=False)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)', 'Promo code must be unique.'),
    ]

    def set_used(self):
        """Mark this promo code as used, record time, and update promotion counter."""
        self.ensure_one()
        self.write({
            'status': 'used',
            'used_time': fields.Datetime.now(),
        })
        self.promotion_id.use_promo_code()

    def is_valid(self):
        """Check if promo code is valid: unused, not deleted, and promotion is active."""
        self.ensure_one()
        if self.status != 'unused':
            return False
        if self.deleted_on:
            return False
        if not self.promotion_id.is_active():
            return False
        return True

    def action_soft_delete(self):
        """Soft delete: set deleted_on timestamp and archive."""
        self.write({
            'deleted_on': fields.Datetime.now(),
            'active': False,
        })
