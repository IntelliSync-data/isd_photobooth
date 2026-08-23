# -*- coding: utf-8 -*-

import uuid

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from .s3_image_mixin import upload_binary_fields_to_s3


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

    # Payment & Download — checkboxes
    pm_cash = fields.Boolean('Cash', default=True)
    pm_free = fields.Boolean('Free')
    pm_transfer = fields.Boolean('Transfer')
    payment_method = fields.Json(
        'Payment Methods', compute='_compute_payment_method', store=True,
    )

    dl_image = fields.Boolean('Image', default=True)
    dl_original_images = fields.Boolean('Original Images')
    dl_video = fields.Boolean('Video')
    download_media_type = fields.Json(
        'Download Media Types', compute='_compute_download_media_type', store=True,
    )

    # Hardware
    max_prints = fields.Integer('Max Prints', default=0)
    printer_paper_count = fields.Integer('Printer Paper Count', default=0)
    hardware_health_data = fields.Json(
        'Hardware Health', readonly=True,
        help='JSON: {printer: bool, camera: bool, bill_acceptor: bool}'
    )
    last_meta_updated_at = fields.Datetime('Last Meta Updated', readonly=True)

    # ── App Config: Layout & Theme ──
    cfg_is_display_layout_description = fields.Boolean('Display Layout Description', default=False)

    # ── App Config: Bank Customization ──
    cfg_payment_method_id = fields.Many2one(
        'isd_payment.method', string='Payment Method',
        help='Link to payment method for bank info (name, account number, prefix)',
    )
    cfg_branch = fields.Char(
        'Branch',
        help='Branch/machine identifier sent to payment API (e.g. "Huế - Máy 1")',
    )

    # ── App Config: UI Customization ──
    # Colors
    cfg_title_font_color = fields.Char('Title Font Color')
    cfg_color_button = fields.Char('Button Text Color')
    cfg_bg_button = fields.Char('Button Background Color')

    # Images (exact order from React source)
    cfg_btn_back = fields.Image('Back Button Icon', attachment=True)
    cfg_bg_main = fields.Image('Home Screen BG', attachment=True)
    cfg_bg_layout = fields.Image('Layout Screen BG', attachment=True)
    cfg_bg_theme = fields.Image('Theme Screen BG', attachment=True)
    cfg_is_hide_label_theme = fields.Boolean('Hide Theme Labels', default=False)
    cfg_cell_theme_font_color = fields.Char('Theme Cell Font Color', default='#FFFFFF')
    cfg_bg_frame = fields.Image('Frame Screen BG', attachment=True)
    cfg_btn_prev = fields.Image('Previous Button Icon', attachment=True)
    cfg_btn_next = fields.Image('Next Button Icon', attachment=True)
    cfg_bg_quantity = fields.Image('Quantity Screen BG', attachment=True)
    cfg_icon_arrow_left = fields.Image('Arrow Right Icon', attachment=True)
    cfg_bg_payment = fields.Image('Payment Screen BG', attachment=True)
    cfg_bg_payment_notice = fields.Image('Payment Notice Screen BG', attachment=True)
    cfg_content_payment_notice = fields.Image('Payment Notice Content', attachment=True)
    cfg_bg_camera_mode = fields.Image('Camera Mode Screen BG', attachment=True)
    cfg_icon_auto_capture = fields.Image('Auto Capture Icon', attachment=True)
    cfg_icon_remote_capture = fields.Image('Remote Capture Icon', attachment=True)
    cfg_bg_frame_horizontal = fields.Image('Horizontal Capture BG', attachment=True)
    cfg_bg_frame_vertical = fields.Image('Vertical Capture BG', attachment=True)
    cfg_camera_label_time = fields.Image('Camera Time Label', attachment=True)
    cfg_camera_label_quantity = fields.Image('Camera Quantity Label', attachment=True)
    cfg_bg_frame_square = fields.Image('Square Capture BG', attachment=True)
    cfg_bg_preview_horizontal = fields.Image('Horizontal Preview BG', attachment=True)
    cfg_bg_preview_vertical = fields.Image('Vertical Preview BG', attachment=True)
    cfg_bg_print = fields.Image('Print Screen BG', attachment=True)
    cfg_btn_home = fields.Image('Home Button Icon', attachment=True)
    cfg_bg_popup = fields.Image('Popup BG', attachment=True)
    cfg_bg_ads = fields.Image('Ads Screen BG', attachment=True)
    cfg_url_ads = fields.Char('Advertisement URL')
    cfg_image_urls = fields.Json('Config Image URLs', help='S3 URLs for cfg_* image fields')

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

    # Mapping: config JSON key -> Odoo field name (text/bool fields only)
    _CONFIG_TEXT_MAP = {
        'is_display_layout_description': 'cfg_is_display_layout_description',
        'font_color': 'cfg_title_font_color',
        'color_button': 'cfg_color_button',
        'bg_button': 'cfg_bg_button',
        'cell_theme_font_color': 'cfg_cell_theme_font_color',
        'is_hide_label_theme': 'cfg_is_hide_label_theme',
        'url_ads': 'cfg_url_ads',
    }

    # Mapping: config JSON key -> Odoo field name (image fields)
    _CONFIG_IMAGE_MAP = {
        'btn_back': 'cfg_btn_back',
        'bg_main': 'cfg_bg_main',
        'bg_layout': 'cfg_bg_layout',
        'bg_theme': 'cfg_bg_theme',
        'bg_frame': 'cfg_bg_frame',
        'btn_prev': 'cfg_btn_prev',
        'btn_next': 'cfg_btn_next',
        'bg_quantity': 'cfg_bg_quantity',
        'icon_arrow_left': 'cfg_icon_arrow_left',
        'bg_payment': 'cfg_bg_payment',
        'bg_payment_notice': 'cfg_bg_payment_notice',
        'content_payment_notice': 'cfg_content_payment_notice',
        'bg_camera_mode': 'cfg_bg_camera_mode',
        'icon_auto_capture': 'cfg_icon_auto_capture',
        'icon_remote_capture': 'cfg_icon_remote_capture',
        'bg_frame_horizontal': 'cfg_bg_frame_horizontal',
        'bg_frame_vertical': 'cfg_bg_frame_vertical',
        'camera_label_time': 'cfg_camera_label_time',
        'camera_label_quantity': 'cfg_camera_label_quantity',
        'bg_frame_square': 'cfg_bg_frame_square',
        'bg_preview_horizontal': 'cfg_bg_preview_horizontal',
        'bg_preview_vertical': 'cfg_bg_preview_vertical',
        'bg_print': 'cfg_bg_print',
        'btn_home': 'cfg_btn_home',
        'bg_popup': 'cfg_bg_popup',
        'bg_ads': 'cfg_bg_ads',
    }

    _BOOL_CONFIG_KEYS = {'is_display_layout_description', 'is_hide_label_theme'}

    @api.depends('pm_cash', 'pm_free', 'pm_transfer')
    def _compute_payment_method(self):
        mapping = [('pm_cash', 'cash'), ('pm_free', 'free'), ('pm_transfer', 'transfer')]
        for record in self:
            record.payment_method = [v for f, v in mapping if record[f]]

    @api.depends('dl_image', 'dl_original_images', 'dl_video')
    def _compute_download_media_type(self):
        mapping = [('dl_image', 'image'), ('dl_original_images', 'original_images'), ('dl_video', 'video')]
        for record in self:
            record.download_media_type = [v for f, v in mapping if record[f]]

    @api.depends(
        'cfg_is_display_layout_description', 'cfg_is_hide_label_theme',
        'cfg_payment_method_id', 'cfg_branch',
        'cfg_title_font_color', 'cfg_color_button', 'cfg_bg_button', 'cfg_cell_theme_font_color',
        'cfg_url_ads', 'cfg_image_urls',
    )
    def _compute_config_photo_app(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        for record in self:
            config = {}
            # Text/bool fields
            for key, field_name in self._CONFIG_TEXT_MAP.items():
                val = record[field_name]
                if key in self._BOOL_CONFIG_KEYS:
                    config[key] = 'true' if val else 'false'
                elif val:
                    config[key] = val
            # Image fields -> S3 URLs (fallback to Odoo /web/image/)
            s3_urls = record.cfg_image_urls or {}
            for key, field_name in self._CONFIG_IMAGE_MAP.items():
                if key in s3_urls:
                    config[key] = s3_urls[key]
                elif record[field_name]:
                    config[key] = f"{base_url}/web/image/isd.photobooth/{record.id}/{field_name}"
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

    def _upload_cfg_images_to_s3(self, vals):
        """Upload cfg_* image fields to S3 and store URLs in cfg_image_urls."""
        from odoo.addons.isd_photobooth.services import PhotoboothS3Service
        s3 = PhotoboothS3Service(self.env)
        if not s3.is_configured():
            return

        import base64 as b64
        import mimetypes

        cfg_urls = dict(vals.get('cfg_image_urls') or {})
        changed = False

        for config_key, field_name in self._CONFIG_IMAGE_MAP.items():
            if field_name not in vals or not vals[field_name]:
                continue
            try:
                data = vals[field_name]
                if isinstance(data, str):
                    data = b64.b64decode(data)
                filename = f"{config_key}.png"
                mime = mimetypes.guess_type(filename)[0] or 'image/png'
                url = s3.upload_asset(data, filename, mime)
                cfg_urls[config_key] = url
                changed = True
            except Exception:
                import logging
                logging.getLogger(__name__).exception(
                    "S3 upload failed for cfg field %s", field_name)

        if changed:
            vals['cfg_image_urls'] = cfg_urls

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('code'):
                vals['code'] = self._generate_code()
            self._upload_cfg_images_to_s3(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._upload_cfg_images_to_s3(vals)
        return super().write(vals)

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
