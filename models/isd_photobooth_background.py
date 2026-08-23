# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IsdPhotoboothBackground(models.Model):
    _name = 'isd.photobooth.background'
    _description = 'Photo Booth Background Layout'
    _order = 'id desc'

    name = fields.Char('Name', compute='_compute_name', store=True)
    frame_type = fields.Selection([
        ('3_2', '3:2'),
        ('2_3', '2:3'),
        ('1_1', '1:1'),
    ], string='Frame Type', required=True)
    image = fields.Binary('Image', attachment=True)
    image_filename = fields.Char('Image Filename')
    image_url = fields.Char('Image URL', help='External image URL (alternative to upload)')
    active = fields.Boolean('Active', default=True)

    @api.depends('frame_type', 'image_filename')
    def _compute_name(self):
        for record in self:
            fname = record.image_filename or ''
            ftype = dict(self._fields['frame_type'].selection).get(record.frame_type, '')
            record.name = f"{ftype} - {fname}" if fname else ftype
