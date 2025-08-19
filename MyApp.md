
You are an expert full-stack engineer and DevOps specialist. Build a production-ready, minimal viable product (MVP) for a SaaS invoicing/quoting/receipting product called **Pixel Crafte Billing**. The user/company running this service is **Pixel Crafte** (a web design, graphic design & Software Development studio). This MVP should be conservative on resources so it can run on a cheap VPS (1–2 vCPU, 2–4GB RAM) and later be easy to scale.

Below are the complete requirements. Produce a Git repository (or repo structure), runnable instructions, code, tests, configuration, and deployment docs. Provide concise explanations for any architectural choices you make.

---

# 1 — Goal

Deliver a Django-based web application (server-rendered templates + Postgres) that enables companies to:

* Create and manage clients.
* Create quotes, invoices, and receipts.
* Generate PDF versions of quotes/invoices/receipts from HTML templates.
* Allow users to download PDFs (PDFs are ephemeral: generated for download then deleted minutes after).
* Persist transactional metadata and versioned invoice data in the database so any invoice can be regenerated deterministically.
* Support per-company theming (colors, font family, logo) at runtime without rebuilding CSS.
* Provide simple status tracking (draft, sent, viewed, paid, overdue).
* Be easily extendable later (payments, reporting, separate frontend, microservices).

---

# 2 — Tech stack (MVP)

* Backend: **Django** (latest stable), Django templates, Django ORM
* DB: **PostgreSQL**
* Styling: **Tailwind CSS** (Tailwind CLI)
* Frontend small interactivity: **htmx** + **Alpine.js**
* PDF generation: **WeasyPrint** (preferred) or **ReportLab** (fallback)
* Process management: **Gunicorn** + **Nginx** reverse proxy
* Optional for background jobs: **Celery + Redis** (provide as optional docker-compose service; background tasks should be implemented as management commands if Celery is not used)
* Authentication: Django sessions (HTTP-only cookies)
* Storage: local media for now; design to use `django-storages` + S3 later
* Dev tooling: `python3-venv`, `pip`, `node` for Tailwind
* Containerization: provide **Dockerfile** + **docker-compose.yml** (optional) for dev parity; production deploy instructions should include non-Docker VPS steps
* Testing: Django unit tests and simple integration tests (pytest optional)

---

# 3 — Multi-tenant / Company model

* Single-DB, multi-tenant by Company (not full SaaS isolation). Each Company has:

  * `name`, `slug`, `logo` (ImageField), `primary_color` (hex), `accent_color` (hex), `font_family`, `timezone`, `currency`, `address`, `tax_info`, `default_terms`, `invoice_prefix` (e.g. PCF-).
* Users belong to a Company (`ForeignKey`) and have roles: `owner`, `admin`, `accountant`, `user`.
* A context processor (or middleware) must populate `request.company` for templates and theming.
* For initial MVP, tenant scoping is enforced at the application layer. Ensure queries use company filter.

---

# 4 — Models (must include)

Provide Django model classes with migrations for:

1. **Company**

   * fields listed above

2. **User** (extend `AbstractUser` or use a `Profile` model) with `company` and `role`.

3. **Client**

   * `company` FK, `name`, `email`, `phone`, `billing_address`, `shipping_address`, `tax_id`, `notes`

4. **InvoiceTemplate** (optional, for future templating)

   * `company`, `name`, `html_template` (TextField), `is_default`

5. **Invoice**

   * `company`, `client`, `created_by`, `number` (auto-generated per company), `status` (choices: DRAFT, SENT, VIEWED, PARTIALLY\_PAID, PAID, OVERDUE), `issue_date`, `due_date`, `notes`, `currency`, `tax_rate`, `subtotal`, `tax_total`, `total`, `metadata` (JSONField), `is_deleted` flag, `versioned_data` (JSONField) — versioned snapshot of line items and company branding at time of generation

6. **InvoiceLineItem**

   * `invoice`, `description`, `quantity`, `unit_price`, `discount`, `line_total`

7. **Quote** (similar to Invoice but separate model or single model with `type`): keep as separate model for clarity

8. **Receipt**

   * `invoice` FK (nullable), `company`, `client`, `amount`, `payment_method`, `received_at`, `notes`

9. **PDFLog** (or DocumentRecord)

   * `company`, `invoice`/`quote`/`receipt` FK, `file_path` (if temporarily stored), `created_at`, `expires_at`, `download_token` (secure unique token), `deleted` flag

10. **AuditLog** (basic): record user actions for accountability (create invoice, send, generate PDF)

---

# 5 — Functional flows (end to end)

For each flow produce UI templates and backend endpoints / views.

### 5.1 — Create invoice (web page)

* Form for invoice header, line items add/remove (JS-friendly), tax, notes, client selector or quick-create client inline.
* When saving: save `Invoice` (status DRAFT).
* Provide “Preview” button that renders invoice HTML (not yet PDF) in a modal (htmx-based partial).

