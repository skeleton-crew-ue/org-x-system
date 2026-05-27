# Organization X — Integrated Digital Management System
## Team plan & 1-month roadmap

**Owner (lead/mentor):** Vladimer
**Team:** 5 students (3 dev-leaning, 2 product/analytics/QA)
**Date:** 2026-05-23
**Status** very draft, to be updated
**Hard deadlines from brief:** Frontend course 2026-07-09 · Agile course 2026-07-18
**Working assumption:** ship a usable MVP by end of May (4 weeks), then 6 weeks of polish, real data, demo prep, and reports until the deadlines.

---

## 1. Reality check on the scope

The brief lists seven modules: web portal & auth, data migration of 4,000 records, document management with search, e-voting, WhatsApp analytics + smart notifications, meeting management, and financial records. For five inexperienced students that is too much if taken literally. The plan below trims the *hardest* parts down to honest MVPs. The full list of cuts and simplifications lives in **Section 8 — Out of scope**; this section just explains the philosophy.

The five biggest descoping decisions:

- **WhatsApp integration is the trap.** The official WhatsApp Business API is paywalled and slow to provision. Don't build live integration. Instead, accept the standard "Export chat" `.txt` file as input and run analytics offline. Notifications go out by email + a downloadable WhatsApp broadcast list.
- **"Online meeting coordination"** does not mean building a video call — paste in a Zoom/Meet link and store it. That's it.
- **"Intelligent automated replies"** is an LLM rabbit hole. Cut from MVP, mention as future work.
- **Data migration of 4,000 records** is the easiest "hard-sounding" item — it's a one-shot pandas script. Treat it as a small task, not a module.
- **Sentiment analysis** — use VADER (Python) out of the box. No training, no fine-tuning.

Two structural decisions buy more time than any individual feature cut: server-rendered templates only (no SPA / React / Vue), and one repo with no Docker, no microservices, no CI beyond the host's auto-deploy.

**Budget constraint:** zero. Everything below is free or has a free tier sufficient for this project.

---

## 2. Tech stack (chosen for beginners)

| Layer | Pick | Why |
|---|---|---|
| Frontend | HTML + Bootstrap 5 + a little vanilla JS, server-rendered via Django templates | Lowest learning curve, matches the FE course list, no build pipeline |
| Backend | Python + Django | Batteries-included: free admin panel, built-in auth, ORM with migrations, forms, CSRF — all the things this team would otherwise reinvent badly |
| DB | PostgreSQL | Stable, free, real SQL — better learning than MongoDB for this team |
| Auth | Django built-in (`django.contrib.auth`) | Sessions, password hashing, permissions — zero custom code |
| Admin UI | Django Admin (`django.contrib.admin`) | All admin-facing CRUD lives here in v1; no custom admin pages to build |
| Charts | Chart.js (CDN) | One file, easy |
| Analytics | pandas, matplotlib, VADER (sentiment) | Run offline; results land as JSON or DB rows that a Django view reads |
| Hosting (live URL) | Render free tier | GitHub auto-deploy, managed Postgres on the same dashboard, Python-friendly. See Section 3. |
| Email | Gmail SMTP or Mailtrap free tier | Free, sufficient for low volume |
| Process | GitHub + Jira free + Confluence free | All free for ≤10 users; required by the agile course anyway |

Single repo. No microservices. No Docker until week 4 if at all. Every paid service has been replaced with a free tier — see Section 3 for hosting trade-offs and free-tier limitations to plan around.

> **Why Django over Flask.** I initially leaned Flask for "fewer files = simpler." On reflection, Django is the better fit for this team. Django gives you a working admin panel, auth, ORM, migrations, forms, and CSRF protection out of the box — exactly the things inexperienced devs reinvent badly. The Django Admin alone directly satisfies *"administrative management of member records"* with no UI work. Django's "magic" is mostly stuff students shouldn't be writing themselves anyway. The opinions Django imposes are the opinions this team needs imposed.

---

## 3. Hosting on Render (zero budget)

**Strategy:** develop locally, deploy to Render so the examiner has a URL between checkpoints, but run the actual final demo from a designated team laptop to avoid free-tier cold-start surprises.

