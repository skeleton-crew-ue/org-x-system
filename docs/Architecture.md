# Organization X System — Architecture

**Owner:** Vladimer · **Status:** Draft v0.1 (Week 0) · **Last updated:** 2026-05-23

This document is the team's shared mental model of how the system fits together. Every dev should be able to read this in 20 minutes and know which app they're touching, which models they own, and how the pieces connect. If something here disagrees with the code, fix this doc — it's authoritative.

> Companion documents: [Project_Plan_Org_X.md](Project_Plan_Org_X.md) (timeline, team, scope), [Database_ERD.md](Database_ERD.md) (schema, fields, constraints).

---

## 1. System overview

A single Django application — one repo, one process, one Postgres database — that members and admins access through a web browser. There is no SPA, no separate API service, no microservices, no message broker. Every page is server-rendered HTML produced by a Django view, styled with Bootstrap, occasionally enhanced with Chart.js for visualizations.

```
                 ┌──────────────────────────────────────────────────────┐
                 │                    Browser                           │
                 │         (Bootstrap 5 + Chart.js, server-rendered)    │
                 └────────────────────────┬─────────────────────────────┘
                                          │ HTTPS
                 ┌────────────────────────▼─────────────────────────────┐
                 │   Render Web Service: Gunicorn → Django app          │
                 │   ┌────────────────────────────────────────────────┐ │
                 │   │  Django Apps                                   │ │
                 │   │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │ │
                 │   │  │ members  │  │documents │  │ voting   │      │ │
                 │   │  ├──────────┤  ├──────────┤  ├──────────┤      │ │
                 │   │  │ meetings │  │ finance  │  │ whatsapp │      │ │
                 │   │  └──────────┘  └──────────┘  └──────────┘      │ │
                 │   │              ┌──────────┐                       │ │
                 │   │              │   core   │ (base templates,      │ │
                 │   │              └──────────┘  shared utils, home)  │ │
                 │   └────────────────────────────────────────────────┘ │
                 │   Django Admin (/admin/) ← all admin-facing CRUD     │
                 │   WhiteNoise (static files)                          │
                 └────┬──────────────────────┬──────────────────────────┘
                      │                      │
                      │                      │
              ┌───────▼─────────┐    ┌───────▼─────────┐
              │ Render Postgres │    │   Render Disk   │
              │  (managed)      │    │ (media uploads) │
              └─────────────────┘    └─────────────────┘
                                            │
              ┌─────────────────────────────┴────────────────────────┐
              │ External:                                            │
              │   - Gmail SMTP (outbound email broadcasts)           │
              │   - WhatsApp .txt exports (file uploads, ingest only)│
              │   - Render Cron (daily reminder job)                 │
              └──────────────────────────────────────────────────────┘
```

---

## 2. Django apps (modules)

Seven Django apps. Each app is a self-contained slice — its own models, views, urls, templates, and admin. The split mirrors the team ownership in the project plan.

| App | Owner | Purpose | Key models |
|---|---|---|---|
| `core` | Lado + Mr T | Project root, base templates, navbar, home page, shared utils, error pages | (none) |
| `members` | Mr H | Custom User model, registration, login, profile, admin member CRUD | `User` (extends `AbstractUser`) |
| `documents` | Mrs D | Upload, tag, search, download organizational documents | `Document`, `Tag` |
| `voting` | Mrs D | Ballot creation, vote casting, results | `Ballot`, `BallotOption`, `Vote` |
| `meetings` | Mr T | Schedule meetings, store Zoom link + minutes, ICS download | `Meeting` |
| `finance` | Mr T | Income/expense entries, summary | `Transaction`, `Category` |
| `whatsapp` | Lado | Ingest exported chats, run analytics, broadcast emails | `ChatExport`, `ChatAnalysis`, `Broadcast` |

The Python package layout:

```
org_x_system/
├── config/                 # Django project settings
│   ├── settings.py
│   ├── urls.py             # root URL conf, includes each app
│   └── wsgi.py
├── core/                   # base templates, home page, shared utils
│   ├── templates/
│   │   ├── base.html       # owned by Mr T (shared UI)
│   │   ├── home.html
│   │   └── 404.html, 500.html
│   ├── static/             # CSS, JS, images
│   ├── urls.py
│   └── views.py
├── members/                # Mr H
├── documents/              # Mrs D
├── voting/                 # Mrs D
├── meetings/               # Mr T
├── finance/                # Mr T
├── whatsapp/               # Lado
├── manage.py
├── requirements.txt
├── runbook.md              # local-dev steps (week 0 deliverable)
└── README.md
```

