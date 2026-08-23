# -*- coding: utf-8 -*-

import uuid

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class IsdPhotoboothTransaction(models.Model):
    _name = 'isd.photobooth.transaction'
    _description = 'Photo Booth Transaction'
    _order = 'date desc'
    _rec_name = 'transaction_id'

    transaction_id = fields.Char(
        'Transaction ID', readonly=True, copy=False, index=True,
    )
    photo_app_id = fields.Many2one(
        'isd.photobooth', string='Photo Booth',
        required=True, ondelete='restrict',
    )
    layout_id = fields.Many2one(
        'isd.photobooth.layout', string='Layout',
        ondelete='set null',
    )
    price = fields.Float('Price', digits=(10, 2))
    real_price = fields.Float('Real Price', digits=(10, 2), help='Actual amount received (accumulated)')
    quantity = fields.Integer('Quantity', default=1)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
    ], string='Status', default='draft', required=True)
    date = fields.Datetime('Date', default=fields.Datetime.now, required=True)
    payment_provider = fields.Selection([
        ('cash', 'Cash'),
        ('free', 'Free'),
        ('topup', 'Top Up'),
        ('transfer', 'Transfer'),
        ('fix', 'Fix'),
        ('promotion', 'Promotion'),
    ], string='Payment Provider')
    medias = fields.Json('Medias', help='List of media URLs')
    medias_expired_at = fields.Datetime('Medias Expired At')
    promotion_code = fields.Char('Promotion Code')
    promo_code_id = fields.Many2one(
        'isd.photobooth.promo.code', string='Promo Code',
        ondelete='set null',
    )
    deleted_on = fields.Datetime('Deleted On', readonly=True, copy=False)
    active = fields.Boolean('Active', default=True)

    # Related field for record rules
    group_id = fields.Many2one(
        related='photo_app_id.group_id', string='Group',
        store=True, readonly=True,
    )

    _sql_constraints = [
        ('unique_transaction_id', 'UNIQUE(transaction_id)',
         'Transaction ID must be unique.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('transaction_id'):
                vals['transaction_id'] = self._generate_transaction_id()
        return super().create(vals_list)

    @staticmethod
    def _generate_transaction_id():
        return uuid.uuid4().hex[:16].upper()

    def set_active(self):
        """Set transaction status to active."""
        self.ensure_one()
        self.write({'status': 'active'})

    def update_real_price(self, amount):
        """Accumulate the real price received."""
        self.ensure_one()
        self.write({'real_price': self.real_price + amount})

    def update_medias(self, urls):
        """Update media URLs and set expiry to 3 days from now."""
        self.ensure_one()
        from datetime import timedelta
        self.write({
            'medias': urls,
            'medias_expired_at': fields.Datetime.now() + timedelta(days=3),
        })

    def is_media_expired(self):
        """Check if media URLs have expired."""
        self.ensure_one()
        if not self.medias_expired_at:
            return False
        return fields.Datetime.now() > self.medias_expired_at

    def check_and_set_active(self):
        """Check if accumulated real_price >= price and auto-activate."""
        self.ensure_one()
        if self.status == 'active':
            return True
        provider = self.payment_provider
        if provider in ('free', 'promotion'):
            self.set_active()
            return True
        if self.real_price >= self.price and self.price > 0:
            self.set_active()
            return True
        return False

    def action_soft_delete(self):
        """Soft delete the transaction."""
        self.write({
            'deleted_on': fields.Datetime.now(),
            'active': False,
        })
