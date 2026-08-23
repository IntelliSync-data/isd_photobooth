# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IsdPhotoboothGroup(models.Model):
    _name = 'isd.photobooth.group'
    _description = 'Photo Booth Group / Location'
    _order = 'name'

    name = fields.Char('Name', required=True)
    address = fields.Text('Address')
    active = fields.Boolean('Active', default=True)
    deleted_at = fields.Datetime('Deleted At', readonly=True, copy=False)

    managed_user_ids = fields.Many2many(
        'res.users', 'isd_photobooth_group_user_rel',
        'group_id', 'user_id',
        string='Managed Users',
        help='Users who manage this group/location'
    )
    photobooth_ids = fields.One2many(
        'isd.photobooth', 'group_id', string='Photo Booths'
    )

    photobooth_count = fields.Integer(
        'Booth Count', compute='_compute_photobooth_count'
    )

    def _compute_photobooth_count(self):
        for record in self:
            record.photobooth_count = len(record.photobooth_ids)

    def action_soft_delete(self):
        self.write({'deleted_at': fields.Datetime.now(), 'active': False})
