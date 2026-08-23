# -*- coding: utf-8 -*-

import uuid

from odoo import models, fields, api, _
from odoo.exceptions import UserError


# Default layout system type templates
DEFAULT_LAYOUT_SYSTEM_TYPES = {
    '2x2v': {
        'name': '2x2 Vertical', 'is_cut': False, 'is_landscape': False,
        'print_height': 1800, 'print_width': 1200,
        'actual_height': 1800, 'actual_width': 1200,
        'viewbox_width': 1200, 'viewbox_height': 1800, 'dpi': 300,
        'items': [
            {'sequence': 1, 'name': 'Photo 1', 'x': 0, 'y': 0, 'width': 600, 'height': 900},
            {'sequence': 2, 'name': 'Photo 2', 'x': 600, 'y': 0, 'width': 600, 'height': 900},
            {'sequence': 3, 'name': 'Photo 3', 'x': 0, 'y': 900, 'width': 600, 'height': 900},
            {'sequence': 4, 'name': 'Photo 4', 'x': 600, 'y': 900, 'width': 600, 'height': 900},
        ],
    },
    '2x2h': {
        'name': '2x2 Horizontal', 'is_cut': False, 'is_landscape': True,
        'print_height': 1200, 'print_width': 1800,
        'actual_height': 1200, 'actual_width': 1800,
        'viewbox_width': 1800, 'viewbox_height': 1200, 'dpi': 300,
        'items': [
            {'sequence': 1, 'name': 'Photo 1', 'x': 0, 'y': 0, 'width': 900, 'height': 600},
            {'sequence': 2, 'name': 'Photo 2', 'x': 900, 'y': 0, 'width': 900, 'height': 600},
            {'sequence': 3, 'name': 'Photo 3', 'x': 0, 'y': 600, 'width': 900, 'height': 600},
            {'sequence': 4, 'name': 'Photo 4', 'x': 900, 'y': 600, 'width': 900, 'height': 600},
        ],
    },
    '1x4h': {
        'name': '1x4 Horizontal', 'is_cut': True, 'is_landscape': True,
        'print_height': 1200, 'print_width': 1800,
        'actual_height': 600, 'actual_width': 1800,
        'viewbox_width': 1800, 'viewbox_height': 600, 'dpi': 300,
        'items': [
            {'sequence': 1, 'name': 'Photo 1', 'x': 0, 'y': 0, 'width': 450, 'height': 600},
            {'sequence': 2, 'name': 'Photo 2', 'x': 450, 'y': 0, 'width': 450, 'height': 600},
            {'sequence': 3, 'name': 'Photo 3', 'x': 900, 'y': 0, 'width': 450, 'height': 600},
            {'sequence': 4, 'name': 'Photo 4', 'x': 1350, 'y': 0, 'width': 450, 'height': 600},
        ],
    },
    '3x1h': {
        'name': '3x1 Horizontal', 'is_cut': False, 'is_landscape': True,
        'print_height': 1200, 'print_width': 1800,
        'actual_height': 1200, 'actual_width': 1800,
        'viewbox_width': 1800, 'viewbox_height': 1200, 'dpi': 300,
        'items': [
            {'sequence': 1, 'name': 'Photo 1', 'x': 0, 'y': 0, 'width': 600, 'height': 1200},
            {'sequence': 2, 'name': 'Photo 2', 'x': 600, 'y': 0, 'width': 600, 'height': 1200},
            {'sequence': 3, 'name': 'Photo 3', 'x': 1200, 'y': 0, 'width': 600, 'height': 1200},
        ],
    },
    '2x4h': {
        'name': '2x4 Horizontal', 'is_cut': True, 'is_landscape': True,
        'print_height': 1200, 'print_width': 1800,
        'actual_height': 600, 'actual_width': 1800,
        'viewbox_width': 1800, 'viewbox_height': 600, 'dpi': 300,
        'items': [
            {'sequence': 1, 'name': 'Photo 1', 'x': 0, 'y': 0, 'width': 450, 'height': 300},
            {'sequence': 2, 'name': 'Photo 2', 'x': 450, 'y': 0, 'width': 450, 'height': 300},
            {'sequence': 3, 'name': 'Photo 3', 'x': 900, 'y': 0, 'width': 450, 'height': 300},
            {'sequence': 4, 'name': 'Photo 4', 'x': 1350, 'y': 0, 'width': 450, 'height': 300},
            {'sequence': 5, 'name': 'Photo 5', 'x': 0, 'y': 300, 'width': 450, 'height': 300},
            {'sequence': 6, 'name': 'Photo 6', 'x': 450, 'y': 300, 'width': 450, 'height': 300},
            {'sequence': 7, 'name': 'Photo 7', 'x': 900, 'y': 300, 'width': 450, 'height': 300},
            {'sequence': 8, 'name': 'Photo 8', 'x': 1350, 'y': 300, 'width': 450, 'height': 300},
        ],
    },
    '1vs3h': {
        'name': '1vs3 Horizontal', 'is_cut': False, 'is_landscape': True,
        'print_height': 1200, 'print_width': 1800,
        'actual_height': 1200, 'actual_width': 1800,
        'viewbox_width': 1800, 'viewbox_height': 1200, 'dpi': 300,
        'items': [
            {'sequence': 1, 'name': 'Photo 1', 'x': 0, 'y': 0, 'width': 900, 'height': 1200},
            {'sequence': 2, 'name': 'Photo 2', 'x': 900, 'y': 0, 'width': 900, 'height': 400},
            {'sequence': 3, 'name': 'Photo 3', 'x': 900, 'y': 400, 'width': 900, 'height': 400},
            {'sequence': 4, 'name': 'Photo 4', 'x': 900, 'y': 800, 'width': 900, 'height': 400},
        ],
    },
    '1x1v': {
        'name': '1x1 Vertical', 'is_cut': False, 'is_landscape': False,
        'print_height': 1800, 'print_width': 1200,
        'actual_height': 1800, 'actual_width': 1200,
        'viewbox_width': 1200, 'viewbox_height': 1800, 'dpi': 300,
        'items': [
            {'sequence': 1, 'name': 'Photo 1', 'x': 0, 'y': 0, 'width': 1200, 'height': 1800},
        ],
    },
    '1x2v': {
        'name': '1x2 Vertical', 'is_cut': True, 'is_landscape': False,
        'print_height': 1800, 'print_width': 1200,
        'actual_height': 900, 'actual_width': 1200,
        'viewbox_width': 1200, 'viewbox_height': 900, 'dpi': 300,
        'items': [
            {'sequence': 1, 'name': 'Photo 1', 'x': 0, 'y': 0, 'width': 600, 'height': 900},
            {'sequence': 2, 'name': 'Photo 2', 'x': 600, 'y': 0, 'width': 600, 'height': 900},
        ],
    },
    '2x3square': {
        'name': '2x3 Square', 'is_cut': False, 'is_landscape': False,
        'print_height': 1800, 'print_width': 1200,
        'actual_height': 1800, 'actual_width': 1200,
        'viewbox_width': 1200, 'viewbox_height': 1800, 'dpi': 300,
        'items': [
            {'sequence': 1, 'name': 'Photo 1', 'x': 0, 'y': 0, 'width': 600, 'height': 600},
            {'sequence': 2, 'name': 'Photo 2', 'x': 600, 'y': 0, 'width': 600, 'height': 600},
            {'sequence': 3, 'name': 'Photo 3', 'x': 0, 'y': 600, 'width': 600, 'height': 600},
            {'sequence': 4, 'name': 'Photo 4', 'x': 600, 'y': 600, 'width': 600, 'height': 600},
            {'sequence': 5, 'name': 'Photo 5', 'x': 0, 'y': 1200, 'width': 600, 'height': 600},
            {'sequence': 6, 'name': 'Photo 6', 'x': 600, 'y': 1200, 'width': 600, 'height': 600},
        ],
    },
    '1x3square': {
        'name': '1x3 Square', 'is_cut': False, 'is_landscape': False,
        'print_height': 1800, 'print_width': 1200,
        'actual_height': 1800, 'actual_width': 1200,
        'viewbox_width': 1200, 'viewbox_height': 1800, 'dpi': 300,
        'items': [
            {'sequence': 1, 'name': 'Photo 1', 'x': 150, 'y': 0, 'width': 900, 'height': 600},
            {'sequence': 2, 'name': 'Photo 2', 'x': 150, 'y': 600, 'width': 900, 'height': 600},
            {'sequence': 3, 'name': 'Photo 3', 'x': 150, 'y': 1200, 'width': 900, 'height': 600},
        ],
    },
}