### 5.2 — Generate PDF & Download

* When user clicks “Download PDF”:

  1. Server renders HTML using a locked `invoice_pdf.html` template with the `invoice.versioned_data` and `company` branding values.
  2. WeasyPrint returns PDF binary. Save PDF temporarily to disk or stream.
  3. Create `PDFLog` record with `download_token` and `expires_at = now + 5 minutes` (configurable).
  4. Return a secure URL (containing token) to the frontend for download.
  5. A background cleanup job (or scheduled management command) removes expired PDF files and sets `deleted=True`. Also ensure immediate deletion a short time after download (e.g., set a hook to delete after successful download).
* Important constraint: **PDF files cannot be stored indefinitely**. Ensure logs & DB metadata store enough info to regenerate deterministically.

### 5.3 — Sending invoice by email

* Provide a “Send” action that emails the client with a link to view the invoice (no login required if you choose to implement a signed view link). Record status `SENT` and timestamp.
* Email template should be adjustable per company.

### 5.4 — Regenerate invoice

* Given the invoice record, use `versioned_data` and company settings to re-render an identical PDF.

### 5.5 — Status updates

* Track `VIEWED` status when client visits signed view link (collect user-agent + IP) — optional for MVP but recommended.
* Allow manual marking as `PAID` and record `Receipt`.

---

# 6 — Theming & Runtime brand customization

* Use CSS variables injected at runtime (inline `<style>` in `<head>`) set from `Company` settings (prefer RGB components to allow alpha handling with tailwind config).
* Tailwind config should map CSS variables to utility colors using:

  ```
  colors: {
    primary: 'rgb(var(--primary-r) / <alpha-value>)'
  }
  ```
* Provide a `theme_context_processor` that converts company hex colors to `r,g,b` strings (helper function).
* Fonts: allow `company.font_family` to be used by injecting `--font-family` CSS var. Support self-hosted `.woff2` fonts by saving font files under `media/fonts/<company>/...` and referencing absolute URLs in PDF generator.
* Logo: `company.logo.url` used in invoice header.
* Provide an admin UI (Django admin or settings page) for companies to set brand colors and test preview.

---

# 7 — UI/UX guidelines & templates

* Create a minimal, clean UI inspired by modern SaaS pricing/invoice panels (use Tailwind).
* Provide the following pages:

  * Dashboard (list of invoices, quick create)
  * Company settings (branding)
  * Clients list & client detail
  * Invoice list & invoice detail (view/preview/send/download)
  * Quote list & quote detail
  * Receipt list
  * Simple landing & auth pages (login/signup)
* Use accessible markup; ensure invoice PDF template matches on-screen HTML.

---

# 8 — Auth, roles, security

* Use Django sessions + CSRF protection.
* Role-based permissions: owners/admins can manage billing; accountants can create invoices/receipts; users have limited view/edit.
* Validate & sanitize company-provided CSS values (validate hex colors).
* Use secure temporary tokens for PDF downloads. Tokens must be cryptographically secure, one-time or with short expiration.
* Ensure uploaded logos are validated (mime type & size) and sanitized.

---

# 9 — Dev & deploy instructions (must include)

**Local dev**

* `python -m venv venv && source venv/bin/activate`
* `pip install -r requirements.txt`
* `npm install` & `npm run watch:css`
* `./manage.py migrate && ./manage.py runserver`
* Provide seed/fixture data and a management command to create a sample company + admin user + sample invoices.

**VPS Production (non-docker)**

* Recommend Ubuntu 22.04.
* Install Python, Postgres, Node (for building tailwind), Nginx.
* Setup PostgreSQL user and DB.
* Use `gunicorn` systemd service file to run Django.
* Nginx serves static files and proxies `/` to Gunicorn; also config subdomain routing if needed.
* Setup SSL with LetsEncrypt (Certbot).
* Add systemd timers or cron job for PDF cleanup.
* Provide a sample `nginx.conf` and `systemd` service files in repo.

**Docker option**

* Provide `Dockerfile` and `docker-compose.yml` for local/dev with services: web, db, redis (optional).
* Make sure docker setup can mimic production env vars.

---

# 10 — Observability, backup & maintenance

* Logging: use Django logging (file + rotation via `logrotate`).
* Monitoring: add basic health endpoint `/healthz`.
* Backups: document simple Postgres backup procedure (cron + `pg_dump` to remote storage).
* Cleanup: scheduled job to delete expired PDFs and old logs (configurable retention).

---

# 11 — Tests & acceptance criteria

Provide tests (unit + integration) and a test plan to prove features work.

**Acceptance criteria (automated / manual)**:

1. Able to create a Company, user, and client and log in.
2. Able to create invoice with multiple line items; `subtotal`, `tax`, and `total` calculations are correct.
3. `versioned_data` saved on invoice creation or when user clicks “Lock for send” and used to re-render identical PDFs.
4. PDF generation endpoint returns a secure download URL with a token that expires in 5 minutes by default.
5. Downloading a PDF marks the `PDFLog` as downloaded and schedules deletion; the file is removed after expiration or download.
6. Theming: changing `Company.primary_color` updates the UI and the invoice PDF visuals without rebuilding CSS.
7. Role permissions enforced (admin can delete, user cannot).
8. Sample seed data and setup commands run successfully so an admin can test in a fresh environment.

