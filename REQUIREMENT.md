# isd_photobooth - Requirement Document

> Module Odoo 18 Community - Photo Booth Management System
> Migrated from: PJ_PhotoApp (FastAPI backend + React frontend + C#/WPF app)
> Created: 2026-08-20

---

## Phase 1: Core Models + Views + Security

### 1.1 Group / Location (`isd.photobooth.group`)
- [ ] Model: name, address, active
- [ ] Many2many: managed_users (res.users)
- [ ] Views: list, form, search
- [ ] Soft delete (deleted_at)

### 1.2 Photo Booth (`isd.photobooth`)
- [ ] Model fields:
  - [ ] name, code (unique, auto-gen snowflake)
  - [ ] status: Selection (not_yet / installed)
  - [ ] background (image URL)
  - [ ] font_color
  - [ ] payment_method: JSON/Selection multi (cash, free, transfer)
  - [ ] download_media_type: JSON/Selection multi (image, original_images, video)
  - [ ] max_prints (integer)
  - [ ] printer_paper_count (integer)
  - [ ] config_photo_app (JSON/Text - UI theme config: 20+ color/bg properties, camera labels, icons, bank info, ads URL)
  - [ ] group_id: Many2one -> isd.photobooth.group
  - [ ] last_meta_updated_at (datetime)
  - [ ] hardware_health_data (JSON - printer, camera, bill_acceptor status)
  - [ ] active, deleted_at
- [ ] Many2many: layout_ids (isd.photobooth.layout) - ordered
- [ ] Many2many: theme_ids (isd.photobooth.theme) - ordered
- [ ] One2many: layout_system_type_ids (isd.photobooth.layout.system.type)
- [ ] Methods:
  - [ ] install() - mark as installed
  - [ ] gen_code() - generate unique code
  - [ ] clone() - clone with layouts, themes, layout system types
  - [ ] initialize_default_layouts() - create 10 built-in layout system types
  - [ ] reset_printer_count() / set_printer_count()
- [ ] Views: list, form (with notebook tabs), search
- [ ] Action: clone button, initialize layouts button

### 1.3 Layout (`isd.photobooth.layout`)
- [ ] Model fields:
  - [ ] name, description, price (Float)
  - [ ] image_url (Char) or image (Binary)
  - [ ] frame_type: Selection (vertical / horizontal / 1:1)
  - [ ] layout_type: Selection (2x2h, 2x2v, 1x4h, 3x1h, 2x4h, 1vs3h, 1x1v, 1x2v, 2x3square, 1x3square)
  - [ ] bg_color: JSON (list of colors)
  - [ ] paper_size (Char)
- [ ] Many2many: bg_layout_ids (isd.photobooth.background) - ordered
- [ ] Many2many: photo_app_ids (isd.photobooth) - ordered
- [ ] One2many: layout_theme_ids (isd.photobooth.layout.theme)
- [ ] Methods:
  - [ ] clone() - clone layout with dependencies
- [ ] Views: list, form, search

### 1.4 Layout System Type - Print Config (`isd.photobooth.layout.system.type`)
- [ ] Model fields:
  - [ ] name
  - [ ] isCutted (Boolean)
  - [ ] isLandscape (Boolean)
  - [ ] printHeight, printWidth (Float)
  - [ ] actualHeight, actualWidth (Float)
  - [ ] viewBoxWidth, viewBoxHeight (Float)
  - [ ] dpi (Integer)
  - [ ] print_top, print_left, print_bottom, print_right (Float - margins)
  - [ ] photo_app_id: Many2one -> isd.photobooth
- [ ] One2many: layout_system_ids (isd.photobooth.layout.system)
- [ ] Views: list, form
- [ ] Bulk update margins action

### 1.5 Layout System - Layout Items (`isd.photobooth.layout.system`)
- [ ] Model fields:
  - [ ] layout_system_type_id: Many2one -> isd.photobooth.layout.system.type
  - [ ] no (Integer - order)
  - [ ] name
  - [ ] x, y (Float - position)
  - [ ] width, height (Float)
  - [ ] is_qr (Boolean)
- [ ] Views: inline list in layout system type form

### 1.6 Theme (`isd.photobooth.theme`)
- [ ] Model fields:
  - [ ] name
  - [ ] background (Image/Binary or URL)
- [ ] Many2many: photo_app_ids (isd.photobooth) - ordered
- [ ] Views: list, form

### 1.7 Background Layout (`isd.photobooth.background`)
- [ ] Model fields:
  - [ ] frame_type: Selection (vertical / horizontal / 1:1)
  - [ ] image_url (Char) or image (Binary)
- [ ] Many2many: layout_ids (isd.photobooth.layout)
- [ ] Views: list, form

### 1.8 Layout Theme (`isd.photobooth.layout.theme`)
- [ ] Model fields:
  - [ ] theme_id: Many2one -> isd.photobooth.theme
  - [ ] layout_id: Many2one -> isd.photobooth.layout
  - [ ] SQL unique constraint (theme_id, layout_id)
- [ ] Many2many: bg_layout_ids (isd.photobooth.background)
- [ ] Views: inline in layout form

### 1.9 Security
- [ ] Groups: isd_photobooth_super_admin, isd_photobooth_franchise, isd_photobooth_staff
- [ ] Record rules:
  - [ ] Super admin: see all
  - [ ] Franchise: see booths/transactions in assigned groups
  - [ ] Staff: see booths/transactions in assigned groups (limited permissions)
- [ ] ir.model.access.csv for all models
- [ ] 13 permission types: statistics, users, transactions (view/edit/delete), photo_apps, layouts, bg_layouts, groups, tickets, theme_types, app_versions, promotions

### 1.10 Menu
- [ ] Root menu: "ISD PhotoBooth"
- [ ] Sub menus: Dashboard, Photo Booths, Layouts, Themes, Backgrounds, Groups, Transactions, Promotions, Tickets, Audit Log, Configuration

---

## Phase 2: Transaction + Payment Flow API

### 2.1 Transaction (`isd.photobooth.transaction`)
- [ ] Model fields:
  - [ ] transaction_id (Char - snowflake, unique)
  - [ ] photo_app_id: Many2one -> isd.photobooth
  - [ ] layout_id: Many2one -> isd.photobooth.layout
  - [ ] price (Float)
  - [ ] real_price (Float - actual amount received, accumulated)
  - [ ] quantity (Integer)
  - [ ] status: Selection (draft / active)
  - [ ] date (Datetime)
  - [ ] payment_provider: Selection (cash / free / topup / transfer / fix / promotion)
  - [ ] medias (JSON - list of media URLs)
  - [ ] medias_expired_at (Datetime - 3 days after upload)
  - [ ] promotion_code (Char)
  - [ ] promo_code_id: Many2one -> isd.photobooth.promo.code
  - [ ] deleted_on (Datetime - soft delete)
- [ ] Methods:
  - [ ] set_active()
  - [ ] update_real_price() - accumulate
  - [ ] update_medias()
  - [ ] is_media_expired()
  - [ ] check_and_set_active()
- [ ] Views: list (with filters), form, search
- [ ] Export CSV action
- [ ] Audit history view

### 2.2 Payment Flow API (JSON/HTTP controllers)
- [ ] `POST /api/v1/photobooth/{booth_id}/payments/calc` - Calculate price
  - Input: layout_id, quantity, promo_code (optional)
  - Output: price, discount, total
- [ ] `POST /api/v1/photobooth/{booth_id}/payments/create` - Create draft transaction
  - Input: layout_id, quantity, payment_provider
  - Output: transaction_id, payment_id
- [ ] `POST /api/v1/photobooth/{booth_id}/payments/pre_confirm` - Pre-confirm
  - Input: payment_id, promo_code (optional)
  - Output: validation result
- [ ] `POST /api/v1/photobooth/{booth_id}/payments/confirm` - Confirm payment
  - Input: payment_id, payment_provider, real_price
  - Output: transaction status
  - Note: Use distributed lock (or DB lock) to prevent concurrent confirmations
- [ ] `POST /api/v1/photobooth/{booth_id}/payments/{payment_id}/media_upload` - Upload media
  - Input: images (multiple), video (optional)
  - Output: media URLs

### 2.3 Booth App API (Public endpoints for C# app)
- [ ] `POST /api/v1/photobooth/setup` - Register new booth
- [ ] `GET /api/v1/photobooth/check_version` - Check app version
- [ ] `POST /api/v1/photobooth/{booth_id}/ping` - Health check + hardware status
- [ ] `GET /api/v1/photobooth/{booth_id}/info` - Get booth config
- [ ] `GET /api/v1/photobooth/{booth_id}/layouts` - Get layouts for booth
- [ ] `GET /api/v1/photobooth/layouts_system` - Get all layout system types
- [ ] `GET /api/v1/photobooth/{booth_id}/check_promo_code` - Validate promo code

---

## Phase 3: Promotion / Voucher + Promo Code

### 3.1 Promotion (`isd.photobooth.promotion`)
- [ ] Model fields:
  - [ ] name
  - [ ] type: Selection (voucher / coupon)
  - [ ] num_of_codes (Integer)
  - [ ] used_count (Integer)
  - [ ] status: Selection (active / deactive)
  - [ ] amount_off (Float - fixed discount for voucher)
  - [ ] percent_off (Float - % discount for coupon)
  - [ ] start_date, end_date (Date)
  - [ ] deleted_on (Datetime - soft delete)
- [ ] Many2many: group_ids (isd.photobooth.group) - applicable groups
- [ ] One2many: promo_code_ids (isd.photobooth.promo.code)
- [ ] Methods:
  - [ ] get_price_off(original_price) - calculate discount
  - [ ] use_promo_code() - increment used_count
  - [ ] is_active() - check status + date range
- [ ] Views: list, form, search
- [ ] Button: Generate promo codes

### 3.2 Promo Code (`isd.photobooth.promo.code`)
- [ ] Model fields:
  - [ ] code (Char, unique)
  - [ ] promotion_id: Many2one -> isd.photobooth.promotion
  - [ ] status: Selection (used / unused)
  - [ ] used_time (Datetime)
  - [ ] deleted_on (Datetime - soft delete)
- [ ] Methods:
  - [ ] set_used()
  - [ ] is_valid() - check unused + promotion active + date range
- [ ] Views: list (inline in promotion form), search
- [ ] Export CSV action

---

## Phase 4: Statistics / Analytics + Audit Log

### 4.1 Statistics Dashboard
- [ ] Dashboard view with:
  - [ ] Total transactions count
  - [ ] Total revenue (price)
  - [ ] Total received (real_price)
  - [ ] Breakdown by date, group, photo app
  - [ ] Charts (bar, line)
- [ ] Filters: date range, group_ids, photo_app_ids
- [ ] Group statistics view with pagination
- [ ] Export CSV (hierarchical: date/group/app)

### 4.2 Audit Log (`isd.photobooth.audit.log`)
- [ ] Model fields:
  - [ ] model_name (Char)
  - [ ] model_id (Integer)
  - [ ] action (Char - create/update/delete)
  - [ ] user_id: Many2one -> res.users
  - [ ] timestamp (Datetime)
  - [ ] data (JSON - previous_state, current_state, changes, action_details)
  - [ ] source: Selection (portal / photobooth)
- [ ] Views: list, form (readonly), search
- [ ] Filters: date range, model, action, source, user
- [ ] Auto-create on PhotoBooth/Transaction changes (override create/write/unlink)

---

## Phase 5: Ticket + App Version + Config

### 5.1 Support Ticket (`isd.photobooth.ticket`)
- [ ] Model fields:
  - [ ] subject
  - [ ] description (Text)
  - [ ] status: Selection (created / received / in_progress / responded / completed)
  - [ ] image_ids: Many2many (ir.attachment)
  - [ ] created_by_id: Many2one -> res.users
  - [ ] assigned_to_id: Many2one -> res.users
- [ ] Views: list, form, search
- [ ] Mail integration (mail.thread)
- [ ] Public API: Create ticket from C# app

### 5.2 App Version (`isd.photobooth.app.version`)
- [ ] Model fields:
  - [ ] version (Char)
  - [ ] package_url (Char - download URL)
  - [ ] status: Selection (enabled / disabled)
- [ ] Views: list, form
- [ ] API: Check version endpoint

### 5.3 Configuration (res.config.settings)
- [ ] Dashboard stats: total booths, total transactions, total revenue
- [ ] Default settings
- [ ] S3/storage config (reuse isd_media if possible)

---

## Data Migration Notes

- Current backend: FastAPI + PostgreSQL
- Current frontend: React + Ant Design
- C# app calls backend API -> after migration, C# app will call Odoo API
- API endpoints should maintain similar structure for minimal C# app changes
- Snowflake IDs: consider using Odoo sequence or UUID
- JSON fields: use Odoo Text fields with JSON serialization or Serialized fields
- Media storage: reuse isd_media module's S3/local storage
- Payment integration: reuse isd_payment module for QR payment (SePay, ACB Pay)

---

## Dependencies

- `base`, `base_setup`
- `mail` (for tickets with chatter)
- `isd_media` (optional - for storage provider)
- `isd_payment` (optional - for payment gateway integration)

---

## Progress Tracking

| Phase | Status | Date Started | Date Completed |
|-------|--------|-------------|----------------|
| Phase 1: Core Models | Done | 2026-08-20 | 2026-08-20 |
| Phase 2: Transaction + API | Done | 2026-08-20 | 2026-08-20 |
| Phase 3: Promotion | Done | 2026-08-20 | 2026-08-20 |
| Phase 4: Analytics + Audit | Done | 2026-08-20 | 2026-08-20 |
| Phase 5: Ticket + Version | Done | 2026-08-20 | 2026-08-20 |