class IsdPhotobooth(models.Model):
    _name = 'isd.photobooth'
    _description = 'Photo Booth'
    _order = 'name'
    _rec_name = 'name'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', readonly=True, copy=False, index=True)
    status = fields.Selection([
        ('not_yet', 'Not Yet'),
        ('installed', 'Installed'),
    ], string='Status', default='not_yet', required=True)

    # Appearance
    background_url = fields.Char('Background URL')
    font_color = fields.Char('Font Color', default='#ffffff')

    # Payment & Download
    payment_method = fields.Json(
        'Payment Methods',
        help='e.g. ["cash", "free", "transfer"]',
        default=lambda self: ['cash'],
    )
    download_media_type = fields.Json(
        'Download Media Types',
        help='e.g. ["image", "original_images", "video"]',
        default=lambda self: ['image'],
    )

    # Hardware
    max_prints = fields.Integer('Max Prints', default=0)
    printer_paper_count = fields.Integer('Printer Paper Count', default=0)
    hardware_health_data = fields.Json(
        'Hardware Health', readonly=True,
        help='JSON: {printer: bool, camera: bool, bill_acceptor: bool}'
    )
    last_meta_updated_at = fields.Datetime('Last Meta Updated', readonly=True)

    # App Config
    config_photo_app = fields.Json(
        'App Configuration',
        help='Full UI theme config: colors, icons, labels, bank info, etc.'
    )

    # Relations
    group_id = fields.Many2one(
        'isd.photobooth.group', string='Group / Location',
        ondelete='set null'
    )
    layout_ids = fields.Many2many(
        'isd.photobooth.layout', 'isd_photobooth_layout_rel',
        'photobooth_id', 'layout_id',
        string='Layouts'
    )
    theme_ids = fields.Many2many(
        'isd.photobooth.theme', 'isd_photobooth_theme_rel',
        'photobooth_id', 'theme_id',
        string='Themes'
    )
    layout_system_type_ids = fields.One2many(
        'isd.photobooth.layout.system.type', 'photobooth_id',
        string='Layout System Types'
    )

    active = fields.Boolean('Active', default=True)
    deleted_at = fields.Datetime('Deleted At', readonly=True, copy=False)

    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)', 'Photo Booth code must be unique.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('code'):
                vals['code'] = self._generate_code()
        return super().create(vals_list)

    @staticmethod
    def _generate_code():
        return uuid.uuid4().hex[:12].upper()

    def action_install(self):
        self.ensure_one()
        self.write({'status': 'installed'})

    def action_clone(self):
        self.ensure_one()
        new = self.copy({
            'name': _('%s (Copy)') % self.name,
            'code': self._generate_code(),
            'status': 'not_yet',
        })
        # Clone layout system types with their items
        for lst in self.layout_system_type_ids:
            new_lst = lst.copy({'photobooth_id': new.id})
            for item in lst.layout_system_ids:
                item.copy({'layout_system_type_id': new_lst.id})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'isd.photobooth',
            'res_id': new.id,
            'view_mode': 'form',
        }

    def action_initialize_default_layouts(self):
        self.ensure_one()
        if self.layout_system_type_ids:
            raise UserError(_('This booth already has layout system types. Clear them first.'))

        LayoutSystemType = self.env['isd.photobooth.layout.system.type']
        LayoutSystem = self.env['isd.photobooth.layout.system']

        for key, data in DEFAULT_LAYOUT_SYSTEM_TYPES.items():
            items = data.get('items', [])
            type_vals = {k: v for k, v in data.items() if k != 'items'}
            type_vals['photobooth_id'] = self.id
            lst = LayoutSystemType.create(type_vals)
            for item in items:
                LayoutSystem.create({
                    'layout_system_type_id': lst.id,
                    **item,
                })

    def action_reset_printer(self):
        self.ensure_one()
        self.write({'printer_paper_count': 0})

    def action_soft_delete(self):
        self.write({'deleted_at': fields.Datetime.now(), 'active': False})
