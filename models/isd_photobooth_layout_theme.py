# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IsdPhotoboothLayoutTheme(models.Model):
    _name = 'isd.photobooth.layout.theme'
    _description = 'Photo Booth Layout Theme'
    _order = 'id'

    theme_id = fields.Many2one(
        'isd.photobooth.theme', string='Theme',
        required=True, ondelete='cascade'
    )
    layout_id = fields.Many2one(
        'isd.photobooth.layout', string='Layout',
        required=True, ondelete='cascade'
    )
    bg_layout_ids = fields.Many2many(
        'isd.photobooth.background', 'isd_photobooth_layout_theme_bg_rel',
        'layout_theme_id', 'bg_layout_id',
        string='Background Layouts'
    )

    _sql_constraints = [
        ('unique_theme_layout', 'UNIQUE(theme_id, layout_id)',
         'Theme + Layout combination must be unique.'),
    ]
