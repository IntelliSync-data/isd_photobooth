# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IsdPhotoboothAuditLog(models.Model):
    _name = 'isd.photobooth.audit.log'
    _description = 'Photobooth Audit Log'
    _order = 'timestamp desc'

    model_name = fields.Char('Model Name', required=True, index=True)
    model_id = fields.Integer('Record ID', required=True, index=True)
    action = fields.Selection([
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ], string='Action', required=True)
    user_id = fields.Many2one(
        'res.users', string='User',
        ondelete='set null',
    )
    timestamp = fields.Datetime(
        'Timestamp', default=fields.Datetime.now, index=True,
    )
    data = fields.Json(
        'Data',
        help='JSON: {previous_state, current_state, changes, action_details}',
    )
    source = fields.Selection([
        ('portal', 'Portal'),
        ('photobooth', 'Photobooth'),
    ], string='Source', default='portal')
    summary = fields.Char('Summary', compute='_compute_summary', store=True)

    @api.depends('action', 'model_name', 'model_id')
    def _compute_summary(self):
        for rec in self:
            action_label = dict(
                rec._fields['action'].selection
            ).get(rec.action, rec.action or '')
            rec.summary = '%s %s #%s' % (
                action_label, rec.model_name or '', rec.model_id or 0,
            )

    @api.model
    def log_change(self, model_name, model_id, action, data,
                   source='portal', user_id=None):
        """Create an audit log record."""
        return self.sudo().create({
            'model_name': model_name,
            'model_id': model_id,
            'action': action,
            'data': data,
            'source': source,
            'user_id': user_id,
        })
