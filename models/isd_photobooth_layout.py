# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IsdPhotoboothLayout(models.Model):
    _name = 'isd.photobooth.layout'
    _description = 'Photo Booth Layout'
    _order = 'name'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    price = fields.Float('Price', digits=(10, 2))
    image = fields.Binary('Image', attachment=True)
    image_filename = fields.Char('Image Filename')
    image_url = fields.Char('Image URL', help='External image URL')

    frame_type = fields.Selection([
        ('3_2', '3:2'),
        ('2_3', '2:3'),
        ('1_1', '1:1'),
    ], string='Frame Type', required=True)

    layout_type = fields.Selection([
        ('2x2h', '2x2 Horizontal'),
        ('2x2v', '2x2 Vertical'),
        ('1x4h', '1x4 Horizontal'),
        ('3x1h', '3x1 Horizontal'),
        ('2x4h', '2x4 Horizontal'),
        ('1vs3h', '1vs3 Horizontal'),
        ('1x1v', '1x1 Vertical'),
        ('1x2v', '1x2 Vertical'),
        ('2x3square', '2x3 Square'),
        ('1x3square', '1x3 Square'),
    ], string='Layout Type')

    bg_color = fields.Json('Background Colors', help='List of hex color codes')
    paper_size = fields.Selection([
        ('6x4', '6x4 (152mm x 102mm)'),
        ('4x6', '4x6 (102mm x 152mm)'),
        ('6x2', '6x2 (152mm x 51mm)'),
        ('2x6', '2x6 (51mm x 152mm)'),
    ], string='Paper Size')
    active = fields.Boolean('Active', default=True)

    bg_layout_ids = fields.Many2many(
        'isd.photobooth.background', 'isd_photobooth_layout_bg_rel',
        'layout_id', 'bg_layout_id',
        string='Background Layouts'
    )
    layout_theme_ids = fields.One2many(
        'isd.photobooth.layout.theme', 'layout_id', string='Layout Themes'
    )

    def action_clone(self):
        self.ensure_one()
        new = self.copy({
            'name': _('%s (Copy)') % self.name,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'isd.photobooth.layout',
            'res_id': new.id,
            'view_mode': 'form',
        }
