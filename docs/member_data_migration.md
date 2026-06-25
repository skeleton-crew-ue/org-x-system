# Member Data Migration

## Overview

This document describes the cleaning rules applied during CSV member import
and the design decisions made for the `feature/harsh/member-data-migration`
branch.

## CSV Format Expected

The importer (`members/management/commands/import_members.py`) expects a CSV
with at least the following columns:

| Column | Required | Notes |
|---|---|---|
| `email` | Yes | Lowercased; invalid rows are skipped |
| `first_name` | Yes | Stored on the User model |
| `last_name` | Yes | Stored on the User model |
| `member_id` | No | Auto-generated as `M-<row_index>` if blank |
| `phone` | No | 9-digit Georgian numbers prefixed with `+995` |
| `joined_at` | No | Parsed with `dateutil`; set to NULL on failure |

## Cleaning Rules

- Trim leading/trailing whitespace from all fields.
- Convert email addresses to lowercase.
- Skip rows with a blank or malformed email address.
- Skip rows with a duplicate email when `--skip-existing` is passed (first
  record wins; later duplicates are silently skipped).
- Auto-generate `member_id` values for rows where the field is blank.
- Normalise Georgian phone numbers: 9-digit numbers are prefixed with `+995`.
- Set `joined_at` to NULL when the date string cannot be parsed.

## Username Scheme

Usernames are derived from the **full email address** — not just the local
part before `@` — to prevent collisions between accounts that share a local
part but use different domains (e.g. `bob@gmail.com` vs `bob@outlook.com`).

The transformation is:

```
bob@gmail.com  →  bob_at_gmail_com
```

This scheme is consistent across:

- `RegistrationForm.save()` in `members/forms.py`
- `ProfileEditForm.save()` in `members/forms.py`
- `import_members` management command

## Duplicate-Email Handling

The `EmailBackend` in `members/backends.py` authenticates users by email.
It uses `filter().first()` rather than `get()` so that if duplicate email
rows exist in the database (e.g. from a failed import run), authentication
degrades gracefully instead of raising `MultipleObjectsReturned`.

To prevent duplicates from being created in the first place, always run the
importer with `--skip-existing`.

## Decision Log

- Synthetic dataset used because no production member data was available.
- Duplicate emails are skipped (first record wins) when `--skip-existing` is
  set; without the flag the command will attempt to create all rows and may
  fail on unique-email constraints.
- Invalid emails are skipped with a warning line in stdout.
- Missing `member_id` values are auto-generated.
- The `members_dump.json` fixture was removed from the branch before merging
  to avoid committing potentially sensitive member data.