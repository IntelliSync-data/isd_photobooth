/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, xml } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class ApiReferenceAction extends Component {
    static template = xml`
        <div class="o_action container-fluid py-4">
            <div class="row">
                <div class="col-12">
                    <h2 class="mb-4">PhotoBooth API Reference</h2>
                    <p class="text-muted mb-4">
                        API endpoints for C# PhotoBooth desktop application.
                        All booth-specific endpoints require <code>x-api-token</code> header matching the booth code.
                    </p>

                    <!-- Booth App API -->
                    <div class="card mb-4">
                        <div class="card-header bg-primary text-white">
                            <h4 class="mb-0">Booth App API</h4>
                        </div>
                        <div class="card-body p-0">
                            <table class="table table-striped table-hover mb-0">
                                <thead>
                                    <tr>
                                        <th style="width:100px">Method</th>
                                        <th style="width:420px">Endpoint</th>
                                        <th>Description</th>
                                        <th style="width:120px">Auth</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><span class="badge text-bg-success">POST</span></td>
                                        <td><code>/api/v1/photobooth/setup</code></td>
                                        <td>Register a new booth. Body: <code>{"name", "group_code"}</code></td>
                                        <td><span class="badge text-bg-secondary">Public</span></td>
                                    </tr>
                                    <tr>
                                        <td><span class="badge text-bg-info">GET</span></td>
                                        <td><code>/api/v1/photobooth/check_version?version=x.x.x</code></td>
                                        <td>Check if app version is latest. Returns latest version, package_url, notes</td>
                                        <td><span class="badge text-bg-secondary">Public</span></td>
                                    </tr>
                                    <tr>
                                        <td><span class="badge text-bg-success">POST</span></td>
                                        <td><code>/api/v1/photobooth/<![CDATA[{booth_id}]]>/ping</code></td>
                                        <td>Health check + send hardware status (printer, camera, bill_acceptor)</td>
                                        <td><span class="badge text-bg-warning">x-api-token</span></td>
                                    </tr>
                                    <tr>
                                        <td><span class="badge text-bg-info">GET</span></td>
                                        <td><code>/api/v1/photobooth/<![CDATA[{booth_id}]]>/info</code></td>
                                        <td>Get booth config: payment methods, media types, layouts, themes</td>
                                        <td><span class="badge text-bg-warning">x-api-token</span></td>
                                    </tr>
                                    <tr>
                                        <td><span class="badge text-bg-info">GET</span></td>
                                        <td><code>/api/v1/photobooth/<![CDATA[{booth_id}]]>/layouts</code></td>
                                        <td>Get all layouts for booth with backgrounds and themes</td>
                                        <td><span class="badge text-bg-warning">x-api-token</span></td>
                                    </tr>
                                    <tr>
                                        <td><span class="badge text-bg-info">GET</span></td>
                                        <td><code>/api/v1/photobooth/layouts_system</code></td>
                                        <td>Get all layout system types with print dimensions and photo positions</td>
                                        <td><span class="badge text-bg-secondary">Public</span></td>
                                    </tr>
                                    <tr>
                                        <td><span class="badge text-bg-info">GET</span></td>
                                        <td><code>/api/v1/photobooth/<![CDATA[{booth_id}]]>/check_promo_code?code=XXX</code></td>
                                        <td>Validate promo code. Returns valid, discount info</td>
                                        <td><span class="badge text-bg-warning">x-api-token</span></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Payment Flow API -->
                    <div class="card mb-4">
                        <div class="card-header bg-success text-white">
                            <h4 class="mb-0">Payment Flow API</h4>
                        </div>
                        <div class="card-body p-0">
                            <table class="table table-striped table-hover mb-0">
                                <thead>
                                    <tr>
                                        <th style="width:100px">Method</th>
                                        <th style="width:420px">Endpoint</th>
                                        <th>Description</th>
                                        <th style="width:120px">Auth</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><span class="badge text-bg-success">POST</span></td>
                                        <td><code>/api/v1/photobooth/<![CDATA[{booth_id}]]>/payments/calc</code></td>
                                        <td>Calculate price. Body: <code>{"layout_id", "quantity", "promo_code"}</code></td>
                                        <td><span class="badge text-bg-warning">x-api-token</span></td>
                                    </tr>
                                    <tr>
                                        <td><span class="badge text-bg-success">POST</span></td>
                                        <td><code>/api/v1/photobooth/<![CDATA[{booth_id}]]>/payments/create</code></td>
                                        <td>Create draft transaction. Body: <code>{"layout_id", "quantity", "payment_provider"}</code></td>
                                        <td><span class="badge text-bg-warning">x-api-token</span></td>
                                    </tr>
                                    <tr>
                                        <td><span class="badge text-bg-success">POST</span></td>
                                        <td><code>/api/v1/photobooth/<![CDATA[{booth_id}]]>/payments/pre_confirm</code></td>
                                        <td>Pre-confirm with optional promo code. Body: <code>{"payment_id", "promo_code"}</code></td>
                                        <td><span class="badge text-bg-warning">x-api-token</span></td>
                                    </tr>
                                    <tr>
                                        <td><span class="badge text-bg-success">POST</span></td>
                                        <td><code>/api/v1/photobooth/<![CDATA[{booth_id}]]>/payments/confirm</code></td>
                                        <td>Confirm payment (DB lock). Body: <code>{"payment_id", "payment_provider", "real_price"}</code></td>
                                        <td><span class="badge text-bg-warning">x-api-token</span></td>
                                    </tr>
                                    <tr>
                                        <td><span class="badge text-bg-success">POST</span></td>
                                        <td><code>/api/v1/photobooth/<![CDATA[{booth_id}]]>/payments/<![CDATA[{payment_id}]]>/media_upload</code></td>
                                        <td>Upload images/video. Multipart: <code>files[]</code>. Auto-expire 3 days</td>
                                        <td><span class="badge text-bg-warning">x-api-token</span></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Payment Flow Sequence -->
                    <div class="card mb-4">
                        <div class="card-header bg-dark text-white">
                            <h4 class="mb-0">Payment Flow Sequence</h4>
                        </div>
                        <div class="card-body">
                            <div class="d-flex align-items-center flex-wrap gap-2">
                                <span class="badge text-bg-primary p-2 fs-6">1. /payments/calc</span>
                                <i class="fa fa-arrow-right text-muted"/>
                                <span class="badge text-bg-primary p-2 fs-6">2. /payments/create</span>
                                <i class="fa fa-arrow-right text-muted"/>
                                <span class="badge text-bg-primary p-2 fs-6">3. /payments/pre_confirm</span>
                                <i class="fa fa-arrow-right text-muted"/>
                                <span class="badge text-bg-secondary p-2 fs-6">4. User pays</span>
                                <i class="fa fa-arrow-right text-muted"/>
                                <span class="badge text-bg-primary p-2 fs-6">5. /payments/confirm</span>
                                <i class="fa fa-arrow-right text-muted"/>
                                <span class="badge text-bg-primary p-2 fs-6">6. /media_upload</span>
                            </div>
                            <hr/>
                            <div>
                                <strong>payment_provider values:</strong>
                                <span class="badge text-bg-light text-dark border mx-1">cash</span>
                                <span class="badge text-bg-light text-dark border mx-1">free</span>
                                <span class="badge text-bg-light text-dark border mx-1">topup</span>
                                <span class="badge text-bg-light text-dark border mx-1">transfer</span>
                                <span class="badge text-bg-light text-dark border mx-1">fix</span>
                                <span class="badge text-bg-light text-dark border mx-1">promotion</span>
                            </div>
                            <div class="mt-2">
                                <strong>Auto-activate rules:</strong>
                                <ul class="mb-0 mt-1">
                                    <li><code>free</code> / <code>promotion</code> — activate immediately</li>
                                    <li><code>cash</code> / <code>topup</code> / <code>transfer</code> / <code>fix</code> — activate when <code>real_price &gt;= price</code></li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <!-- Authentication -->
                    <div class="card mb-4">
                        <div class="card-header bg-warning">
                            <h4 class="mb-0">Authentication</h4>
                        </div>
                        <div class="card-body">
                            <p>Booth-specific endpoints require the <code>x-api-token</code> HTTP header with the booth code:</p>
                            <pre class="bg-light p-3 rounded border"><code>curl -X GET \
  https://your-odoo.com/api/v1/photobooth/123/info \
  -H "x-api-token: A1B2C3D4E5F6"</code></pre>
                            <p class="text-muted mb-0">
                                The booth code is auto-generated on creation and visible in the Photo Booth form view.
                            </p>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    `;
}

registry.category("actions").add("isd_photobooth.api_reference", ApiReferenceAction);
