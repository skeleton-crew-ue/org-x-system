# Organization X — Integrated Digital Management System

A Django-based web application that centralizes Organization X's member management, document storage, electronic voting, meeting coordination, financial records, and WhatsApp analytics.

**Status:** in development (Spring 2026 student project) · **Deadlines:** Frontend course 2026-07-09 · Agile course 2026-07-18

---

## Stack

- **Backend:** Python 3.12 + Django 5.2
- **Database:** PostgreSQL 16 (prod) · SQLite (local dev)
- **Frontend:** Bootstrap 5 + Chart.js, server-rendered Django templates
- **Hosting:** Render (free tier) · GitHub auto-deploy from `main`
- **Process:** GitHub + Jira + Confluence + Mailtrap (dev email)

---

## Getting started

New to the project? Open [`runbook.md`](runbook.md). It walks you from a clean laptop to a running local copy in about 30 minutes.

Quick version (assumes you've already done the prerequisites in the runbook):

```bash
git clone https://github.com/<org-name>/org-x-system.git
cd org-x-system
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # then fill in values
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data
python manage.py runserver
```

Open <http://localhost:8000>.

---

## Documentation

The four governance docs every dev should read in their first week:

| Doc | What's in it |
|---|---|
| [`Project_Plan_Org_X.md`](docs/Project_Plan_Org_X.md) | Team split, sprint plan, scope, deadlines |
| [`Architecture.md`](docs/Architecture.md) | Django apps, data model, key flows, tech choices |
| [`Database_ERD.md`](docs/Database_ERD.md) | Schema, fields, constraints, indexes |
| [`runbook.md`](runbook.md) | Local dev setup, daily workflow, troubleshooting |

If anything in the code disagrees with these docs, fix one of them in the same PR.

---

## Team

| Person | Role | Primary modules |
|---|---|---|
| Lado | Tech lead, Scrum Master, architect | WhatsApp analytics, DB design |
| Harsh | Developer | `members` (auth, profile, data migration), Render deployment |
| Thinley | Developer | `documents`, `voting` |
| Dana | Developer | `meetings`, `finance`, **shared UI** |
| Karim | Product Manager / BA | Backlog, AC, test scenarios, report |
| Asadbek | QA Engineer | Test cases, bug board, security pass |

Full ownership and stretch-ticket model: [`Project_Plan_Org_X.md`](docs/Project_Plan_Org_X.md) § 4.

---

## Contributing

Full workflow, conventions, and review process: **[`CONTRIBUTING.md`](CONTRIBUTING.md)**. Read it before your first PR.

The essentials:
- Nothing goes straight to `main` — every change is a feature branch + a pull request. Branch protection enforces this.
- Branch naming: `feature/<your-name>/<short-description>`.
- Keep PRs ≤ 300 lines; every model change ships with its migration in the same PR.
- Request review from the module owner (see team table above), squash-merge after approval.

```bash
git checkout main && git pull
git checkout -b feature/your-name/short-description
# ...work, commit...
git push -u origin feature/your-name/short-description
# open PR, fill in template, get 1 approval, squash-merge
```

---

## License

This is a student project. No license — not open source, not redistributable.
