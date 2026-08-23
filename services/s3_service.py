# -*- coding: utf-8 -*-

import hashlib
import logging
import os
import time
import uuid

_logger = logging.getLogger(__name__)

_PARAM_PREFIX = 'isd_photobooth.s3_'
_MEDIA_PARAM_PREFIX = 'isd_media.s3_'


def _p(env, key, default=''):
    ICP = env['ir.config_parameter'].sudo()
    val = ICP.get_param(f'{_PARAM_PREFIX}{key}', '').strip()
    if val:
        return val
    return ICP.get_param(f'{_MEDIA_PARAM_PREFIX}{key}', default).strip()


class PhotoboothS3Service:
    """S3 service for isd_photobooth media uploads.

    Reads config from isd_photobooth.s3_* params first, falls back to
    isd_media.s3_* params so the module works standalone or alongside isd_media.
    """

    def __init__(self, env):
        self.env = env

    def _get_client(self):
        import boto3
        from botocore.config import Config as BotoConfig

        endpoint_url = _p(self.env, 'endpoint_url')
        use_ssl = _p(self.env, 'use_ssl', 'True') == 'True'

        kwargs = {
            'aws_access_key_id': _p(self.env, 'access_key'),
            'aws_secret_access_key': _p(self.env, 'secret_key'),
            'region_name': _p(self.env, 'region'),
            'use_ssl': use_ssl,
            'config': BotoConfig(
                signature_version='s3v4',
                s3={'payload_signing_enabled': False},
                connect_timeout=60,
                read_timeout=300,
                retries={'max_attempts': 5},
            ),
        }
        if endpoint_url:
            kwargs['endpoint_url'] = endpoint_url
        return boto3.client('s3', **kwargs)

    def _get_bucket(self):
        return _p(self.env, 'bucket_name')

    def _is_aws(self):
        return 'amazonaws.com' in _p(self.env, 'endpoint_url', '')

    def _build_url(self, key):
        public_base = _p(self.env, 'public_base_url')
        if public_base:
            return f"{public_base.rstrip('/')}/{key}"
        bucket = self._get_bucket()
        region = _p(self.env, 'region')
        endpoint_url = _p(self.env, 'endpoint_url')
        if endpoint_url and self._is_aws():
            return f"{endpoint_url.rstrip('/')}/{key}"
        if endpoint_url:
            return f"{endpoint_url.rstrip('/')}/{bucket}/{key}"
        return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

    @staticmethod
    def _generate_key(prefix, file_name):
        ext = os.path.splitext(file_name)[1].lower() or ''
        uid = uuid.uuid4().hex[:8]
        ts = str(time.time()).encode()
        name_hash = hashlib.sha256(ts + file_name.encode()).hexdigest()[:12]
        return f"{prefix}/{ext.lstrip('.')}/{name_hash}_{uid}{ext}"

    def upload_media(self, file_data, file_name, mime_type, expires_in=None):
        """Upload a file to S3.

        Args:
            file_data: Raw file bytes.
            file_name: Original file name.
            mime_type: MIME type string.
            expires_in: Seconds until auto-expiry. When set, the key is
                        prefixed with ``temp/`` and the object is tagged
                        ``auto-expire=true``.

        Returns:
            str: Public URL of the uploaded file.
        """
        import io
        client = self._get_client()
        bucket = self._get_bucket()

        if expires_in:
            key = self._generate_key('temp/transactions/media', file_name)
        else:
            key = self._generate_key('media', file_name)

        extra_args = {
            'ContentType': mime_type,
            'ACL': 'public-read',
        }

        if expires_in:
            from datetime import datetime, timedelta, timezone
            extra_args['Expires'] = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            extra_args['Tagging'] = 'auto-expire=true'

        client.upload_fileobj(io.BytesIO(file_data), bucket, key, ExtraArgs=extra_args)
        url = self._build_url(key)
        _logger.info(
            "Photobooth S3: uploaded %s (%s, %d bytes, expires_in=%s)",
            key, mime_type, len(file_data), expires_in,
        )
        return url

    def upload_transaction_media(self, file_data, file_name, mime_type):
        """Upload transaction media with 3-day expiry."""
        return self.upload_media(file_data, file_name, mime_type, expires_in=60 * 60 * 24 * 3)

    def upload_asset(self, file_data, file_name, mime_type):
        """Upload a permanent asset (backgrounds, layouts, etc.)."""
        return self.upload_media(file_data, file_name, mime_type, expires_in=None)

    def delete(self, url):
        """Delete a file from S3 by its public URL."""
        key = self._url_to_key(url)
        if not key:
            return
        client = self._get_client()
        bucket = self._get_bucket()
        client.delete_object(Bucket=bucket, Key=key)
        _logger.info("Photobooth S3: deleted %s", key)

    def _url_to_key(self, url):
        public_base = _p(self.env, 'public_base_url')
        if public_base and url.startswith(public_base):
            return url[len(public_base.rstrip('/')):].lstrip('/')
        bucket = self._get_bucket()
        markers = [f'/{bucket}/', '.amazonaws.com/']
        for marker in markers:
            idx = url.find(marker)
            if idx != -1:
                return url[idx + len(marker):]
        return None

    def is_configured(self):
        """Check if S3 is configured (at least bucket and access key present)."""
        return bool(_p(self.env, 'bucket_name') and _p(self.env, 'access_key'))
