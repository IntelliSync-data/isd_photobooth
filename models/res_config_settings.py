# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # S3 Storage — falls back to isd_media.s3_* params when empty
    photobooth_s3_bucket_name = fields.Char('S3 Bucket Name')
    photobooth_s3_region = fields.Char('S3 Region')
    photobooth_s3_access_key = fields.Char('S3 Access Key')
    photobooth_s3_secret_key = fields.Char('S3 Secret Key')
    photobooth_s3_endpoint_url = fields.Char('S3 Endpoint URL')
    photobooth_s3_public_base_url = fields.Char('S3 Public Base URL')
    photobooth_s3_use_ssl = fields.Boolean('Use SSL', default=True)

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        res.update(
            photobooth_s3_bucket_name=ICP.get_param('isd_photobooth.s3_bucket_name', ''),
            photobooth_s3_region=ICP.get_param('isd_photobooth.s3_region', ''),
            photobooth_s3_access_key=ICP.get_param('isd_photobooth.s3_access_key', ''),
            photobooth_s3_secret_key=ICP.get_param('isd_photobooth.s3_secret_key', ''),
            photobooth_s3_endpoint_url=ICP.get_param('isd_photobooth.s3_endpoint_url', ''),
            photobooth_s3_public_base_url=ICP.get_param('isd_photobooth.s3_public_base_url', ''),
            photobooth_s3_use_ssl=ICP.get_param('isd_photobooth.s3_use_ssl', 'True') == 'True',
        )
        return res

    def set_values(self):
        super().set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('isd_photobooth.s3_bucket_name', self.photobooth_s3_bucket_name or '')
        ICP.set_param('isd_photobooth.s3_region', self.photobooth_s3_region or '')
        ICP.set_param('isd_photobooth.s3_access_key', self.photobooth_s3_access_key or '')
        ICP.set_param('isd_photobooth.s3_secret_key', self.photobooth_s3_secret_key or '')
        ICP.set_param('isd_photobooth.s3_endpoint_url', self.photobooth_s3_endpoint_url or '')
        ICP.set_param('isd_photobooth.s3_public_base_url', self.photobooth_s3_public_base_url or '')
        ICP.set_param('isd_photobooth.s3_use_ssl', str(self.photobooth_s3_use_ssl))
