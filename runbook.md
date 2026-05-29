# Org X System — Local Development Runbook

**Owner:** Vladimer + Harsh · **Status:** Draft v0.2 · **Last updated:** 2026-05-27

This document gets you from a clean laptop to a running local copy of the app. Follow it top to bottom — every step has a purpose. If something fails, check the **Troubleshooting** section at the end before pinging Slack.

**What you'll have at the end:** the app running at <http://localhost:8000> with demo data loaded, ready for you to start coding.

**Time required:** 30–45 minutes if everything goes smoothly. First time setting up a Python project? Budget 90 minutes and don't panic.

**Operating systems:** Windows 10/11, macOS 13+, Ubuntu 22.04+. Commands are shown for all three; pick yours and ignore the others.

---

## 0. Before you start

You need:
- A laptop with admin/sudo rights to install software
- Internet connection
- ~3 GB free disk space
- **VS Code** (assumed installed — if not, get it from <https://code.visualstudio.com/>)
- Your GitHub username

---

## 1. Install Python 3.12

We use **Python 3.12.x** (any patch version, e.g. 3.12.3, 3.12.7). Not 3.11, not 3.13 — sticking to one major version avoids "works on my machine" bugs.

Why 3.12: Django 5.2 (our framework) supports Python 3.10–3.13, but 3.12 is the most widely tested combination as of mid-2026 and matches what Render runs in production.

### Windows

1. Go to <https://www.python.org/downloads/release/python-3127/> (or the latest 3.12.x).
2. Download **Windows installer (64-bit)**.
3. Run the installer. **Critical:** check the box **"Add python.exe to PATH"** on the first screen, then click **Install Now**.
4. Open a fresh PowerShell (close any open ones first) and verify:
   ```powershell
   python --version
   ```
   Expected output: `Python 3.12.x`

### macOS

```bash
# Install Homebrew first if you don't have it (https://brew.sh):
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then Python:
brew install python@3.12

# Verify:
python3.12 --version
```
Expected output: `Python 3.12.x`

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip

# Verify:
python3.12 --version
```

> **Note:** on macOS and Linux the binary is `python3.12` (or `python3`); on Windows it's `python`. Inside a virtualenv (Step 4) both become just `python` — that's the form used in the rest of this runbook.

---

## 2. Install Git

If you've used GitHub before, skip this — `git --version` will tell you.

### Windows

1. Download from <https://git-scm.com/download/win>.
2. Run the installer. Accept the defaults *except*: when asked about the default editor, pick **Use Visual Studio Code as Git's default editor**.
3. The installer also gives you **Git Bash** — a unix-style terminal we recommend over PowerShell for git commands.
4. Verify (in a fresh terminal): `git --version`

### macOS

```bash
brew install git
git --version
```

### Linux

```bash
sudo apt install -y git
git --version
```

### One-time Git config (all platforms)

```bash
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"   # use your GitHub email
git config --global init.defaultBranch main
git config --global pull.rebase false              # merge on pull, not rebase
```

---

## 3. (Optional) Install PostgreSQL 16

**You can skip this for initial setup but you should have it already from previous courses.** The app runs on SQLite locally by default — you only need Postgres if you want to test against the same database we use in production. Plan to install it before sprint 2 (when document full-text search lands, which is Postgres-only).

### Windows

1. Download the installer from <https://www.postgresql.org/download/windows/> (use the EnterpriseDB build, version 16.x).
2. During install, set the **postgres user password** to something you'll remember and write it down. Use `5432` as the port.
3. The installer offers Stack Builder at the end — skip it.
4. Verify: open `pgAdmin` from the Start menu; you should be able to connect to "PostgreSQL 16" using the password you set.

### macOS

```bash
brew install postgresql@16
brew services start postgresql@16

# Create a database user matching your macOS user (one-time):
createuser -s $(whoami)

# Verify:
psql postgres -c "SELECT version();"
```

### Linux

```bash
sudo apt install -y postgresql-16
sudo systemctl enable --now postgresql

# Create a database user matching your Linux user (one-time):
sudo -u postgres createuser -s $(whoami)

# Verify:
psql postgres -c "SELECT version();"
```

### Create the project database (all platforms, after Postgres is installed)

```bash
createdb org_x_system
```

If `createdb` fails on Windows, open `pgAdmin` and create a database named `org_x_system` through the GUI.

---

## 4. Get the code and set up the Python environment

### 4.1 Clone the repo

Pick a folder for your code (e.g. `~/code` on Mac/Linux, `C:\code` on Windows) and:

```bash
cd ~/code                                                 # or your chosen folder
git clone https://github.com/skeleton-crew-ue/org-x-system.git
cd org-x-system
```

### 4.2 Create a virtual environment

A virtualenv is an isolated Python install for this project so its libraries don't collide with anything else on your machine. Always activate it before working on this project.

```bash
# Create:
python3.12 -m venv .venv          #  or your latest version macOS / Linux
py -3.12 -m venv .venv            # Windows (use this if `python` defaults to a different version)

# Activate:
source .venv/bin/activate         # macOS / Linux
.venv\Scripts\activate            # Windows PowerShell
.venv\Scripts\activate.bat        # Windows cmd
source .venv/Scripts/activate     # Windows Git Bash
```

Your shell prompt should now start with `(.venv)`. From here on, `python` and `pip` refer to the virtualenv's versions.

> **Daily reminder:** every time you open a new terminal to work on this project, run the activate command again. If you forget, `pip install` will pollute your global Python.

### 4.3 Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs everything listed in `requirements.txt`, including:

| Library | Why we have it |
|---|---|
| `Django==5.2.*` | The web framework. |
| `psycopg[binary]==3.2.*` | PostgreSQL driver. (Harmless if you're only using SQLite.) |
| `django-environ==0.11.*` | Reads settings from `.env` files. |
| `gunicorn==23.0.*` | Production WSGI server (used on Render). |
| `whitenoise==6.7.*` | Serves static files in production. |
| `Pillow==10.4.*` | Image handling for `ImageField` / file uploads. |
| `django-crispy-forms==2.3` + `crispy-bootstrap5==2024.*` | Nicer form rendering with Bootstrap. |
| `pandas==2.2.*` | Data cleaning for the member-migration script and WhatsApp analytics. |
| `vaderSentiment==3.3.*` | Sentiment analysis for WhatsApp module. |
| `python-dateutil==2.9.*` | Parsing WhatsApp export timestamps. |
| `python-decouple==3.8` *(optional alternative to django-environ)* | — |

Verify Django installed correctly:

```bash
python -m django --version
```
Expected: `5.2.x`

---

## 5. Configure environment variables

The app reads configuration from a `.env` file in the project root. We never commit real `.env` files (they contain secrets) — instead the repo has a `.env.example` you copy and fill in.

```bash
cp .env.example .env              # macOS / Linux / Git Bash
copy .env.example .env            # Windows PowerShell / cmd
```

Open `.env` in VS Code and set these values:

```ini
# Required
DEBUG=True
SECRET_KEY=dev-not-a-real-secret-do-not-use-in-prod
ALLOWED_HOSTS=localhost,127.0.0.1

# Database — pick ONE
DATABASE_URL=sqlite:///db.sqlite3
# DATABASE_URL=postgres://yourname@localhost:5432/org_x_system    # if using Postgres

# Email (use Mailtrap for local dev — free fake-SMTP, never sends real emails)
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_HOST_USER=ask-later # ask Vladimer later
EMAIL_HOST_PASSWORD=ask-later # ask Vladimer later
DEFAULT_FROM_EMAIL=Org X Dev <noreply@orgx.local>

# Time zone
TIME_ZONE=Europe/Berlin
```

> **Why Mailtrap?** When you're testing the broadcast feature, you don't want it accidentally emailing 4,000 real members. Mailtrap is a free service that catches every email your app tries to send and shows them in a web inbox you can open. Harsh will later set up the team account and shares the credentials in Teams.

> **Don't commit your `.env`.** It's in `.gitignore` already, but double-check before any push. Real secrets in git history are painful to scrub.

---

## 6. Set up the database

### 6.1 Run migrations

Migrations create the tables defined by our Django models.

```bash
python manage.py migrate
```

You should see a list of "Applying ..." lines ending in `OK`. If anything says `FAILED`, jump to **Troubleshooting**.

### 6.2 Create a superuser (admin login)

```bash
python manage.py createsuperuser
```

When prompted:
- **Username:** anything you'll remember (e.g. your first name)
- **Email:** your real email
- **Password:** anything ≥8 characters — this is local-only, security doesn't matter here

### 6.3 Load seed data  -- Skip for the initial setup, will be useful later

```bash
python manage.py seed_data
```

This populates the database with demo users, documents, ballots, meetings, transactions, and a sample WhatsApp analysis — enough to click around and see all the modules working without manually creating data first.

You should see something like:
```
Created 5 admins, 20 members
Created 6 documents across 3 tags
Created 2 ballots (1 open, 1 closed)
Created 4 meetings
Created 15 transactions across 5 categories
Created 1 ChatExport with sample analysis
Done in 4.2s
```

> **Tip:** running `seed_data` again wipes and re-creates the demo data, so you can always get back to a clean state if you mess something up locally. (It does *not* delete the superuser you just created — only the demo accounts.)

---

## 7. Run the server

```bash
python manage.py runserver
```

Expected output:
```
Watching for file changes with StatReloader
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Open <http://localhost:8000> in your browser. You should see the home page with a login link. Log in as your superuser → you should land on a dashboard with cards for each module.

Also try <http://localhost:8000/admin/> — you should see the Django Admin interface listing every model.

🎉 **You're done with setup.** Press `Ctrl+C` in the terminal to stop the server when you want to take a break.

---

## 8. Daily workflow

Every time you sit down to code on this project:

```bash
cd ~/code/org-x-system          # 1. Move into the project folder
source .venv/bin/activate       # 2. Activate the virtualenv (Windows: .venv\Scripts\activate)
git pull                        # 3. Get the latest code from main
pip install -r requirements.txt # 4. In case dependencies changed (safe to run anytime)
python manage.py migrate        # 5. In case the schema changed
python manage.py runserver      # 6. Start the server
```

If `git pull` shows changes to `requirements.txt` or any `migrations/` folder, you must run steps 4 and 5 before the server. Most days you can skip them, but it's safer to always run.

When you're done for the day, just `Ctrl+C` to stop the server and close the terminal. The virtualenv stays on disk; you'll re-activate it next time.

---

## 9. VS Code setup (recommended)

Install these extensions (open VS Code → Extensions panel → search and install each):

- **Python** (Microsoft) — syntax, IntelliSense, debugger
- **Pylance** (Microsoft) — better type checking; comes auto-installed with Python
- **Django** (Baptiste Darthenay) — template syntax highlighting
- **GitLens** (GitKraken) — better git integration
- **Black Formatter** (Microsoft) — auto-format on save *(optional but recommended)*

After installing the Python extension, open the project folder in VS Code and:

1. **`Ctrl+Shift+P`** → type **"Python: Select Interpreter"** → pick the one in `.venv/` (it'll say `Python 3.12.x ('.venv': venv)`).
2. Open a terminal in VS Code (**`Ctrl+`** backtick). It should auto-activate the virtualenv — your prompt starts with `(.venv)`.
3. Add this to `.vscode/settings.json` in the project root (commit it — it's shared team config, not secrets):
   ```json
   {
     "python.defaultInterpreterPath": ".venv/bin/python",
     "python.terminal.activateEnvironment": true,
     "files.exclude": {
       "**/__pycache__": true,
       "**/.venv": true
     },
     "[python]": {
       "editor.formatOnSave": true,
       "editor.defaultFormatter": "ms-python.black-formatter"
     }
   }
   ```
   On Windows, change the interpreter path to `".venv/Scripts/python.exe"`.

---

## 10. Troubleshooting

### `python: command not found` (or `'python' is not recognized`)

- **Windows:** the "Add to PATH" checkbox was missed during install. Re-run the installer, choose **Modify**, check the box.
- **Mac/Linux:** use `python3.12` or `python3` instead of `python`. Inside the virtualenv, plain `python` works.

### `port 8000 is already in use`

Another process (probably an earlier `runserver` you forgot to stop) is holding the port. Either kill it or use a different port:

```bash
python manage.py runserver 8001
```

To find and kill the existing process:

```bash
# Mac / Linux:
lsof -i :8000
kill <PID>

# Windows PowerShell:
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
Stop-Process -Id <PID>
```

### `psycopg.OperationalError: connection to server ... failed`

You set `DATABASE_URL` to Postgres but Postgres isn't running, or the database doesn't exist.

```bash
# Mac:    brew services start postgresql@16
# Linux:  sudo systemctl start postgresql
# Windows: open Services → start "postgresql-x64-16"

# Then ensure the database exists:
createdb org_x_system
```

If you don't need Postgres yet, switch back to SQLite by setting `DATABASE_URL=sqlite:///db.sqlite3` in `.env`.

### `ModuleNotFoundError: No module named 'django'` (or any other library)

Your virtualenv isn't activated. Run the activate command (Step 4.2) and try again. If activation works but the import still fails:

```bash
pip install -r requirements.txt
```

### `django.db.utils.OperationalError: no such table: ...`

You haven't run migrations. Run `python manage.py migrate`.

### `CSRF verification failed` when submitting a form

You're submitting a form from a host other than `localhost`/`127.0.0.1`. Check `ALLOWED_HOSTS` in `.env` and `CSRF_TRUSTED_ORIGINS` in `settings.py`.

### `permission denied` when activating the venv on Windows PowerShell

PowerShell's execution policy is blocking the activate script. One-time fix:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Then close and reopen PowerShell.

### Migrations conflict (`CommandError: Conflicting migrations detected`)

Two devs created migrations from the same parent. Don't try to merge them by hand. Run:

```bash
python manage.py makemigrations --merge
```

Then commit the new merge migration. Tell the team in Slack.

### `git pull` shows merge conflicts I don't understand

Stop. Don't `git push --force` anything. Ping Mr H or Lado in Slack with the output of `git status`.

### Anything else

1. Read the full error message — Python tracebacks are long but the relevant line is usually near the bottom.
2. Search the exact error text on Google (or Stack Overflow). Django has been around 19 years; almost any error you hit has been hit before.
3. If still stuck after 20 minutes, paste the error in the Teams channel. **Include:** what you were doing, the full error, your OS, and whether your virtualenv is activated.

---

## 11. Useful commands cheat sheet

```bash
# Start the server
python manage.py runserver

# Make a migration after changing a model
python manage.py makemigrations
python manage.py migrate

# Open a Python shell with Django loaded (great for poking at models)
python manage.py shell

# Wipe and re-seed the demo data
python manage.py seed_data

# Run all tests
python manage.py test

# Collect static files (needed before deploy, not for local dev)
python manage.py collectstatic

# Check for problems
python manage.py check
```

---

## 12. What to do *before* every push

1. Activate your venv if you haven't.
2. `python manage.py check` — catches most config errors.
3. `python manage.py test <app_you_changed>` — runs tests for that app.
4. `python manage.py runserver` — open the page you changed and click around for 30 seconds.
5. `git status` — make sure you're not committing `.env`, `db.sqlite3`, `__pycache__/`, or `.venv/`.
6. Small commits, descriptive messages. PRs ≤ 300 lines (per the project plan).
7. Push to a feature branch (`feature/<your-name>/<short-description>`), open a PR, request review from the module owner (see `docs/Project_Plan_Org_X.md` § 4).

That's the whole workflow. Welcome to the project.
