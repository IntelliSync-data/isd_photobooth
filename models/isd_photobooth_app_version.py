# -*- coding: utf-8 -*-

from odoo import models, fields


class IsdPhotoboothAppVersion(models.Model):
    _name = 'isd.photobooth.app.version'
    _description = 'Photobooth App Version'
    _order = 'create_date desc'

    version = fields.Char('Version', required=True)
    package_url = fields.Char(
        'Package URL', help='Download URL for app package',
    )
    status = fields.Selection([
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled'),
    ], string='Status', default='enabled', required=True)
    notes = fields.Text('Notes', help='Release notes')
