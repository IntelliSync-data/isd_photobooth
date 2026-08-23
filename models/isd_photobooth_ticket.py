# -*- coding: utf-8 -*-

from odoo import models, fields


class IsdPhotoboothTicket(models.Model):
    _name = 'isd.photobooth.ticket'
    _description = 'Photobooth Support Ticket'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    subject = fields.Char('Subject', required=True)
    description = fields.Text('Description')
    status = fields.Selection([
        ('created', 'Created'),
        ('received', 'Received'),
        ('in_progress', 'In Progress'),
        ('responded', 'Responded'),
        ('completed', 'Completed'),
    ], string='Status', default='created', required=True, tracking=True)
    image_ids = fields.Many2many(
        'ir.attachment', 'isd_photobooth_ticket_attachment_rel',
        'ticket_id', 'attachment_id',
        string='Images',
    )
    created_by_id = fields.Many2one(
        'res.users', string='Created By',
        default=lambda self: self.env.user,
        readonly=True,
    )
    assigned_to_id = fields.Many2one(
        'res.users', string='Assigned To',
    )
    photobooth_id = fields.Many2one(
        'isd.photobooth', string='Photo Booth',
        ondelete='set null',
    )

    def action_receive(self):
        self.write({'status': 'received'})

    def action_in_progress(self):
        self.write({'status': 'in_progress'})

    def action_respond(self):
        self.write({'status': 'responded'})

    def action_complete(self):
        self.write({'status': 'completed'})
