# GitHub Repo Setup Guide

**Owner:** Lado · **Status:** Week 0 checklist · **Time required:** ~45 minutes

> **Historical record.** This guide documents the one-time GitHub setup and the reasoning behind it (public repo, squash-merge, team permissions, branch protection). The setup itself is done — this lives in `docs/` so anyone joining later can understand *why* the repo is configured the way it is. The `_repo_starter/` folder it refers to was a temporary staging folder used during planning; its contents are now this repo.

This is the one-time setup to create the team's GitHub repo and lock the basics. Walk through it top to bottom; the starter files referenced lived in `_repo_starter/` during planning and were committed in step 4.

---

## 1. Create a GitHub organization (5 min)

Why an org rather than a personal repo: ownership outlives any one student, you can transfer the repo to the university or a teammate later without losing history, and the GitHub Free plan for orgs includes unlimited public and private repos with unlimited collaborators.

1. Sign in to GitHub with your personal account (Lado).
2. Click your avatar (top right) → **Your organizations** → **New organization**.
3. Pick the **Free** plan.
4. **Organization name:** something stable and distinct, e.g. `org-x-system-team` or `orgx-2026`. You can't easily change this later; pick something the examiner can find.
5. **Contact email:** the project Gmail (the dedicated team account, not your personal email).
6. Skip the "invite members" screen for now — we'll do it deliberately in step 3.

---

## 2. Create the repo (5 min)

1. From the new org, click **New repository**.
2. **Name:** `org-x-system` (lowercase, hyphenated — this becomes the URL slug).
3. **Description:** "Integrated Digital Management System for Organization X — student project, Spring 2026."
4. **Visibility:** **Public**. Two reasons: branch protection rulesets only enforce for free on *public* repos (private repos need paid GitHub Team — see step 5), and all project data is synthetic so there's no PII to leak. The hard team rule that makes this safe: **synthetic data only — no real member records or WhatsApp exports ever get committed.** The `.gitignore` blocks the data paths as a backstop, but the discipline is what matters.
5. **Initialize with:**
   - ✓ Add a README
   - ✓ Add `.gitignore` → choose **Python** (we'll overwrite this in step 4 with our customized version)
   - ✗ Don't add a license (skip — class project, doesn't matter)
6. Click **Create repository**.

---

## 3. Add team members with the right permissions (10 min)

The model: everyone is a collaborator with write access, but the repo's **branch protection rule** (set in step 5) prevents anyone from pushing straight to `main`. So everyone can branch and PR; only the merge requires review.

1. From the repo, go to **Settings → Collaborators and teams**.
2. **Create one team per role** so you can grant permissions in bulk and they survive people coming and going:
   - **`devs`** team — Mr H, Mrs D, Mr T, Lado. Permission: **Write**.
   - **`reviewers`** team — Lado (you). Permission: **Maintain**.
   - **`observers`** team — Mr K, Mr A. Permission: **Triage** (can comment on PRs, manage issues, but not push code).
3. Invite each teammate by their GitHub username. They'll get an email; chase them to accept before sprint 1.
4. **Owners of the org:** add Lado as Owner. Don't add anyone else as Owner — too much power, no need.

> If `Triage` feels too restrictive for Mr K and Mr A (e.g. they want to push the seed-data script or test fixtures), bump them to **Write** but remind them that nothing they push goes to `main` without your review anyway.

---

## 4. Commit the starter files (10 min)

The `_repo_starter/` folder in this workspace has the files this project needs from day one. Drag them into your local clone of the repo.

> **Order matters:** this step assumes branch protection (step 5) is **not yet active** — the direct `git push origin main` below is the intentional bootstrap commit. If you've already done step 5, that direct push will be rejected. In that case, do this step on a feature branch and open a PR instead (see [`CONTRIBUTING.md`](../CONTRIBUTING.md) — it's the first real exercise of the workflow). Either order is fine; just match the push method to whether protection is on.

```bash
# Clone the repo locally:
cd ~/code
git clone https://github.com/<org-name>/org-x-system.git
cd org-x-system

# Copy the starter files in (paths assume Mac/Linux — adjust for Windows):
cp -r ~/Documents/Claude/Projects/"Skeleton dev project"/_repo_starter/. .

# Sanity-check what got added:
git status

# You should see:
#   modified:   .gitignore   (overwritten with our version)
#   modified:   README.md    (overwritten with our version)
#   new file:   .github/PULL_REQUEST_TEMPLATE.md
#   new file:   CONTRIBUTING.md

# Commit and push:
git add .
git commit -m "Add project starter files: README, .gitignore, PR template, CONTRIBUTING"
git push origin main
```

