# -*- coding: utf-8 -*-

import random
import string

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class IsdPhotoboothPromotion(models.Model):
    _name = 'isd.photobooth.promotion'
    _description = 'Photo Booth Promotion'
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char('Name', required=True)
    type = fields.Selection([
        ('voucher', 'Voucher'),
        ('coupon', 'Coupon'),
    ], string='Type', required=True)
    num_of_codes = fields.Integer('Number of Codes', default=0)
    used_count = fields.Integer('Used Count', readonly=True, default=0)
    status = fields.Selection([
        ('active', 'Active'),
        ('deactive', 'Deactive'),
    ], string='Status', default='active', required=True)

    # Discount
    amount_off = fields.Float('Amount Off', help='Fixed discount amount (for voucher)')
    percent_off = fields.Float('Percent Off', help='Percentage discount 0-100 (for coupon)')

    # Date range
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')

    # Soft delete
    deleted_on = fields.Datetime('Deleted On', readonly=True, copy=False)
    active = fields.Boolean('Active', default=True)

    # Relations
    group_ids = fields.Many2many(
        'isd.photobooth.group', 'isd_photobooth_promotion_group_rel',
        'promotion_id', 'group_id',
        string='Applicable Groups',
    )
    promo_code_ids = fields.One2many(
        'isd.photobooth.promo.code', 'promotion_id',
        string='Promo Codes',
    )
    promo_code_count = fields.Integer(
        'Promo Code Count', compute='_compute_promo_code_count',
    )

    @api.depends('promo_code_ids')
    def _compute_promo_code_count(self):
        for rec in self:
            rec.promo_code_count = len(rec.promo_code_ids)

    def get_price_off(self, original_price):
        """Return the discount amount based on promotion type."""
        self.ensure_one()
        if self.type == 'voucher':
            return min(self.amount_off, original_price)
        elif self.type == 'coupon':
            return original_price * self.percent_off / 100.0
        return 0.0

    def use_promo_code(self):
        """Increment the used_count by 1."""
        self.ensure_one()
        self.sudo().write({'used_count': self.used_count + 1})

    def is_active(self):
        """Check if promotion is active, not soft-deleted, and within the valid date range."""
        self.ensure_one()
        if self.deleted_on:
            return False
        if self.status != 'active':
            return False
        today = fields.Date.context_today(self)
        if self.start_date and today < self.start_date:
            return False
        if self.end_date and today > self.end_date:
            return False
        return True

    def action_generate_codes(self):
        """Generate num_of_codes random 8-character alphanumeric uppercase promo codes."""
        self.ensure_one()
        if self.num_of_codes <= 0:
            raise UserError(_('Please set a positive number of codes to generate.'))

        PromoCode = self.env['isd.photobooth.promo.code']
        chars = string.ascii_uppercase + string.digits
        existing_codes = set(
            PromoCode.search([]).mapped('code')
        )
        codes_to_create = []
        while len(codes_to_create) < self.num_of_codes:
            code = ''.join(random.choices(chars, k=8))
            if code not in existing_codes:
                existing_codes.add(code)
                codes_to_create.append({
                    'code': code,
                    'promotion_id': self.id,
                })

        PromoCode.create(codes_to_create)
        return True

    def action_soft_delete(self):
        """Soft delete: set deleted_on timestamp and archive."""
        self.write({
            'deleted_on': fields.Datetime.now(),
            'active': False,
        })
