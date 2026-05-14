# Organization X — Integrated Digital Management System

A Django-based web application that centralizes Organization X's member management, document storage, electronic voting, meeting coordination, financial records, and WhatsApp analytics.

**Status:** in development (Spring 2026 student project)

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
| [`Project_Plan_Org_X.md`](Project_Plan_Org_X.md) | Team split, sprint plan, scope, deadlines |
| [`Architecture.md`](Architecture.md) | Django apps, data model, key flows, tech choices |
| [`Database_ERD.md`](Database_ERD.md) | Schema, fields, constraints, indexes |
| [`runbook.md`](runbook.md) | Local dev setup, daily workflow, troubleshooting |

If anything in the code disagrees with these docs, fix one of them in the same PR.

---

## Team

| Person | Role | Primary modules |
|---|---|---|
| Mr G | Tech lead, Scrum Master, architect | WhatsApp analytics, DB design |
| Mr H | Developer | `members` (auth, profile, data migration), Render deployment |
| Mrs D | Developer | `documents`, `voting` |
| Mr T | Developer | `meetings`, `finance`, **shared UI** |
| Mr K | Product Manager / BA | Backlog, AC, test scenarios, report |
| Mr A | QA Engineer | Test cases, bug board, security pass |

Full ownership and stretch-ticket model: [`Project_Plan_Org_X.md`](Project_Plan_Org_X.md) § 4.

---

## Contributing

1. Create a feature branch: `feature/<your-name>/<short-description>` (e.g. `feature/mr-h/auth-login`).
2. Make your changes. Commit often, push when you're at a checkpoint.
3. Run `python manage.py check && python manage.py test <your_app>` before pushing.
4. Open a PR against `main`. Fill in the PR template.
5. Request review from the module owner (see table above).
6. After approval, squash-merge. Branch auto-deletes.

PR rules:
- Keep PRs ≤ 300 lines where possible.
- Every model change ships with its migration in the same PR.
- No commits directly to `main`. Branch protection enforces this.

---

## License

This is a student project. No license — not open source, not redistributable.
