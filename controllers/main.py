# -*- coding: utf-8 -*-

import json
import logging
import base64
from datetime import timedelta

from odoo import http, fields, _
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class IsdPhotoboothController(http.Controller):

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _json_response(self, data, status=200):
        """Return a JSON HTTP response."""
        return Response(
            json.dumps(data, ensure_ascii=False, default=str),
            status=status,
            headers={'Content-Type': 'application/json'},
        )

    def _error_response(self, message, status=400, code=None):
        """Return a JSON error response."""
        payload = {'success': False, 'error': message}
        if code:
            payload['error_code'] = code
        return self._json_response(payload, status=status)

    def _get_json_body(self):
        """Parse JSON body from the request."""
        try:
            body = request.httprequest.get_data(as_text=True)
            return json.loads(body) if body else {}
        except (json.JSONDecodeError, Exception):
            return {}

    def _authenticate_booth(self, booth_id):
        """Authenticate request using x-api-token header matching booth code.
        Returns (booth_record, error_response). If error_response is not None,
        return it immediately.
        """
        Booth = request.env['isd.photobooth'].sudo()
        booth = Booth.browse(booth_id)
        if not booth.exists():
            return None, self._error_response('Booth not found', status=404, code='BOOTH_NOT_FOUND')

        token = request.httprequest.headers.get('x-api-token', '')
        if token != booth.code:
            return None, self._error_response('Invalid API token', status=401, code='UNAUTHORIZED')

        return booth, None

    # ==================================================================
    # Booth App API (Section 2.3)
    # ==================================================================

    @http.route('/api/v1/photobooth/setup', type='http', auth='public',
                methods=['POST'], csrf=False)
    def setup_booth(self, **kwargs):
        """POST /api/v1/photobooth/setup - Register a new booth."""
        try:
            data = self._get_json_body()
            name = data.get('name')
            group_code = data.get('group_code')

            if not name:
                return self._error_response('name is required')

            Booth = request.env['isd.photobooth'].sudo()
            vals = {'name': name}

            if group_code:
                Group = request.env['isd.photobooth.group'].sudo()
                group = Group.search([('name', '=', group_code)], limit=1)
                if group:
                    vals['group_id'] = group.id

            booth = Booth.create(vals)

            return self._json_response({
                'success': True,
                'data': {
                    'id': booth.id,
                    'code': booth.code,
                    'name': booth.name,
                },
            })
        except Exception as e:
            _logger.exception('Error in setup_booth')
            return self._error_response(str(e), status=500)

    @http.route('/api/v1/photobooth/check_version', type='http', auth='public',
                methods=['GET'], csrf=False)
    def check_version(self, **kwargs):
        """GET /api/v1/photobooth/check_version - Check C# app version."""
        try:
            version = kwargs.get('version', '')
            AppVersion = request.env['isd.photobooth.app.version'].sudo()
            latest = AppVersion.search([('status', '=', 'enabled')], order='create_date desc', limit=1)
            latest_version = latest.version if latest else ''

            is_latest = version == latest_version if version and latest_version else False

            data = {
                'current_version': version,
                'latest_version': latest_version,
                'is_latest': is_latest,
                'update_required': not is_latest,
            }
            if latest and not is_latest:
                data['package_url'] = latest.package_url or ''
                data['notes'] = latest.notes or ''

            return self._json_response({
                'success': True,
                'data': data,
            })
        except Exception as e:
            _logger.exception('Error in check_version')
            return self._error_response(str(e), status=500)

    @http.route('/api/v1/photobooth/<int:booth_id>/ping', type='http',
                auth='public', methods=['POST'], csrf=False)
    def ping(self, booth_id, **kwargs):
        """POST /api/v1/photobooth/<booth_id>/ping - Health check + hardware status."""
        try:
            booth, error = self._authenticate_booth(booth_id)
            if error:
                return error

            data = self._get_json_body()
            health = {
                'printer': data.get('printer', False),
                'camera': data.get('camera', False),
                'bill_acceptor': data.get('bill_acceptor', False),
            }
            vals = {
                'hardware_health_data': health,
                'last_meta_updated_at': fields.Datetime.now(),
            }
            if 'printer_paper_count' in data:
                vals['printer_paper_count'] = int(data['printer_paper_count'])

            booth.write(vals)

            return self._json_response({
                'success': True,
                'data': {'status': 'ok'},
            })
        except Exception as e:
            _logger.exception('Error in ping')
            return self._error_response(str(e), status=500)

    @http.route('/api/v1/photobooth/<int:booth_id>/info', type='http',
                auth='public', methods=['GET'], csrf=False)
    def get_info(self, booth_id, **kwargs):
        """GET /api/v1/photobooth/<booth_id>/info - Get booth config."""
        try:
            booth, error = self._authenticate_booth(booth_id)
            if error:
                return error

            layouts = []
            for layout in booth.layout_ids:
                layouts.append({
                    'id': layout.id,
                    'name': layout.name,
                    'price': layout.price,
                    'frame_type': layout.frame_type,
                    'layout_type': layout.layout_type,
                    'image_url': layout.image_url or '',
                })

            themes = []
            for theme in booth.theme_ids:
                themes.append({
                    'id': theme.id,
                    'name': theme.name,
                })

            return self._json_response({
                'success': True,
                'data': {
                    'id': booth.id,
                    'name': booth.name,
                    'code': booth.code,
                    'status': booth.status,
                    'config_photo_app': booth.config_photo_app or {},
                    'payment_method': booth.payment_method or [],
                    'download_media_type': booth.download_media_type or [],
                    'max_prints': booth.max_prints,
                    'printer_paper_count': booth.printer_paper_count,
                    'layouts': layouts,
                    'themes': themes,
                },
            })
        except Exception as e:
            _logger.exception('Error in get_info')
            return self._error_response(str(e), status=500)

    @http.route('/api/v1/photobooth/<int:booth_id>/layouts', type='http',
                auth='public', methods=['GET'], csrf=False)
    def get_layouts(self, booth_id, **kwargs):
        """GET /api/v1/photobooth/<booth_id>/layouts - Get layouts for booth."""
        try:
            booth, error = self._authenticate_booth(booth_id)
            if error:
                return error

            layouts = []
            for layout in booth.layout_ids:
                bg_layouts = []
                for bg in layout.bg_layout_ids:
                    bg_layouts.append({
                        'id': bg.id,
                        'image_url': bg.image_url or '',
                        'frame_type': bg.frame_type,
                    })

                themes = []
                for lt in layout.layout_theme_ids:
                    if lt.theme_id:
                        themes.append({
                            'id': lt.theme_id.id,
                            'name': lt.theme_id.name,
                            'bg_layouts': [
                                {'id': b.id, 'image_url': b.image_url or '', 'frame_type': b.frame_type}
                                for b in lt.bg_layout_ids
                            ],
                        })

                layouts.append({
                    'id': layout.id,
                    'name': layout.name,
                    'price': layout.price,
                    'frame_type': layout.frame_type,
                    'layout_type': layout.layout_type,
                    'image_url': layout.image_url or '',
                    'bg_color': layout.bg_color or [],
                    'bg_layouts': bg_layouts,
                    'themes': themes,
                })

            return self._json_response({
                'success': True,
                'data': layouts,
            })
        except Exception as e:
            _logger.exception('Error in get_layouts')
            return self._error_response(str(e), status=500)

    @http.route('/api/v1/photobooth/layouts_system', type='http',
                auth='public', methods=['GET'], csrf=False)
    def get_layouts_system(self, **kwargs):
        """GET /api/v1/photobooth/layouts_system - Get all layout system types with items."""
        try:
            LayoutSystemType = request.env['isd.photobooth.layout.system.type'].sudo()
            types = LayoutSystemType.search([])

            result = []
            for lst in types:
                items = []
                for item in lst.layout_system_ids:
                    items.append({
                        'id': item.id,
                        'sequence': item.sequence,
                        'name': item.name,
                        'x': item.x,
                        'y': item.y,
                        'width': item.width,
                        'height': item.height,
                        'is_qr': item.is_qr,
                    })

                result.append({
                    'id': lst.id,
                    'name': lst.name,
                    'is_cut': lst.is_cut,
                    'is_landscape': lst.is_landscape,
                    'print_height': lst.print_height,
                    'print_width': lst.print_width,
                    'actual_height': lst.actual_height,
                    'actual_width': lst.actual_width,
                    'viewbox_width': lst.viewbox_width,
                    'viewbox_height': lst.viewbox_height,
                    'dpi': lst.dpi,
                    'print_top': lst.print_top,
                    'print_left': lst.print_left,
                    'print_bottom': lst.print_bottom,
                    'print_right': lst.print_right,
                    'items': items,
                })

            return self._json_response({
                'success': True,
                'data': result,
            })
        except Exception as e:
            _logger.exception('Error in get_layouts_system')
            return self._error_response(str(e), status=500)

    # ==================================================================
    # Payment Flow API (Section 2.2)
    # ==================================================================

    @http.route('/api/v1/photobooth/<int:booth_id>/payments/calc', type='http',
                auth='public', methods=['POST'], csrf=False)
    def payments_calc(self, booth_id, **kwargs):
        """POST /api/v1/photobooth/<booth_id>/payments/calc - Calculate price."""
        try:
            booth, error = self._authenticate_booth(booth_id)
            if error:
                return error

            data = self._get_json_body()
            layout_id = data.get('layout_id')
            quantity = int(data.get('quantity', 1))
            promo_code = data.get('promo_code')

            if not layout_id:
                return self._error_response('layout_id is required')

            Layout = request.env['isd.photobooth.layout'].sudo()
            layout = Layout.browse(int(layout_id))
            if not layout.exists():
                return self._error_response('Layout not found', status=404)

            unit_price = layout.price
            subtotal = unit_price * quantity
            discount = 0.0

            # Apply promo code discount if provided
            if promo_code:
                discount = self._calculate_promo_discount(promo_code, subtotal, booth)

            total = max(subtotal - discount, 0)

            return self._json_response({
                'success': True,
                'data': {
                    'unit_price': unit_price,
                    'quantity': quantity,
                    'subtotal': subtotal,
                    'discount': discount,
                    'total': total,
                },
            })
        except Exception as e:
            _logger.exception('Error in payments_calc')
            return self._error_response(str(e), status=500)

    @http.route('/api/v1/photobooth/<int:booth_id>/payments/create', type='http',
                auth='public', methods=['POST'], csrf=False)
    def payments_create(self, booth_id, **kwargs):
        """POST /api/v1/photobooth/<booth_id>/payments/create - Create draft transaction."""
        try:
            booth, error = self._authenticate_booth(booth_id)
            if error:
                return error

            data = self._get_json_body()
            layout_id = data.get('layout_id')
            quantity = int(data.get('quantity', 1))
            payment_provider = data.get('payment_provider', 'cash')

            if not layout_id:
                return self._error_response('layout_id is required')

            Layout = request.env['isd.photobooth.layout'].sudo()
            layout = Layout.browse(int(layout_id))
            if not layout.exists():
                return self._error_response('Layout not found', status=404)

            valid_providers = ('cash', 'free', 'topup', 'transfer', 'fix', 'promotion')
            if payment_provider not in valid_providers:
                return self._error_response(
                    f'Invalid payment_provider. Must be one of: {", ".join(valid_providers)}')

            price = layout.price * quantity

            Transaction = request.env['isd.photobooth.transaction'].sudo()
            txn = Transaction.create({
                'photo_app_id': booth.id,
                'layout_id': layout.id,
                'price': price,
                'real_price': 0,
                'quantity': quantity,
                'status': 'draft',
                'payment_provider': payment_provider,
            })

            return self._json_response({
                'success': True,
                'data': {
                    'transaction_id': txn.transaction_id,
                    'payment_id': txn.id,
                    'price': price,
                    'status': txn.status,
                },
            })
        except Exception as e:
            _logger.exception('Error in payments_create')
            return self._error_response(str(e), status=500)

    @http.route('/api/v1/photobooth/<int:booth_id>/payments/pre_confirm', type='http',
                auth='public', methods=['POST'], csrf=False)
    def payments_pre_confirm(self, booth_id, **kwargs):
        """POST /api/v1/photobooth/<booth_id>/payments/pre_confirm - Pre-confirm payment."""
        try:
            booth, error = self._authenticate_booth(booth_id)
            if error:
                return error

            data = self._get_json_body()
            payment_id = data.get('payment_id')
            promo_code = data.get('promo_code')

            if not payment_id:
                return self._error_response('payment_id is required')

            Transaction = request.env['isd.photobooth.transaction'].sudo()
            txn = Transaction.browse(int(payment_id))
            if not txn.exists() or txn.photo_app_id.id != booth.id:
                return self._error_response('Transaction not found', status=404)

            if txn.status != 'draft':
                return self._error_response('Transaction is not in draft status')

            # Apply promo code if provided
            if promo_code:
                PromoCode = request.env['isd.photobooth.promo.code'].sudo()
                promo = PromoCode.search([('code', '=', promo_code)], limit=1)
                discount = self._calculate_promo_discount(promo_code, txn.price, booth)
                if discount > 0:
                    vals = {
                        'promotion_code': promo_code,
                        'price': max(txn.price - discount, 0),
                    }
                    if promo:
                        vals['promo_code_id'] = promo.id
                        promo.set_used()
                    txn.write(vals)

            return self._json_response({
                'success': True,
                'data': {
                    'payment_id': txn.id,
                    'transaction_id': txn.transaction_id,
                    'price': txn.price,
                    'status': 'pre_confirmed',
                },
            })
        except Exception as e:
            _logger.exception('Error in payments_pre_confirm')
            return self._error_response(str(e), status=500)

    @http.route('/api/v1/photobooth/<int:booth_id>/payments/confirm', type='http',
                auth='public', methods=['POST'], csrf=False)
    def payments_confirm(self, booth_id, **kwargs):
        """POST /api/v1/photobooth/<booth_id>/payments/confirm - Confirm payment."""
        try:
            booth, error = self._authenticate_booth(booth_id)
            if error:
                return error

            data = self._get_json_body()
            payment_id = data.get('payment_id')
            payment_provider = data.get('payment_provider')
            real_price = float(data.get('real_price', 0))

            if not payment_id:
                return self._error_response('payment_id is required')

            # Use DB-level lock to prevent concurrent confirmations
            request.env.cr.execute(
                "SELECT id FROM isd_photobooth_transaction WHERE id = %s FOR UPDATE NOWAIT",
                [int(payment_id)],
            )

            Transaction = request.env['isd.photobooth.transaction'].sudo()
            txn = Transaction.browse(int(payment_id))
            if not txn.exists() or txn.photo_app_id.id != booth.id:
                return self._error_response('Transaction not found', status=404)

            if txn.status == 'active':
                return self._error_response('Transaction already confirmed')

            vals = {}
            if payment_provider:
                valid_providers = ('cash', 'free', 'topup', 'transfer', 'fix', 'promotion')
                if payment_provider not in valid_providers:
                    return self._error_response('Invalid payment_provider')
                vals['payment_provider'] = payment_provider

            # Accumulate real_price
            vals['real_price'] = txn.real_price + real_price
            txn.write(vals)

            # Use model method to check and auto-activate
            txn.check_and_set_active()

            return self._json_response({
                'success': True,
                'data': {
                    'payment_id': txn.id,
                    'transaction_id': txn.transaction_id,
                    'status': txn.status,
                    'real_price': txn.real_price,
                    'price': txn.price,
                },
            })
        except Exception as e:
            _logger.exception('Error in payments_confirm')
            return self._error_response(str(e), status=500)

    @http.route('/api/v1/photobooth/<int:booth_id>/payments/<int:payment_id>/media_upload',
                type='http', auth='public', methods=['POST'], csrf=False)
    def media_upload(self, booth_id, payment_id, **kwargs):
        """POST /api/v1/photobooth/<booth_id>/payments/<payment_id>/media_upload - Upload media."""
        try:
            booth, error = self._authenticate_booth(booth_id)
            if error:
                return error

            Transaction = request.env['isd.photobooth.transaction'].sudo()
            txn = Transaction.browse(payment_id)
            if not txn.exists() or txn.photo_app_id.id != booth.id:
                return self._error_response('Transaction not found', status=404)

            # Collect uploaded files
            uploaded_urls = []
            files = request.httprequest.files.getlist('files')
            if not files:
                files = request.httprequest.files.getlist('file')

            Attachment = request.env['ir.attachment'].sudo()
            for f in files:
                file_data = f.read()
                attachment = Attachment.create({
                    'name': f.filename,
                    'datas': base64.b64encode(file_data),
                    'res_model': 'isd.photobooth.transaction',
                    'res_id': txn.id,
                    'type': 'binary',
                })
                url = '/web/content/%d/%s' % (attachment.id, f.filename)
                uploaded_urls.append(url)

            # Merge with existing medias
            existing = txn.medias or []
            all_urls = existing + uploaded_urls

            txn.update_medias(all_urls)

            return self._json_response({
                'success': True,
                'data': {
                    'payment_id': txn.id,
                    'medias': all_urls,
                    'medias_expired_at': txn.medias_expired_at,
                },
            })
        except Exception as e:
            _logger.exception('Error in media_upload')
            return self._error_response(str(e), status=500)

    @http.route('/api/v1/photobooth/<int:booth_id>/check_promo_code', type='http',
                auth='public', methods=['GET'], csrf=False)
    def check_promo_code(self, booth_id, **kwargs):
        """GET /api/v1/photobooth/<booth_id>/check_promo_code - Validate promo code."""
        try:
            booth, error = self._authenticate_booth(booth_id)
            if error:
                return error

            code = kwargs.get('code', '')
            if not code:
                return self._error_response('code parameter is required')

            # Try to find promo code in isd.photobooth.promo.code if model exists
            result = self._validate_promo_code(code, booth)

            return self._json_response({
                'success': True,
                'data': result,
            })
        except Exception as e:
            _logger.exception('Error in check_promo_code')
            return self._error_response(str(e), status=500)

    # ------------------------------------------------------------------
    # Promo helpers (will be expanded in Phase 3)
    # ------------------------------------------------------------------

    def _calculate_promo_discount(self, promo_code, subtotal, booth):
        """Calculate discount for a promo code. Returns discount amount."""
        PromoCode = request.env['isd.photobooth.promo.code'].sudo()
        promo = PromoCode.search([('code', '=', promo_code)], limit=1)
        if not promo or not promo.is_valid():
            return 0.0

        promotion = promo.promotion_id
        # Check group applicability
        if promotion.group_ids and booth.group_id and booth.group_id not in promotion.group_ids:
            return 0.0

        return promotion.get_price_off(subtotal)

    def _validate_promo_code(self, code, booth):
        """Validate a promo code and return discount info."""
        PromoCode = request.env['isd.photobooth.promo.code'].sudo()
        promo = PromoCode.search([('code', '=', code)], limit=1)
        if not promo:
            return {'valid': False, 'message': 'Promo code not found'}

        if not promo.is_valid():
            return {'valid': False, 'message': 'Promo code is invalid or expired'}

        promotion = promo.promotion_id
        # Check group applicability
        if promotion.group_ids and booth.group_id and booth.group_id not in promotion.group_ids:
            return {'valid': False, 'message': 'Promo code not applicable for this booth'}

        return {
            'valid': True,
            'code': code,
            'promotion_name': promotion.name,
            'type': promotion.type,
            'amount_off': promotion.amount_off or 0,
            'percent_off': promotion.percent_off or 0,
        }

    # ==================================================================
    # Photo Download Page (public, mobile-first)
    # ==================================================================

    def _classify_media_urls(self, urls):
        """Separate media URLs into png_images, jpg_images, and video_url."""
        png_images = []
        jpg_images = []
        video_url = None
        for url in (urls or []):
            lower = url.rsplit('.', 1)[-1].split('?')[0].lower() if '.' in url else ''
            if lower == 'png':
                png_images.append(url)
            elif lower in ('jpg', 'jpeg'):
                jpg_images.append(url)
            elif lower in ('mp4', 'webm', 'mov'):
                video_url = url
        return png_images, jpg_images, video_url

    @http.route('/photo-download/<string:transaction_id>', type='http',
                auth='public', methods=['GET'], csrf=False, website=False)
    def photo_download_page(self, transaction_id, **kwargs):
        """Public photo download page — QR code leads here."""
        if transaction_id == 'example':
            return request.render('isd_photobooth.photo_download_page', {
                'error': False,
                'error_type': False,
                'png_images': [
                    'https://picsum.photos/seed/pb1/400/600',
                    'https://picsum.photos/seed/pb2/400/600',
                ],
                'jpg_images': [
                    'https://picsum.photos/seed/pb3/400/600',
                ],
                'video_url': None,
                'transaction_id': 'example',
            })

        Transaction = request.env['isd.photobooth.transaction'].sudo()
        txn = Transaction.search([('transaction_id', '=', transaction_id)], limit=1)

        if not txn:
            return request.render('isd_photobooth.photo_download_page', {
                'error': 'Không tìm thấy giao dịch.',
                'error_type': 'not_found',
            })

        if txn.is_media_expired():
            return request.render('isd_photobooth.photo_download_page', {
                'error': 'Hình ảnh và video đã hết hạn.',
                'error_type': 'expired',
            })

        medias = txn.medias or []
        png_images, jpg_images, video_url = self._classify_media_urls(medias)

        return request.render('isd_photobooth.photo_download_page', {
            'error': False,
            'error_type': False,
            'png_images': png_images,
            'jpg_images': jpg_images,
            'video_url': video_url,
            'transaction_id': transaction_id,
        })

    @http.route('/api/v1/transactions/<string:transaction_id>/media_previews',
                type='http', auth='public', methods=['GET'], csrf=False)
    def media_previews_api(self, transaction_id, **kwargs):
        """GET /api/v1/transactions/<transaction_id>/media_previews — backward-compatible API."""
        Transaction = request.env['isd.photobooth.transaction'].sudo()
        txn = Transaction.search([('transaction_id', '=', transaction_id)], limit=1)

        if not txn:
            return self._error_response('Transaction not found', status=404)

        if not txn.medias:
            return self._error_response('No media found', status=404, code='media_not_found')

        if txn.is_media_expired():
            return self._error_response('Media expired', status=410, code='media_expired')

        png_images, jpg_images, video_url = self._classify_media_urls(txn.medias)

        return self._json_response({
            'image_urls': png_images + jpg_images,
            'video_url': video_url,
        })