> **Naming convention:** every app uses lowercase plural (`documents`, not `document` or `docs`). URLs use the same name (`/documents/`). Templates live in `<app>/templates/<app>/<page>.html` (the redundant `<app>/` directory is required for Django's template loader to namespace them — annoying but standard).

---

## 3. Data model (high level)

This is the conceptual model. Field-level details live in the code (single source of truth) and the ERD doc. Relationships and integrity constraints are described here because they affect every developer's choices.

### `members.User`

Extends `django.contrib.auth.models.AbstractUser`. We use a custom user model from day one — it's painful to switch later. Fields beyond Django's defaults:

- `role` — `CharField` with choices `ADMIN` / `MEMBER`, defaults to `MEMBER`
- `member_id` — string, unique, comes from the legacy spreadsheet during migration
- `phone` — string, normalized to E.164 during migration
- `joined_at` — date, optional (some legacy records lack this)

Django's `is_staff` flag controls Django Admin access. Set `is_staff=True` for users with `role=ADMIN`. Members never see `/admin/`.

### `documents.Document`

- `title`, `description`
- `file` — `FileField`, max 50 MB, uploaded to `media/documents/<year>/<month>/`
- `tags` — `ManyToManyField` to `documents.Tag` (single tag field, not a tree — see scope cuts in the plan)
- `uploaded_by` — `ForeignKey(User)`
- `uploaded_at` — `DateTimeField(auto_now_add=True)`
- `search_vector` — `SearchVectorField` (Postgres full-text), populated on save via a signal or override

`documents.Tag` is `name` + `slug`.

### `voting.Ballot` / `BallotOption` / `Vote`

- `Ballot`: `title`, `description`, `opens_at`, `closes_at`, `created_by`, `is_active`
- `BallotOption`: `ballot` (FK), `text`, `display_order`
- `Vote`: `ballot` (FK), `option` (FK), `voter` (FK User), `cast_at`
  - **Critical constraint:** `unique_together = ("ballot", "voter")` — enforces one vote per member per ballot at the DB level. This is a defense-in-depth pattern; we also check it in the view, but the DB constraint is the safety net.
  - The `Vote.voter` FK means votes are *not* anonymous in v1. The report should disclose this honestly. True secret-ballot would require a separate token-issuance flow, which is out of scope.

### `meetings.Meeting`

- `title`, `description`, `scheduled_at`, `duration_minutes`
- `location_or_link` — string (a Zoom/Meet URL or a physical address)
- `minutes` — `TextField`, blank initially, filled in after the meeting
- `created_by` — FK User
- `status` — `SCHEDULED` / `COMPLETED` / `CANCELLED`

### `finance.Transaction` / `Category`

- `Category`: `name`, `type` (`INCOME` / `EXPENSE`)
- `Transaction`: `amount` (DecimalField, 2 places), `transaction_date`, `category` (FK), `description`, `recorded_by` (FK User), `recorded_at`

The summary view runs three SQL aggregations: total income, total expense, balance. One Chart.js bar chart shows monthly income vs expense for the last 6 months.

### `whatsapp.ChatExport` / `ChatAnalysis` / `Broadcast`

- `ChatExport`: `file` (FileField), `uploaded_by`, `uploaded_at`, `source_group_name`, `message_count` (filled in after parsing)
- `ChatAnalysis`: `chat_export` (FK), `generated_at`, `results` (`JSONField` containing all the metrics — per-user message counts, peak hours, sentiment distribution, top influencers, spam flags, etc.)
- `Broadcast`: `subject`, `body`, `sent_by`, `sent_at`, `recipient_filter` (e.g. `ALL`, `ACTIVE_MEMBERS`, `ADMINS_ONLY`), `recipient_count`

`ChatAnalysis.results` is intentionally a JSONField rather than 12 separate tables. The shape of analytics output will iterate during sprint 3, and JSON lets us add metrics without migrations.

---

## 4. URL map

Top-level routes mounted in `config/urls.py`. Each app owns its own subtree.

```
/                       core/home (logged-in dashboard, redirects anonymous to /accounts/login)
/accounts/login/        Django built-in
/accounts/logout/       Django built-in
/accounts/register/     members.views.register
/accounts/profile/      members.views.profile
/accounts/profile/edit/ members.views.profile_edit

/documents/             documents list (with search box)
/documents/upload/      upload form
/documents/<id>/        detail view
/documents/<id>/download/   serves the file with permission check

/voting/                ballots list (open + closed)
/voting/<id>/           ballot detail + cast-vote form
/voting/<id>/results/   results page (visible after closes_at)

/meetings/              meeting list
/meetings/<id>/         meeting detail
/meetings/<id>/ics/     ICS calendar download

/finance/               transaction list
/finance/summary/       totals + Chart.js chart
/finance/add/           new transaction form (admin only)

/whatsapp/              analytics dashboard
/whatsapp/upload/       upload chat export (admin only)
/whatsapp/broadcast/    compose + send broadcast (admin only)

/admin/                 Django Admin (admin/staff only) — handles all admin CRUD
```

URL names follow `<app>:<view>` namespacing (e.g. `documents:detail`, `voting:results`). Always reverse URLs in templates with `{% url 'documents:detail' doc.id %}`, never hardcode paths.

---

## 5. Authentication & permissions

We use Django's built-in `django.contrib.auth` with a custom `User` model. No third-party auth libraries.

**Two roles, no granular permissions:**

- **Admin** — `User.role = "ADMIN"`, `is_staff = True`. Can access Django Admin, upload documents, create ballots, send broadcasts, add finance transactions, upload WhatsApp exports.
- **Member** — `User.role = "MEMBER"`, `is_staff = False`. Can view documents, vote in ballots, see results, see meetings, see their own profile. Cannot upload anything or write to admin-only models.

**Enforcement layers (defense in depth):**

1. **`@login_required` on every member-facing view.** Anonymous users get redirected to login.
2. **Custom `@admin_required` decorator** in `core.decorators` for admin-only views — checks `request.user.role == "ADMIN"`.
3. **Class-based views use `LoginRequiredMixin` + a custom `AdminRequiredMixin`.**
4. **Django Admin's own `is_staff` check** — admins-only by definition.
5. **Template-level rendering hints** — show the "upload" button only if `{% if user.role == 'ADMIN' %}`. This is a UX nicety, not security.

**Sessions:** Django's default DB-backed sessions. Cookie is HttpOnly, Secure (in prod), SameSite=Lax. No JWT, no API tokens.

**CSRF:** Django's middleware is on. Every POST form uses `{% csrf_token %}`. Out of the box.

**Password policy:** Django's `AUTH_PASSWORD_VALIDATORS` with the default 4 validators (min length 8, not too common, not all numeric, not similar to user attributes).

---

## 6. Key flows

The flows worth diagramming because they involve multiple modules or have integrity considerations.

### 6.1 Member registration → profile

```
User submits /accounts/register/ form
  → members.views.register validates form
  → creates User with role=MEMBER, is_active=True (no email verification in v1)
  → logs them in via auth.login()
  → redirects to /
```

**Notes:** No email verification in v1 (cut from scope). Password reset by email link is also cut — admins reset passwords manually via Django Admin.

### 6.2 Document upload → search → download

```
Admin: POST /documents/upload/ with file + tags
  → documents.views.upload validates form (admin_required)
  → saves Document (FileField writes file to media/documents/<year>/<month>/)
  → post_save signal computes search_vector from title + description + filename
  → redirects to /documents/<id>/

Member: GET /documents/?q=budget
  → documents.views.list filters where search_vector @@ to_tsquery('budget')
  → renders list

Member: GET /documents/<id>/download/
  → documents.views.download checks permission (logged in)
  → serves file via FileResponse
```

**Notes:** Search uses Postgres `SearchVector` + `SearchQuery`. No Elasticsearch, no embeddings, no semantic search. PDF/Word *content* (not just filename) extraction is a stretch goal — if not extracted, search only covers title + description + filename, which is fine for v1. Document the limitation in the report.

### 6.3 Voting (the integrity-critical flow)

```
Admin: creates Ballot via Django Admin (BallotAdmin handles inline BallotOption)
   → Ballot saved with opens_at and closes_at

Member: GET /voting/<id>/  (between opens_at and closes_at)
   → voting.views.detail checks: user is logged in,
                                  ballot is currently open,
                                  user has not already voted
   → renders form

Member: POST /voting/<id>/  with selected option
   → voting.views.cast wraps the write in transaction.atomic()
     → checks ballot is still open
     → checks Vote.objects.filter(ballot=b, voter=u).exists() — if yes, redirect with error
     → creates Vote(ballot=b, option=o, voter=u)
     → DB-level UNIQUE(ballot, voter) is the final safety net
     → on IntegrityError, redirect with "you already voted" message

Anyone: GET /voting/<id>/results/  (after closes_at)
   → voting.views.results aggregates votes per option, renders Chart.js bar chart
   → results are NOT shown before closes_at to prevent strategic voting
```

**Vote integrity guarantees:**

- One vote per (ballot, voter) — enforced at view, transaction, and DB layers.
- Votes can't be cast outside opens_at..closes_at — enforced in view.
- Results hidden until closes_at — enforced in view.
- Votes are *not* anonymous (the `Vote.voter` FK exists for audit) — disclosed in report as a known limitation; true secret ballot is out of scope.

### 6.4 WhatsApp analytics ingestion

```
Admin: POST /whatsapp/upload/ with .txt file
  → whatsapp.views.upload saves ChatExport
  → kicks off whatsapp.tasks.analyze_export(chat_export_id)
     (synchronous in v1 — no Celery; parsing 4,000 lines takes seconds)
  → analyze_export:
       - parse the .txt with whatsapp.parsers.parse_whatsapp_export
       - update ChatExport.message_count
       - run whatsapp.analytics.compute_metrics:
            - per-user message counts
            - peak hours histogram
            - daily/weekly frequency
            - sentiment via VADER (per-message and aggregated)
            - top influencers (message count + reply heuristic)
            - spam flags (keyword + frequency rules)
       - save results into a new ChatAnalysis row (results = JSONField)
  → redirect to /whatsapp/

Anyone (logged in): GET /whatsapp/
  → whatsapp.views.dashboard fetches latest ChatAnalysis
  → renders Chart.js charts from ChatAnalysis.results JSON
```

**Notes:** Parsing runs in the request cycle for v1 (it's fast enough for typical exports). If exports get large enough to hurt the request, move it to a Render Cron Job triggered after upload, or accept a slow upload page. No Celery/Redis — they're out of scope for the MVP.

### 6.5 Email broadcast

```
Admin: POST /whatsapp/broadcast/ with subject, body, recipient_filter
  → whatsapp.views.broadcast saves Broadcast row
  → resolves recipient_filter to a User queryset
  → calls django.core.mail.send_mass_mail with bcc list
  → updates Broadcast.recipient_count and sent_at
  → redirects with "sent to N members" message
```

**Notes:** Gmail SMTP caps at ~500/day. The team's WhatsApp group probably has fewer than 500 active members so this works for v1. The report calls out that production-scale (4,000-member) broadcasts would need a transactional email provider. Send synchronously in the request — slow but simple.

### 6.6 Scheduled event reminders

```
Render Cron Job (daily 09:00):
  → runs `python manage.py send_event_reminders`
  → meetings.management.commands.send_event_reminders:
       - finds Meetings with scheduled_at within next 24 hours
       - emails each member who hasn't seen it
       - logs to Confluence-readable output
```

This is the only scheduled task in v1. Don't introduce APScheduler, don't introduce Celery beat — Render Cron Jobs are simpler.

---

## 7. Technology choices recap

This is the locked stack. Decisions made earlier in the planning process; deviation requires explicit team agreement.

| Concern | Choice | Notes |
|---|---|---|
| Backend framework | Django 5.x | Locked — see Project_Plan §2 for why over Flask. |
| Database | PostgreSQL (Render managed) | Locked — needed for `SearchVector`. |
| Auth | `django.contrib.auth` with custom User | Locked. |
| Admin UI | Django Admin | Locked — handles all admin CRUD in v1. |
| Templates | Django Templates + Bootstrap 5 | Locked. |
| Charts | Chart.js (via CDN) | Single CDN script, no build pipeline. |
| Static files | WhiteNoise | Required because Render doesn't serve static by default. |
| Media files | Django `FileField` → Render disk | Ephemeral on free tier; `seed_data.py` recreates demo files. |
| Form rendering | django-crispy-forms (with bootstrap5 template pack) | Optional — only if vanilla forms feel painful in week 1. |
| WSGI server | Gunicorn | Standard Django prod choice. |
| Settings management | `django-environ` for env vars | `.env` locally; Render Env Vars in prod. |
| Email | Django `send_mail` over Gmail SMTP | App password, not real password. |
| Analytics | pandas + VADER (offline notebook + production parser) | No ML training. |
| Scheduled tasks | Render Cron Job | One job for daily reminders. No Celery/Redis. |
| File parsing | Python stdlib + `python-dateutil` | WhatsApp exports are line-based text. |
| Search | Postgres `SearchVector` / `SearchQuery` | No Elasticsearch. |

---

## 8. Configuration and settings

Settings split via `django-environ` with one `.env` per environment. `config/settings.py` reads:

```
DEBUG                  bool      False in prod
SECRET_KEY             string    50+ char random; never committed
ALLOWED_HOSTS          csv       org-x-system.onrender.com,localhost,127.0.0.1
DATABASE_URL           url       Render auto-injects in prod; sqlite:///db.sqlite3 locally
EMAIL_HOST             string    smtp.gmail.com
EMAIL_PORT             int       587
EMAIL_HOST_USER        string    project Gmail
EMAIL_HOST_PASSWORD    string    Gmail app password
DEFAULT_FROM_EMAIL     string    "Org X System <noreply@orgx.example>"
MEDIA_ROOT             path      ./media locally; /opt/render/project/media in prod
TIME_ZONE              string    Asia/Tbilisi (or whatever the team agrees on)
```

Local devs use SQLite (file at `db.sqlite3`) so no Postgres install is needed for week 0. Mr H verifies the app runs identically on Postgres before the sprint-1 demo.

---

## 9. Deployment

See **Project_Plan §3** for the full Render setup. The architectural shape:

- **Build:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- **Start:** `gunicorn config.wsgi:application`
- **Cron:** `python manage.py send_event_reminders` daily at 09:00 local
- **Static:** WhiteNoise serves `/static/` from `STATIC_ROOT` after collectstatic
- **Media:** writes to a Render disk; ephemeral on free tier (accept this in v1)

Any push to `main` triggers a Render deploy. PRs are merged to `main` after code review. There is no staging environment in v1 — the cost is a broken `main` occasionally; the benefit is forced discipline in code review. Mr H owns the `backup_db.py` management command that runs before each sprint demo.

---

## 10. Cross-cutting concerns

**Logging.** Django's default logging to stdout; Render captures it in their log viewer. No separate logging service. Use `logger = logging.getLogger(__name__)` at the top of modules; log at WARNING for unexpected branches.

**Error pages.** Custom `404.html` and `500.html` in `core/templates/` (owned by Mr T). Sentry / Rollbar are not set up in v1 — the team checks Render logs after every deploy.

**Time zones.** `USE_TZ = True`. All times stored as UTC; rendered in the team's local time zone. Don't store naïve datetimes anywhere.

**Internationalization.** Single language only (`USE_I18N = False`). No translation files.

**File-upload security.** `FileField` with explicit `upload_to` and a max-size validator. Whitelist MIME types: `application/pdf`, `application/vnd.openxmlformats-officedocument.*`, `text/plain`, `image/png`, `image/jpeg`. Never serve user-uploaded files from the same origin without a `Content-Disposition: attachment` header — this prevents browser-rendered XSS via uploaded HTML/SVG.

**Performance.** Don't optimize. The free tier has limits, the dataset is small (4,000 members, hundreds of documents). If a page is slow, add `select_related` / `prefetch_related` before adding a cache. No cache layer in v1.

**Tests.** Django's test runner. Per-app `tests.py`. Mr A writes manual test cases (out of scope for this doc — see his test plan in Confluence). Devs write at least one model test per app and one view test per module-owner, executed locally before push. No CI; tests are the dev's responsibility.

---

## 11. What's *not* in this architecture

For honesty (and to push back on scope creep):

- **No REST API.** Every interaction is a server-rendered page. If a future requirement needs an API, that's a separate architectural decision.
- **No async tasks.** No Celery, Redis, RQ, or APScheduler. Render Cron Jobs handle the one scheduled task we have.
- **No real-time.** No websockets, no SSE, no live vote counts.
- **No microservices.** One Django app, one process, one Postgres.
- **No object storage.** Files on the Render disk; documented as a free-tier limitation.
- **No SPA.** No React, Vue, build pipeline, or API for a frontend to consume.
- **No third-party auth.** Username/password only.
- **No caching layer.** No Redis, no Memcached.
- **No CI.** Tests run locally; Render auto-deploys from `main`.
- **No staging environment.** One environment in production, one on each laptop.

These cuts are not failures of architecture — they're scope discipline. If the team is ahead of schedule by mid-June, the **first** thing to add is **password reset by email link** (real users will need it). Everything else stays absent unless there's a strong reason.

---

## 12. Open questions for week 0

- Does the legacy member CSV use a primary key we can map to `User.member_id`, or do we generate fresh IDs?
- Are documents uploaded as PDFs only, or also `.docx`? (Affects MIME whitelist and search-text extraction.)
- What's the actual Gmail account the project will send broadcasts from? (Needs to be set up before sprint 3.)
- Is there a real WhatsApp export Mr K can share, or do we synthesize a fake one for development?
- Time zone: which one? (Affects every datetime rendered in the UI.)

These are reflected in **Project_Plan §9 — Open questions to resolve in week 0**. Lado and Mr K to clear before sprint 1 starts.