After this push, the repo has the bones. The actual Django code arrives in step 6 (Mr H's `django-admin startproject` scaffolding).

---

## 5. Set up branch protection on `main` (5 min)

This is the one rule that catches half the bad habits an inexperienced team would otherwise drift into.

> **Why this needs a public repo:** GitHub's Free plan for orgs does **not** enforce branch protection rulesets on *private* repos — only on public ones (or with paid GitHub Team). Because this repo is public (step 2), the ruleset below enforces for free. If the repo is ever made private, the ruleset stays configured but silently stops enforcing until the org upgrades — so you'd see a warning banner on the Rulesets page.

1. In the repo, go to **Settings → Branches**.
2. Click **Add branch ruleset** (or **Add rule** on older UIs).
3. **Ruleset name:** `main protection`.
4. **Target branches:** `main`.
5. **Enable these rules:**
   - ✓ **Require a pull request before merging** — set required approvals to **1**.
   - ✓ **Dismiss stale pull request approvals when new commits are pushed** — forces re-review if someone changes code after approval.
   - ✓ **Block force pushes** — prevents accidental history rewrites.
   - ✗ **Require status checks to pass** — skip for now; we'll turn this on when CI lands in sprint 2.
   - ✗ **Require signed commits** — not worth the friction for this team.
   - ✓ **Restrict deletions** — nobody can delete `main`.
6. **Bypass list:** leave empty. Even you should PR your own changes. (If you genuinely need to push directly in an emergency, you can temporarily disable the ruleset.)
7. Save.

Test it: try to push to `main` directly from your laptop. GitHub should reject it. Good.

---

## 6. Repo settings tweaks (5 min)

In **Settings → General**:

- **Pull Requests** section:
  - ✗ Allow merge commits
  - ✓ Allow squash merging — **make this the default merge method**. Squash keeps `main`'s history clean even when devs make 12 messy work-in-progress commits per PR.
  - ✗ Allow rebase merging
  - ✓ Always suggest updating pull request branches
  - ✓ Automatically delete head branches — keeps the branch list manageable.

- **Issues** section:
  - ✗ Disable Issues — we're using Jira for tickets. (If you want a fallback channel for things that don't belong in Jira, leave Issues enabled but tell the team not to use it for sprint work.)

- **Discussions** section:
  - ✗ Disable — not needed.

---

## 7. Confirm Mr H is ready to scaffold Django (next step, not now)

After the above is done, the repo is ready for Mr H's week-0 scaffolding work:

1. `django-admin startproject config .`
2. Create the seven app skeletons (`python manage.py startapp members`, etc.)
3. Add `requirements.txt` and `.env.example` (referenced by the runbook).
4. First migration with the custom `User` model.
5. "Hello world" deployed to Render.
6. Push to a feature branch, open a PR for review.

Don't do this yourself — it's Mr H's deliverable and the first opportunity for him to use the PR workflow. Just make sure he has write access and knows the next move.

---

## 8. What's deferred (not now)

These come later, deliberately:

- **GitHub Actions CI** — wait until Mr H has `requirements.txt` and one passing test. Then add a workflow that runs `python manage.py check` and `makemigrations --check --dry-run` on every PR.
- **Issue templates** — skipped because we're using Jira.
- **Custom labels** — GitHub defaults are fine.
- **CODEOWNERS file** — useful when the team is bigger; for six people, comments in PR template + Slack mentions cover it.
- **GitHub Pages / docs site** — not needed; docs live in the repo as markdown.
- **Dependabot** — useful but noisy; defer until you have a stable `requirements.txt`.
- **Secret scanning** — already on by default for private repos.

---

## 9. Checklist (tick as you go)

- [ ] GitHub org created (Free plan, project-Gmail contact)
- [ ] Repo `org-x-system` created, **Public**, with README + Python `.gitignore`
- [ ] Three teams created: `devs`, `reviewers`, `observers`
- [ ] Team permissions assigned: `devs` Write, `reviewers` Maintain, `observers` Triage
- [ ] All 5 teammates invited and (eventually) accepted
- [ ] Lado is org Owner; nobody else is
- [ ] Starter files committed to `main` (README, .gitignore, PR template)
- [ ] Branch protection ruleset on `main`: PR required, 1 approval, no force push, no delete
- [ ] Ruleset confirmed enforcing (no "won't be enforced" warning; direct push to `main` rejected)
- [ ] Squash-merge set as default; auto-delete branches enabled
- [ ] Issues disabled (we use Jira)
- [ ] Team briefed: **synthetic data only** — no real PII in a public repo, ever
- [ ] Mr H knows he's up next for the Django scaffolding

When all ticked, drop a message in the team channel: "Repo is live at <URL>. Mr H, you're up — `django-admin startproject` and PR it. Everyone else, accept your GitHub invite if you haven't."
