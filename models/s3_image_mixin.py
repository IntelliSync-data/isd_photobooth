# -*- coding: utf-8 -*-

import base64
import logging
import mimetypes

_logger = logging.getLogger(__name__)


def upload_binary_fields_to_s3(env, vals, field_map):
    """Upload binary image data from vals to S3 and set URL fields.

    Args:
        env: Odoo environment.
        vals: dict of field values being written.
        field_map: dict mapping binary_field_name -> url_field_name.

    Returns:
        vals dict with url fields populated.
    """
    from odoo.addons.isd_photobooth.services import PhotoboothS3Service
    s3 = PhotoboothS3Service(env)
    if not s3.is_configured():
        return vals

    for binary_field, url_field in field_map.items():
        if binary_field not in vals or not vals[binary_field]:
            continue
        try:
            data = vals[binary_field]
            if isinstance(data, str):
                data = base64.b64decode(data)

            filename_field = f'{binary_field}_filename'
            filename = vals.get(filename_field, f'{binary_field}.png')
            mime = mimetypes.guess_type(filename)[0] or 'image/png'

            url = s3.upload_asset(data, filename, mime)
            vals[url_field] = url
            _logger.info("S3 auto-upload: %s -> %s", binary_field, url)
        except Exception:
            _logger.exception("S3 auto-upload failed for field %s", binary_field)

    return vals
