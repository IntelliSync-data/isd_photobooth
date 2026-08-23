# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from .s3_image_mixin import upload_binary_fields_to_s3

_S3_FIELDS = {'background': 'background_url'}


class IsdPhotoboothTheme(models.Model):
    _name = 'isd.photobooth.theme'
    _description = 'Photo Booth Theme'
    _order = 'name'

    name = fields.Char('Name', required=True)
    background = fields.Binary('Background', attachment=True)
    background_filename = fields.Char('Background Filename')
    background_url = fields.Char('Background URL', help='External background URL')
    active = fields.Boolean('Active', default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            upload_binary_fields_to_s3(self.env, vals, _S3_FIELDS)
        return super().create(vals_list)

    def write(self, vals):
        upload_binary_fields_to_s3(self.env, vals, _S3_FIELDS)
        return super().write(vals)
