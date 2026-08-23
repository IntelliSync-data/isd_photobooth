# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IsdPhotoboothLayoutSystemType(models.Model):
    _name = 'isd.photobooth.layout.system.type'
    _description = 'Photo Booth Layout System Type (Print Config)'
    _order = 'name'

    name = fields.Char('Name', required=True)
    is_cut = fields.Boolean('Is Cut')
    is_landscape = fields.Boolean('Is Landscape')

    # Print dimensions
    print_height = fields.Float('Print Height')
    print_width = fields.Float('Print Width')
    actual_height = fields.Float('Actual Height')
    actual_width = fields.Float('Actual Width')

    # ViewBox
    viewbox_width = fields.Float('ViewBox Width')
    viewbox_height = fields.Float('ViewBox Height')

    # DPI
    dpi = fields.Integer('DPI', default=300)

    # Print margins
    print_top = fields.Float('Margin Top')
    print_left = fields.Float('Margin Left')
    print_bottom = fields.Float('Margin Bottom')
    print_right = fields.Float('Margin Right')

    # Relations
    photobooth_id = fields.Many2one(
        'isd.photobooth', string='Photo Booth', ondelete='cascade'
    )
    layout_system_ids = fields.One2many(
        'isd.photobooth.layout.system', 'layout_system_type_id',
        string='Layout Items'
    )


class IsdPhotoboothLayoutSystem(models.Model):
    _name = 'isd.photobooth.layout.system'
    _description = 'Photo Booth Layout System Item'
    _order = 'sequence, id'

    layout_system_type_id = fields.Many2one(
        'isd.photobooth.layout.system.type', string='Layout System Type',
        required=True, ondelete='cascade'
    )
    sequence = fields.Integer('Sequence', default=10)
    name = fields.Char('Name')
    x = fields.Float('X Position')
    y = fields.Float('Y Position')
    width = fields.Float('Width')
    height = fields.Float('Height')
    is_qr = fields.Boolean('Is QR Code')
