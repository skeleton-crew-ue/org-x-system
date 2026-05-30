# Contributing to Org X System

This is the canonical guide for how work gets into this repo. Read it once fully; after that, use the quick reference at the top.

**The golden rule:** nothing goes straight to `main`. Every change — code, docs, config, anything — goes through a feature branch and a pull request. Branch protection enforces this; even the repo owner follows it.

---

## Quick reference

```bash
git checkout main && git pull                       # 1. start fresh
git checkout -b feature/your-name/short-description  # 2. branch
# ...make changes...
git add <files> && git commit -m "Clear message"     # 3. commit (repeat as you go)
git push -u origin feature/your-name/short-description # 4. push
# 5. open PR on GitHub, fill in the template, request a reviewer
# 6. address review comments (push more commits to the same branch)
# 7. squash-merge via GitHub UI once approved
git checkout main && git pull                        # 8. sync up
```

---

## Before you start

You need a working local environment — see [`runbook.md`](runbook.md). You also need **Write** access to the repo (you're in the `devs` team). If `git push` is rejected with a permissions error, ask Lado to check your team membership.

---

## The workflow, step by step

### 1. Start from a fresh `main`

```bash
git checkout main
git pull
```

Always branch from the latest `main`. Branching from a stale `main` causes avoidable merge conflicts later.

### 2. Create a feature branch

```bash
git checkout -b feature/your-name/short-description
```

See [Branch naming](#branch-naming) below.

### 3. Work and commit

Make your changes. Commit in small, logical chunks as you go — not one giant commit at the end. Small commits are easier to review and easier to undo if something goes wrong.

```bash
git add path/to/changed/files
git commit -m "Add login view and template"
```

See [Commit messages](#commit-messages) below.

### 4. Keep your branch current

If `main` moves while you're working (someone else's PR merged), pull those changes into your branch so your eventual merge is clean:

```bash
git checkout main
git pull
git checkout feature/your-name/short-description
git merge main          # resolve any conflicts, then commit
git push
```

Do this before opening your PR, and again if your PR sits open for more than a day or two.

### 5. Push and open a PR

```bash
git push -u origin feature/your-name/short-description
```

The push output prints a link to open a PR — or use the GitHub UI. Target `main`. Fill in the **PR template** completely (what it does, how to test, linked Jira ticket, the checklist). Request a reviewer — see [Module ownership](#module-ownership--who-reviews-what).

### 6. Get reviewed

Your reviewer will approve, request changes, or leave comments. To address feedback, push more commits to the **same branch** — the PR updates automatically. Don't open a new PR. Once you've addressed everything, re-request review.

### 7. Merge

Once you have 1 approval, click **Squash and merge** in the GitHub UI. Squash keeps `main`'s history clean — your 8 work-in-progress commits become 1 tidy commit. The branch auto-deletes after merge.

### 8. Sync up

```bash
git checkout main
git pull
```

Now your local `main` has your merged change. Delete your local branch if you like (`git branch -d feature/...`); the remote one is already gone.

---

## Branch naming

Format: `feature/<your-name>/<short-description>`

Examples:
- `feature/mr-h/auth-login`
- `feature/mrs-d/document-upload`
- `feature/mr-t/finance-summary-chart`
- `feature/lado/whatsapp-parser`

Use `fix/` instead of `feature/` for bug fixes (`fix/mrs-d/vote-double-submit`). Keep the description short and lowercase-hyphenated.

---

## Commit messages

Keep them plain and useful:

- **Imperative mood:** "Add login view", not "Added" or "Adds login view".
- **Short summary line** (~50 characters). Add a blank line and a body only if you need to explain *why*.
- **Reference the Jira ticket** if there is one: `ORGX-42: Add login view`.

Good:
```
ORGX-15: Add Member profile edit view

Members can now update their phone and email. Admin-managed
fields (role, member_id) are read-only on this form.
```

Not useful: `update`, `fix stuff`, `asdf`, `changes`.

Don't adopt a heavy commit-convention scheme (conventional commits, etc.) — for this team, clear plain messages beat a convention people forget.

---

## Pull request guidelines

**Size.** Keep PRs **≤ 300 lines** of change where possible. If a PR has to be bigger, say why in the description. Big PRs get shallow reviews; small PRs get real ones.

**One concern per PR.** A PR should do one thing. Don't bundle "add the voting model" with "fix a typo in the navbar" — they're two PRs.

**Fill in the template.** The PR template isn't decoration. The "how to test it" section especially — your reviewer should be able to follow those steps and see your change work.

**Migrations ship with their model change.** If your PR changes a Django model, the generated migration file is committed *in the same PR*. Never separate them.

**Screenshots for UI changes.** Any template or styling change needs a before/after screenshot in the PR.

**Self-approval isn't possible.** GitHub won't let you approve your own PR, and the ruleset requires 1 approval — so every PR, including the repo owner's and including docs-only PRs, needs a teammate to click Approve. That's the discipline working; it takes the reviewer two minutes for a small PR.

---

## Code review

### As the author

- Open the PR early if you want feedback on direction — mark it as a **Draft** PR.
- Respond to every comment, even if just "done" or "good point, fixed in <commit>".
- Don't take review comments personally. The review is of the code, not of you.
- Don't merge until you have an approval *and* all conversations are resolved.

### As the reviewer

- Review within a day — a blocked teammate is worse than a context switch.
- Pull the branch and actually run it for anything non-trivial. Don't just read the diff.
- Be specific and kind. "This could be clearer" is useless; "rename `d` to `document` here" is useful.
- Distinguish blocking issues from nits. Prefix nits with "nit:" so the author knows what's optional.
- Approve when it's good enough, not when it's perfect. Perfect is the enemy of shipped.
- If you're the module owner, you're also checking it fits the architecture — flag schema or pattern drift.

---

## Before every push — checklist

(This mirrors [`runbook.md`](runbook.md) §12.)

1. Virtualenv activated.
2. `python manage.py check` passes.
3. `python manage.py test <app_you_changed>` passes.
4. You ran the app and clicked through the thing you changed.
5. `git status` — you are **not** committing `.env`, `db.sqlite3`, `__pycache__/`, `.venv/`, or any real/synthetic data files.
6. Commits are small with clear messages.

---

## Merge conflicts

Conflicts happen — they're normal, not a crisis. When `git merge main` reports a conflict:

1. Run `git status` to see which files conflict.
2. Open each file; find the `<<<<<<<`, `=======`, `>>>>>>>` markers.
3. Edit to the correct combined result; delete the markers.
4. `git add <file>` for each resolved file.
5. `git commit -m "<Description>"` to complete the merge.
6. `git push`.

If the conflict involves a **migration file** or you don't understand the conflict: stop, don't guess. Ping Lado or the module owner in Slack with the output of `git status`. A wrongly-resolved migration conflict is much harder to fix later than to prevent now.

Never `git push --force` to a shared branch. If you think you need to, ask first.

---

## Module ownership — who reviews what

Request the **primary owner** of the module you touched as your reviewer. Full ownership table is in [`Project_Plan_Org_X.md`](docs/Project_Plan_Org_X.md) §4.

| Area | Primary reviewer |
|---|---|
| `members` (auth, profile, migration), deployment | Mr H |
| `documents`, `voting` | Mrs D |
| `meetings`, `finance`, shared UI / `base.html` | Mr T |
| `whatsapp`, database schema, architecture | Lado |
| Project docs (plan, architecture, ERD) | Lado |
| Anything cross-cutting or you're unsure | Lado |

For a cross-domain stretch ticket, request *both* the module owner and your own primary owner.

---

## What this applies to

Everything. Code, templates, migrations, `requirements.txt`, the docs in this repo, this file itself. There is no category of change that skips the branch-and-PR flow. The workspace planning folder is not the repo — once a doc is in the repo, the repo version is authoritative and changes to it go through a PR like anything else.
