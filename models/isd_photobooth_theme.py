# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IsdPhotoboothTheme(models.Model):
    _name = 'isd.photobooth.theme'
    _description = 'Photo Booth Theme'
    _order = 'name'

    name = fields.Char('Name', required=True)
    background = fields.Binary('Background', attachment=True)
    background_filename = fields.Char('Background Filename')
    background_url = fields.Char('Background URL', help='External background URL')
    active = fields.Boolean('Active', default=True)
