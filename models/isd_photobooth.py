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

    # App Config - Layout & Description
    cfg_is_display_layout_description = fields.Boolean('Display Layout Description', default=False)

    # App Config - Bank Customization (linked to isd_payment)
    cfg_payment_method_id = fields.Many2one(
        'isd.payment.method', string='Payment Method',
        help='Link to payment method for bank info (name, account number, prefix)',
    )
    cfg_branch = fields.Char(
        'Branch', help='Branch/machine identifier sent to payment API (e.g. "Huế - Máy 1")',
    )

    # App Config - UI Colors
    cfg_color_button = fields.Char('Button Text Color')
    cfg_bg_button = fields.Char('Button Background Color')
    cfg_cell_theme_font_color = fields.Char('Theme Cell Font Color', default='#FFFFFF')

    # App Config - Background Images (Main Screens)
    cfg_bg_main = fields.Char('Home Screen BG')
    cfg_bg_layout = fields.Char('Layout Screen BG')
    cfg_bg_theme = fields.Char('Theme Screen BG')
    cfg_bg_quantity = fields.Char('Quantity Screen BG')
    cfg_bg_payment = fields.Char('Payment Screen BG')
    cfg_bg_payment_notice = fields.Char('Payment Notice Screen BG')
    cfg_bg_popup = fields.Char('Popup BG')
    cfg_bg_ads = fields.Char('Ads Screen BG')

    # App Config - Background Images (Camera Screens)
    cfg_bg_camera_mode = fields.Char('Camera Mode Screen BG')
    cfg_bg_frame = fields.Char('Frame Screen BG')
    cfg_bg_frame_horizontal = fields.Char('Horizontal Capture BG')
    cfg_bg_frame_vertical = fields.Char('Vertical Capture BG')
    cfg_bg_frame_square = fields.Char('Square Capture BG')

    # App Config - Background Images (Preview & Print)
    cfg_bg_preview_horizontal = fields.Char('Horizontal Preview BG')
    cfg_bg_preview_vertical = fields.Char('Vertical Preview BG')
    cfg_bg_print = fields.Char('Print Screen BG')

    # App Config - Button/Icon Images
    cfg_btn_back = fields.Char('Back Button Icon')
    cfg_btn_home = fields.Char('Home Button Icon')
    cfg_btn_next = fields.Char('Next Button Icon')
    cfg_btn_prev = fields.Char('Previous Button Icon')
    cfg_icon_arrow_left = fields.Char('Arrow Left Icon')

    # App Config - Capture Mode Icons
    cfg_icon_auto_capture = fields.Char('Auto Capture Icon')
    cfg_icon_remote_capture = fields.Char('Remote Capture Icon')

    # App Config - Camera Labels
    cfg_camera_label_time = fields.Char('Camera Time Label')
    cfg_camera_label_quantity = fields.Char('Camera Quantity Label')

    # App Config - Payment Notice
    cfg_content_payment_notice = fields.Char('Payment Notice Content')

    # App Config - Ads
    cfg_url_ads = fields.Char('Advertisement URL')

    # App Config - Theme
    cfg_is_hide_label_theme = fields.Boolean('Hide Theme Labels', default=False)

    # Computed JSON for API
    config_photo_app = fields.Json(
        'App Configuration', compute='_compute_config_photo_app', store=True,
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

    # Mapping: config JSON key -> Odoo field name
    _CONFIG_FIELD_MAP = {
        'is_display_layout_description': 'cfg_is_display_layout_description',
        'color_button': 'cfg_color_button',
        'bg_button': 'cfg_bg_button',
        'cell_theme_font_color': 'cfg_cell_theme_font_color',
        'bg_main': 'cfg_bg_main',
        'bg_layout': 'cfg_bg_layout',
        'bg_theme': 'cfg_bg_theme',
        'bg_quantity': 'cfg_bg_quantity',
        'bg_payment': 'cfg_bg_payment',
        'bg_payment_notice': 'cfg_bg_payment_notice',
        'bg_popup': 'cfg_bg_popup',
        'bg_ads': 'cfg_bg_ads',
        'bg_camera_mode': 'cfg_bg_camera_mode',
        'bg_frame': 'cfg_bg_frame',
        'bg_frame_horizontal': 'cfg_bg_frame_horizontal',
        'bg_frame_vertical': 'cfg_bg_frame_vertical',
        'bg_frame_square': 'cfg_bg_frame_square',
        'bg_preview_horizontal': 'cfg_bg_preview_horizontal',
        'bg_preview_vertical': 'cfg_bg_preview_vertical',
        'bg_print': 'cfg_bg_print',
        'btn_back': 'cfg_btn_back',
        'btn_home': 'cfg_btn_home',
        'btn_next': 'cfg_btn_next',
        'btn_prev': 'cfg_btn_prev',
        'icon_arrow_left': 'cfg_icon_arrow_left',
        'icon_auto_capture': 'cfg_icon_auto_capture',
        'icon_remote_capture': 'cfg_icon_remote_capture',
        'camera_label_time': 'cfg_camera_label_time',
        'camera_label_quantity': 'cfg_camera_label_quantity',
        'content_payment_notice': 'cfg_content_payment_notice',
        'url_ads': 'cfg_url_ads',
        'is_hide_label_theme': 'cfg_is_hide_label_theme',
    }

    _BOOL_CONFIG_KEYS = {'is_display_layout_description', 'is_hide_label_theme'}

    @api.depends(
        'cfg_is_display_layout_description',
        'cfg_payment_method_id', 'cfg_payment_method_id.name',
        'cfg_payment_method_id.provider_account_id', 'cfg_payment_method_id.prefix',
        'cfg_payment_method_id.acb_beneficiary_name', 'cfg_payment_method_id.acb_account_number',
        'cfg_branch',
        'cfg_color_button', 'cfg_bg_button', 'cfg_cell_theme_font_color',
        'cfg_bg_main', 'cfg_bg_layout', 'cfg_bg_theme', 'cfg_bg_quantity',
        'cfg_bg_payment', 'cfg_bg_payment_notice', 'cfg_bg_popup', 'cfg_bg_ads',
        'cfg_bg_camera_mode', 'cfg_bg_frame', 'cfg_bg_frame_horizontal',
        'cfg_bg_frame_vertical', 'cfg_bg_frame_square',
        'cfg_bg_preview_horizontal', 'cfg_bg_preview_vertical', 'cfg_bg_print',
        'cfg_btn_back', 'cfg_btn_home', 'cfg_btn_next', 'cfg_btn_prev',
        'cfg_icon_arrow_left', 'cfg_icon_auto_capture', 'cfg_icon_remote_capture',
        'cfg_camera_label_time', 'cfg_camera_label_quantity',
        'cfg_content_payment_notice', 'cfg_url_ads', 'cfg_is_hide_label_theme',
    )
    def _compute_config_photo_app(self):
        for record in self:
            config = {}
            for key, field_name in self._CONFIG_FIELD_MAP.items():
                val = record[field_name]
                if key in self._BOOL_CONFIG_KEYS:
                    config[key] = 'true' if val else 'false'
                elif val:
                    config[key] = val
            # Bank info from linked payment method
            pm = record.cfg_payment_method_id
            if pm:
                config['bank_account_name'] = pm.acb_beneficiary_name or pm.name or ''
                config['bank_account_number'] = pm.acb_account_number or pm.provider_account_id or ''
                config['bank_account_prefix'] = pm.prefix or ''
                config['payment_method_id'] = pm.id
            if record.cfg_branch:
                config['branch'] = record.cfg_branch
            record.config_photo_app = config

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
