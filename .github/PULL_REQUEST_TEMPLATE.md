<!--
Thanks for opening a PR! Fill in the sections below.
Keep it short — a good PR description is two paragraphs, not an essay.
-->

## What this PR does

<!-- One paragraph. What problem does it solve, what user-visible behavior changes? -->

## How to test it

<!-- The reviewer should be able to follow these steps and see your change working. -->

1.
2.
3.

## Linked Jira ticket

<!-- e.g. ORGX-42 -->

---

## Pre-merge checklist

- [ ] My branch name follows `feature/<name>/<description>`
- [ ] PR is ≤ 300 lines (or I've explained in the description why it can't be smaller)
- [ ] `python manage.py check` passes
- [ ] `python manage.py test <app>` passes for the app(s) I changed
- [ ] If I changed a model, the migration is committed in this PR
- [ ] If I added a new template, it extends `base.html` and follows the namespacing convention
- [ ] If I added a new URL, it's namespaced (`<app>:<view>`) and reverse-able from templates
- [ ] If I added a Python dependency, I updated `requirements.txt` with a pinned version
- [ ] I have NOT committed `.env`, `db.sqlite3`, `__pycache__/`, or any real member/WhatsApp data
- [ ] Module owner (see README) is requested as reviewer

## Screenshots (if UI changed)

<!-- Drag images into the comment box. Required for any template change. -->

## Notes for the reviewer

<!-- Anything non-obvious, follow-ups you're deferring, decisions you're unsure about. -->