Include unit tests for:

* Price calculations
* PDF token generation & expiration
* Theme color conversion (hex → rgb)
* Permission checks

---

# 12 — Deliverables (explicit)

* Complete source code in a logical repo layout, with:

  * `README.md` explaining setup (dev + prod VPS + Docker option)
  * `requirements.txt` or `pyproject.toml`
  * `package.json` for frontend build (Tailwind)
  * `Dockerfile` and `docker-compose.yml` (optional)
  * `nginx.conf` and `gunicorn.service` systemd file examples
  * Migrations and fixtures
  * Unit tests and instructions to run them
  * Management commands: seed sample data, cleanup expired pdfs
  * Example `.env.example` listing required env vars
  * Clear instructions for generating SSL certs, setting up Postgres, and starting the app
* A short architecture doc (one page): how theming works, PDF lifecycle, where to add payments later.
* A minimal but attractive invoice HTML/CSS template used for PDF rendering.
* A short changelog or roadmap for adding payments, reports, DRF API, and Next.js front-end.

---

# 13 — Nice-to-have (bonus features if easy)

* Short-lived public view link for clients (signed URL).
* Email send queue (async) with retry & templating.
* CSV import for clients and invoices.
* Simple accounting summary (monthly income) on dashboard.

---

# 14 — Output format required from the AI you call

Ask the AI to respond with the following (in order):

1. A one-page architecture diagram text description (components + data flow).
2. A recommended file tree for the project (top 6–10 files/folders).
3. `requirements.txt` and `package.json` contents.
4. Example `settings.py` (security sensitive values replaced by env vars) showing relevant snippets (DATABASES, STATIC, MEDIA, CELERY optional, LOGGING, ALLOWED\_HOSTS).
5. A complete Django models file (`models.py`) with all models above.
6. Example views for invoice create, preview (htmx partial), generate-pdf, download-pdf (token).
7. Example `invoice_pdf.html` template showing how to use injected CSS vars, fonts, and logo.
8. `tailwind.config.js` showing mapping to CSS vars for theming.
9. Management command(s): `seed_sample_data`, `cleanup_expired_pdfs`.
10. Example test cases (pytest or Django TestCase).
11. `README.md` with setup & VPS production steps.
12. `nginx` and `systemd` sample config.
13. Short list of follow-ups/tradeoffs and next steps (payments, DRF, Next.js separation).

---

# 15 — Constraints & configuration values (defaults)

* Token expiry for PDF downloads: **5 minutes** (configurable `PDF_DOWNLOAD_EXPIRES_SECONDS`).
* PDF temp storage path: `MEDIA_ROOT/pdfs/tmp/`
* Default company currency: `USD` but allow per-company override.
* Disk retention for logs: 30 days by default.
* Target minimal VPS: 1 vCPU, 2GB RAM — test that basic flows run under these constraints; document memory usage and what pushes you to upgrade.

---

# 16 — Security & legal notes to implement

* Do not store credit card details or payment data in MVP.
* Validate user inputs, sanitize company-supplied strings, verify uploaded logo content-type and size.
* Provide DB backup instructions and recommend production-level secrets handling (use environment variables, don't commit secrets).
* Consider GDPR-style privacy for client contact data — include ability to delete client records and export client data.

---

# 17 — Tone & code quality

* Write clean, idiomatic Python/Django code with docstrings and comments where non-trivial.
* Use type hints where useful.
* Keep UI simple and usable; rely on Tailwind and accessible patterns.
* Keep the repository easy to read for a small team to pick up later.

---

# 18 — Final instruction for the AI agent

Start by producing the **one-page architecture description**, **file tree**, and the **requirements/package.json**. Then provide the core `models.py`. After that, continue with the remaining deliverables in the order listed in Section 14. If a choice is ambiguous, explain your rationale and pick the simplest robust option.

---

If you need sample values for Company (colors, logo path, sample invoice numbers, etc.), use the following seed sample:

* Company: Pixel Crafte Billing (slug: pixel-crafte-billing), primary: `#6B46C1`, accent: `#8B5CF6`, font: `Inter, system-ui, sans-serif`, logo: `media/sample/logo-pixelcrafte.png`
* Admin user: `admin@pixelcrafte.test` / password `Password123!`
* Client: Acme Design, email: `billing@acme.example.com`
* Example invoice number prefix: `PCF-2025-`

---

Deliver the prompt as a ready-to-use instruction set the other AI can follow. If anything in the spec is infeasible or would cause deployment risk on a tiny VPS, call it out and give the simpler alternative.

Good luck — build it clean and keep it lightweight, Pixel Crafte.