### Layered approach

1. **Local first.** Every dev runs the app on their own machine via `python manage.py runserver`. SQLite locally for speed; Postgres only when deployed. This is where 95% of work happens.
2. **Render for the "live demo URL".** Auto-deploys from `main`, gives a real subdomain, accessible to the examiner between checkpoints, satisfies the agile-course rubric of having something live.
3. **Local + ngrok for the actual final demo.** When presenting on July 18, run on a laptop and tunnel a public URL via ngrok free tier. No cold starts, no surprises.

### Why Render

Render is a managed cloud platform that connects to a GitHub repo and redeploys on every push to `main`. It auto-detects a Django app (or you give it explicit build/start commands), provisions managed Postgres on the same dashboard, and gives you a `<your-app>.onrender.com` subdomain. The killer feature for inexperienced teams: the moment someone merges a broken PR, the live site visibly breaks — that consequence forces good "test before you push" habits faster than any process document. The UI is simpler than AWS or GCP, no Linux server admin needed.

### Render setup (week 0 — Mr H owns)

- New Render account on the team Gmail.
- Connect the GitHub repo, web service named `org-x-system`, environment **Python 3**.
- Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`.
- Start command: `gunicorn config.wsgi:application`.
- Environment variables: `DEBUG=False`, `SECRET_KEY` (generated), `ALLOWED_HOSTS=org-x-system.onrender.com`, `DATABASE_URL` (auto-injected by Render Postgres), `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (Gmail app password).
- Provision a managed Postgres instance (free tier).
- Add `whitenoise` to `MIDDLEWARE` for static-file serving (Render doesn't serve static files by default).
- Add a Render Cron Job for the daily reminder management command (Sprint 3).

A working `runbook.md` in the repo root documents the exact commands to bring the app up locally on any teammate's machine in under five minutes. Test the runbook on someone else's laptop in week 0 — if it doesn't work for them, fix it now, not the night before the demo.

### Render free-tier landmines to plan around

- **Web service sleeps** after ~15 minutes of inactivity. Cold start takes 30–60 seconds. Workaround: hit the URL five minutes before any examiner meeting, and run the actual demo from local + ngrok.
- **Free Postgres has limited retention** (historically 90-day expiry — verify the current policy when you sign up). Treat the deployed DB as a demo, not a system of record. Mr H writes a `backup_db.py` management command that runs before every sprint demo (`pg_dump` to a local file, committed to a private branch). Keep a `seed_data.py` management command that re-creates a clean demo dataset (a few members, a few documents, a sample election, sample finance entries, sample WhatsApp analytics) in under a minute — so even if data is lost, the demo is one command away.
- **Limited memory/CPU** on free tier. The app will feel slow but won't fall over. The 4,000-member migration runs locally first, then the cleaned data is imported on Render — don't run the cleaning script in production.
- **Render disk is ephemeral** for files outside `/opt/render/project/src`. Document uploads and WhatsApp exports go to a Render-mounted disk if persistence is needed; for v1, accept that uploads may not survive a redeploy and rely on `seed_data.py` to recreate demo files.
- **Email-sending limits.** Gmail SMTP allows ~500 emails/day from a personal account. Plenty for a demo, not for a real broadcast to 4,000 members. The report should call this out as a production-readiness gap.

---

## 4. Team split

Six people: four coders (you + three students), one PO/BA, one QA. Module ownership chosen by the team, refined here for full-stack coverage and load balance.

**On full-stack rotation:** all three student devs want to try frontend *and* backend. That's pedagogically the right ask for an educational project, and Django's server-rendered structure (template + view in the same app, often the same PR) makes the boundary fuzzier than a SPA stack would. The model below keeps **stable primary ownership** per module (so somebody still owns the schema for voting, somebody still owns the meetings UI) and layers cross-pollination on top:

- Each sprint, every dev picks **one stretch ticket** outside their primary module(s). Code review by the module's primary owner before merge.
- One **cross-domain pairing** per sprint: pair two devs for 2–3 hours on a single end-to-end vertical slice (model → view → template → CSS). Both learn faster, you ship a feature.
- **Don't** rotate full module ownership every sprint. That guarantees nobody owns anything, schema drift goes unmanaged, merge conflicts get ugly. Scrum *role* rotation (PO/Scrum Master) is required by the brief; module ownership is not.

### Vladimer — Tech lead, architect, Scrum Master, WhatsApp module owner
Owns: system architecture, database schema design, Jira & Confluence administration, code review on every PR, design review on every UI PR, unblocking, the WhatsApp analytics module (chat parsing, VADER sentiment, charts, dashboard data), and visual design / wireframes for the whole product.
**Load warning:** this is four hats — architect, SM, lead reviewer, and feature dev. If WhatsApp slips or you find yourself blocking the team during middle sprints, drop WhatsApp first to a "demo-quality" subset (activity charts + sentiment only — see Section 8).
**SM rotation:** ceremonial Scrum Master duties (running standup, writing retro notes) rotate each sprint to satisfy the agile-course rubric — see the rotation note at the end of this section. You retain the Jira admin and process ownership.

### Harsh — Developer (auth + member portal + data migration + deployment)
Owns: Django project skeleton (week 0, with Lado), `django.contrib.auth` wiring, registration/login/logout, Member model and roles, member profile views, `MemberAdmin` configuration in Django Admin, the 4,000-row data migration script (as a Django management command), and **Render deployment** (account, build/start commands, env vars, Postgres provisioning, `backup_db.py`). The "spine" the other modules hang off of.
**Why these together:** auth, member data, and migration all touch the same models and tables. One person owning that surface keeps the schema coherent.
**Stretch:** picks up one small frontend ticket each sprint paired with Mr T.

### Dana — Developer (voting + documents)
Owns: `voting` Django app (Ballot/BallotOption/Vote models with the unique-together constraint, ballot-creation in Django Admin, voter UI, results page, tally view) and `documents` Django app (Document model with `FileField` and tags, Postgres full-text search via `SearchVector`, list/detail/upload views, permission decorator).
**Why these together:** both modules have similar permission patterns (admin creates, members consume) and both need search/listing UIs that share template structure.
**Stretch:** picks up one small frontend ticket each sprint.

### Thinley — Developer (shared UI lead + meetings + finance)
Mr T has **two co-equal responsibilities**, and the shared UI work is *not* secondary:

**Shared UI lead (cross-cutting):** base template, navbar, footer, Bootstrap theme and CSS variables, the home page, the analytics dashboard layout, the 404/500 error pages, the empty-state designs, and **design-review on every UI PR from devs**. Without this single owner, the four modules look like four different products.

**Feature modules:** `meetings` Django app (Meeting model with Zoom-link field and minutes textarea, list view, ICS download), `finance` Django app (Income/Expense models with category, summary view, one Chart.js bar chart). Both registered in Django Admin so most CRUD is free.

**Why this combination:** meetings and finance are the two lightest backend modules in the system, which deliberately leaves capacity for shared UI — a job that's bigger than it looks once four different devs start writing templates.
**Stretch:** picks up one small backend ticket each sprint (e.g. a model field, a small view) outside meetings/finance to grow into other parts of the stack.

### Karim — Product Manager / Business Analyst (+ test design)
Owns the **upstream half** of quality: requirements gathering and clarification, user stories with acceptance criteria, backlog grooming (with Lado), stakeholder coordination, demo script, lead author of the project report, and the **ceremonial Product Owner role** for sprint reviews.

**Test design (shared with Asadbek):** writes the test *scenarios* (Given/When/Then-style narratives derived from his own acceptance criteria) for each module before that module enters QA. Mr A turns those scenarios into executable test cases and runs them. This split makes sense because Mr K already holds the requirements model in his head — extracting test scenarios from his own AC is a 30-minute task; rebuilding them from scratch is a half-day for someone who didn't write the AC.

**Bug triage (shared with Asadbek:** runs a 30-minute bug-grooming session each sprint — Mr A presents reproduced bugs, Mr K decides priority and what's fix-now vs defer-to-buffer based on requirements impact.

**Report contribution:** writes Introduction, Requirements, System Architecture (from Lado's week-0 doc), Implementation Summary, and Future Work chapters.

**Hands-on overflow:** when ahead, takes low-risk hands-on tickets — seed-data scripts, manual data cleanup for the migration, drafting Bootstrap pages from Lado's wireframes (HTML/CSS only).

### Mr A — QA Engineer (+ Jira bug board owner)
Owns the **downstream half** of quality: turns Mr K's test scenarios into concrete test *cases* (click-by-click steps with expected results), executes them on every release, reproduces and files bugs in Jira, verifies fixes, runs end-to-end tests, and runs the security-pass checklist in Sprint 3.

**Jira bug board ownership:** the kanban view of bugs (open / in progress / fixed / verified / deferred), reported in standup. This frees Lado from Jira micro-admin and gives Mr A a clear "I run this" deliverable beyond test execution.

**Bug triage (shared with Mr K):** brings reproduction steps and severity assessment to the sprint bug-grooming session.

**Report contribution:** writes the Testing & Evaluation chapter (his domain) *and* contributes screenshots throughout the Implementation Summary chapter — he's the person exercising every flow anyway, so he's best placed to capture clean screenshots.

**Demo support:** co-runs the demo rehearsal with Mr K — Mr A clicks through the live flow, Mr K narrates against the demo script. This catches both technical regressions and "the script no longer matches the UI" issues.

**Note:** even with Mr K absorbing test design and shared bug triage, the QA load still ramps — lightest in week 1, heaviest in weeks 3–4. The rebalance gives Mr A more *predictable* work earlier and keeps the late-sprint surge proportional rather than overwhelming.

> **Scrum role rotation (mandatory by the brief):** the agile course requires PO and Scrum Master to rotate each sprint. Resolution: keep the *operational* roles stable (Lado owns the Jira admin and process; Mr K owns backlog and acceptance criteria) but rotate the **ceremonial** SM and PO duties — who runs standup, who chairs sprint review, who writes the retro — across all six team members over the four executing sprints. Document this distinction in Confluence so the examiner sees compliance. Suggested rotation: Sprint 1 — Lado SM / Mr K PO. Sprint 2 — Mr H SM / Mrs D PO. Sprint 3 — Mr T SM / Mr A PO. Sprint 4 — Mr K SM / Lado PO.

---

## 5. One-month plan (Sprint 0 + Sprints 1–3, with Sprint 4 falling in week 5)

Sprints are one week each. Standups three times a week (Mon/Wed/Fri, 15 min). Sprint review + retro every Friday afternoon. Everything in Jira.

### Week 0 — Sprint Planning (May 4–8)
**Goal:** everyone can run the project locally and the backlog exists.

- **Lado:** architecture doc (`Architecture.md` — Django apps, models, URL map, key flows), wireframes for the 6 main member-facing pages, GitHub repo with `django-admin startproject` scaffolding. DB schema reviewed end-to-end.
- **Mr H:** Django models for User and Member, skeleton apps for the other modules, first migration, superuser created, **Render account + web service + Postgres provisioned**, "hello world" deployed and reachable at `org-x-system.onrender.com`. Local dev runbook written and tested on a teammate's machine.
- **Mr K:** full backlog in Jira broken into stories with acceptance criteria; sprint 1 selected; **drafts test scenarios for sprint-1 stories alongside the AC** (Given/When/Then format); stakeholder questions from Section 9 answered.
- **Mr A:** Confluence space set up, definition-of-done agreed, branch & PR rules written. Sets up the **Jira bug board** (kanban with Open/In Progress/Fixed/Verified/Deferred columns). Reviews Mr K's sprint-1 test scenarios and turns them into the test-case template.
- **Mrs D & Mr T:** dev environment running (`pip install -r requirements.txt`, `python manage.py runserver`), a tiny "your name here" PR each to prove the workflow. Mr T also picks the Bootstrap theme.

### Week 1 — Sprint 1: Foundation (May 11–15)
**Goal:** a logged-in user can see their profile. Migrated data is in the DB.

- **Mr H:** stock Django auth wired up (login/logout/registration views), Member model with admin/member role, `MemberAdmin` registered in Django Admin (gives admin list/edit for free), password policy. Member profile view + edit page (`UpdateView`). Data migration: clean the 4,000-row export (dedupe, standardize phone/email, fix dates) and import via a Django management command (`python manage.py import_members data.csv`). Document the cleaning rules in Confluence.
- **Mr T:** base template (navbar, footer, container), login/register/profile templates, Bootstrap theme applied site-wide. Home-page skeleton with placeholder cards for each module.
- **Mrs D:** stretch ticket — write a small admin-only "members search" page (server-rendered table + simple filter form) to start learning Django views and templates ahead of her sprint-2 work.
- **Lado:** code review every PR, design review every template PR, schema review with Mr H, start the WhatsApp parser (offline notebook only — no app integration this sprint).
- **Mr K:** sprint-2 AC + test scenarios written ahead (so Mr A is never blocked waiting on him). Demo script v1, stakeholder check-ins. Hands-on overflow: writes a `seed_data.py` management command for demo data.
- **Mr A:** turns Mr K's sprint-1 scenarios into executable test cases, runs them against auth and member management, files bugs in Jira (and tracks them on the bug board he owns). Joint bug-grooming session with Mr K on Friday — decide what to fix in sprint 2 vs defer.

**Demo at end of week:** admin logs into Django Admin, sees 4,000 imported members, can edit one. A member can register, log in, and edit their profile on the public site.

### Week 2 — Sprint 2: Core modules (May 18–22)
**Goal:** documents, meetings, finance basics work end-to-end.

- **Mrs D:** `documents` Django app — Document model with `FileField` and tags, Postgres full-text search via `SearchVector`, list/detail/upload views, permission decorator. `DocumentAdmin` registered.
- **Mr T:** `meetings` Django app — Meeting model with Zoom-link field and minutes textarea, list view, detail view, ICS download. `finance` Django app — Income/Expense models with category, summary view (three SQL aggregations + one Chart.js bar chart). Both registered in Django Admin. Plus shared-UI work: dashboard layout polish, navigation updates for the three new modules.
- **Mr H:** stretch ticket — pair with Mrs D on the document-upload form template. Beyond that: deployment hardening (`DEBUG=False` in prod, `ALLOWED_HOSTS`, env-var secret key, WhiteNoise static files served correctly on Render).
- **Lado:** continue WhatsApp parser, code/design review, unblock. Architecture review of how documents/meetings/finance are wired before merging.
- **Mr K:** sprint-3 AC + test scenarios (particularly for the trickier voting and notifications work — voting has integrity edge cases that are easy to miss). Drafts the report's Introduction and Requirements chapters from existing Confluence pages. Hands-on overflow: drafts the documents and finance pages from Lado's wireframes (HTML + Bootstrap, no logic).
- **Mr A:** turns sprint-2 scenarios into test cases; regression-test auth; manually run new module tests; load-test document upload with a 50 MB file. Bug-grooming session with Mr K on Friday — surfaces severity assessments per bug for triage.

**Demo at end of week:** upload a doc, search for it, schedule a meeting, log an expense.

### Week 3 — Sprint 3: Voting + analytics + notifications (May 25–29)
**Goal:** the two "wow" modules land. Notifications go out.

- **Mrs D:** `voting` Django app — Ballot, BallotOption, Vote models with a unique-together constraint on (ballot, voter), tally view, results view. `BallotAdmin` for admins; voter-facing ballot list + cast-vote page; results visualization with Chart.js.
- **Lado:** WhatsApp module integrated into the app — upload exported chat `.txt`, run analytics (sentiment via VADER, peak hours, top users, simple keyword-spam detection, top-N "influencers" by message + reply count), persist results into a `ChatAnalysis` model, render the dashboard with Chart.js. This is the heaviest single sprint for you — protect the time.
- **Mr T:** email-broadcast view using Django's `send_mail` over Gmail SMTP, broadcast composer page, event-reminder management command set up to run on a daily cron. Plus shared-UI work: analytics dashboard layout (visual frame for Lado's data).
- **Mr H:** stretch ticket — pair with Mrs D on the voting results page. Beyond that: write a `backup_db.py` management command and run it before the sprint-3 demo (because free Postgres data can disappear).
- **Mr K:** sprint-4 AC + test scenarios (lighter — mostly polish/regression criteria). Drafts the report's System Architecture chapter from Lado's week-0 doc. Demo script v2 with the new voting + analytics flows. Joint bug-grooming with Mr A.
- **Mr A:** turns sprint-3 scenarios into test cases. End-to-end test: register → vote → see results. **Security pass** (Mr A's solo deliverable): Django gives SQL-injection and CSRF protection by default — verify it's enabled. Check file-upload MIME whitelist, password policy, `DEBUG=False`, `ALLOWED_HOSTS`, secret key in env var. Pen-test the broadcast composer for XSS. Capture screenshots of every working flow for the Implementation Summary chapter Mr K is writing.

**Demo at end of week:** a working election with a chart of results, plus an analytics dashboard from a real exported group chat.

### Week 4 — Sprint 4: Finalization (June 1–5)
**Goal:** the product is complete enough for the July demo. Reports started.

- **All devs:** bug burn-down from Mr A's list. No new features. Each dev owns the bugs filed against their modules.
- **Mr T:** visual polish, mobile responsiveness pass, empty states, error pages, 404/500 templates.
- **Mr K:** finishes his report chapters — Introduction, Requirements, System Architecture, Implementation Summary, Future Work. Integrates Mr A's Testing chapter and screenshots. Co-runs the demo rehearsal with Mr A (Mr K narrates against the demo script).
- **Mr A:** runs the full manual test plan one more time. Writes the **Testing & Evaluation chapter** of the report. Captures the final round of screenshots for the Implementation Summary. Signs off go/no-go on the bug board (zero blockers, agreed list of known issues). Co-runs demo rehearsal with Mr K (Mr A clicks the live system, surfacing any "the script no longer matches the UI" gaps).
- **Lado:** production deploy verified, code-review the report, run the demo rehearsal as if you were the examiner, fill any documentation gaps.
- **Mr H:** runbook update, final DB backup, env-var sanity check.

**Demo at end of week:** the team gives a 15-minute walkthrough to Lado as if he were the examiner. Identify the three weakest moments; week 5+ buffer is for fixing those.

---

## 6. Weeks 5–10 (June–early July) — buffer & polish

You'll be tempted to add features. Don't. Use the buffer for: real WhatsApp data analysis on actual organization chats, the 1,000-page document corpus ingestion, accessibility & UX cleanup, the agile-course retrospective prep, and report writing. If everything's truly done by late June, *then* consider adding intelligent auto-replies as a bonus module — and only if Lado wants the stretch challenge on top of the WhatsApp module he already owns.

---

## 7. Things to watch for (mentor's eye)

- **PR sizes.** Inexperienced devs ship 2,000-line PRs. Cap at ~300 lines per PR. Reject the rest with kindness.
- **Schema drift.** All schema changes go through Mr H and Lado. Every model change ships as a Django migration that's committed to the repo. Otherwise Mrs D and Mr T will each invent their own user table.
- **"It works on my machine."** Set up Render deploys from `main` in week 0 so broken code is visible immediately.
- **Scope creep from the brief.** The brief is a wish list. Push back gently when a teammate says "but the doc says we need intelligent auto-replies" — point them at the explicit cuts in section 8.
- **Django Admin overuse.** It's tempting to expose every model in admin and call it done. For *member-facing* features (voting, document browsing, etc.) you still need real views. Admin is for staff only.
- **Jira hygiene.** The agile course grades this. Lado (as Jira owner) and Mr K (as PO) should jointly hassle people daily about logging time and updating status. Set a daily 5pm reminder.
- **Frontend consistency.** With four people writing templates, drift is inevitable. Mr T owns visual review on every UI PR; Lado does a sweep at end of each sprint to catch anything that slipped through.

---

## 8. Out of scope — what we're explicitly not building

This is the single most important section of the plan. When a teammate or stakeholder says "but the brief says we need X," point them here. Each item is either cut, simplified to an MVP, or deferred to the post-MVP buffer (June onward) if there's time.

### Cut from MVP, mention in the report as "future work"

- **Live WhatsApp Business API integration** — paywalled, slow to provision, weeks of setup with Meta. We accept exported chat `.txt` files instead.
- **Intelligent automated replies to WhatsApp messages** — would require an LLM, message routing, and live API access. None of which we have.
- **"Identification of message types that generate strong emotional reactions"** — this is a research problem, not a sprint task.
- **Real-time anything** — no live vote counts, no live chat, no websockets, no server-sent events.
- **Mobile app** — responsive web only.
- **Two-factor authentication.**
- **File versioning** for documents — latest upload wins.
- **Audit log** beyond `created_at` / `updated_by` fields on each model.
- **Multilingual UI** — single language only.
- **Password reset by email link** in v1 — admin manually resets passwords from Django Admin. Add the email flow later if there's time.
- **Granular permission matrices** — only two roles: `admin` and `member`. No per-document ACLs, no group-level permissions.

### Simplified to honest MVPs

- **Document search** → Postgres full-text search on filename + extracted text. Not semantic search, no vector DB, no embeddings.
- **Document categorization** → a single tag field (or `ManyToMany` to a Tag model). Not a category tree, no hierarchies.
- **"Online meeting coordination"** → a text field on the Meeting model where the admin pastes a Zoom or Meet link. Plus an ICS download. We do not build video, screensharing, or calendar sync.
- **Meeting minutes** → a rich-text field on the Meeting model. No collaborative editing, no version history.
- **Financial reporting** → three SQL aggregations rendered as a table and one bar chart. Not a BI tool, no custom report builder, no exports beyond CSV.
- **Sentiment analysis** → VADER out of the box. No model training, no fine-tuning, no domain adaptation.
- **Spam detection** → keyword list + message-frequency heuristic. Be honest about the simplicity in the report.
- **"Smart notifications"** → scheduled email broadcasts via SMTP, plus a downloadable contact list admins paste into WhatsApp themselves. No push notifications, no SMS.
- **"Influential group members"** → ranked by message count + reply count. Not a real influence graph, no PageRank.
- **Admin UI** → Django Admin for v1. We do not build a custom admin dashboard. If the examiner wants a "branded" admin look, that's a week-5+ task.

### Structural cuts (high leverage)

- **No SPA** — server-rendered Django templates only. No React, Vue, Next.js, or build pipeline.
- **No microservices** — one Django project, one repo, one process.
- **No Docker in v1** — Render auto-deploys from `main`. Add a Dockerfile in week 5 only if deployment is hurting.
- **No custom CI** — just Render's auto-deploy. Tests run locally before push.
- **No third-party auth** (Google/GitHub login) — username + password only.
- **No object storage in dev** — local filesystem; switch to S3 only when deploying to prod.

### What stays fully in scope

For clarity, here's what we *are* committing to, end-to-end: member registration & login, admin management of members via Django Admin, the 4,000-record migration, document upload + tag + keyword search + download with permission control, e-voting with ballots/votes/results, WhatsApp analytics dashboard from exported chats (activity, peak hours, sentiment, spam, influencers), email broadcasts + scheduled reminders, meeting CRUD with Zoom link + minutes, finance income/expense CRUD with summary, and the project report + demo.

### Reopening cuts

If by mid-June the team is ahead of schedule, the *first* item to bring back from this list is **password reset by email link** (real users will need it). The *second* is a **branded custom admin dashboard** for nicer demo screenshots. Everything else stays cut unless there's a strong reason.

---

## 9. Open questions to resolve in week 0

- Do we have access to a real WhatsApp chat export, or do we need to fabricate one for the demo?
- Is the 4,000-record export already available, or are we waiting on the organization?
- Are the 1,000 pages of documents real PDFs, or do we mock them with a representative sample?
- Who owns the Render account, the GitHub org, and the Jira/Confluence workspace? (One person — likely Lado — should own all three so access doesn't break when someone graduates.)
- Which Gmail account sends the broadcast emails? (Use a dedicated project Gmail, not someone's personal account.)

**Resolved:**
- Budget — zero. Free tier only. (Tech stack and hosting picks already reflect this.)
- Live demo strategy — local + ngrok on demo day; Render as the persistent URL between checkpoints.
- Hosting — Render free tier; managed Postgres on the same dashboard.
- Cross-domain rotation — primary owners stay stable, each dev takes one stretch ticket per sprint plus one cross-domain pairing.
