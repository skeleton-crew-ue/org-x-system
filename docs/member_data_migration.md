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
| `email` | Yes | Lowercased; invalid or duplicate rows are skipped |
| `first_name` | Yes | Stored on the User model |
| `last_name` | Yes | Stored on the User model |
| `member_id` | No | Auto-generated as `M-<row_index>` if blank |
| `phone` | No | 9-digit Georgian numbers prefixed with `+995` |
| `joined_at` | No | Parsed with `dateutil`; set to NULL on failure |

## Cleaning Rules

- Trim leading/trailing whitespace from all fields.
- Convert email addresses to lowercase.
- Skip rows with a blank or malformed email address.
- Skip rows with a duplicate email (first record wins; later duplicates are
  skipped with a warning line in stdout).
- Auto-generate `member_id` values for rows where the field is blank.
- Normalise Georgian phone numbers: 9-digit numbers are prefixed with `+995`.
- Set `joined_at` to NULL when the date string cannot be parsed.

## Username Scheme

The full email address is used directly as the username with no
transformation. Django's default username validator permits `@` and `.`, so
`bob@gmail.com` is a valid username. Uniqueness beyond what the email field
already guarantees is handled by `clean_email()` in `RegistrationForm` and by
the duplicate-email check in the importer.

## Duplicate-Email Handling

One account per email address is the rule across the entire codebase:

- `RegistrationForm.clean_email()` rejects registration attempts with an
  already-used email.
- The importer always skips rows whose email already exists in the database
  (first record wins).
- `EmailBackend` uses `filter().first()` as a safety net so that if a
  duplicate somehow exists, authentication degrades gracefully instead of
  raising `MultipleObjectsReturned`.

## Running the Importer

```bash
# Dry run — no database writes
python manage.py import_members path/to/members.csv --dry-run

# Live import
python manage.py import_members path/to/members.csv
```

## Decision Log

- Synthetic dataset used because no production member data was available.
- Duplicate emails are always skipped (no flag required); first record wins.
- Invalid emails are skipped with a warning line in stdout.
- Missing `member_id` values are auto-generated.
- `members_dump.json` was removed from branch history before merging to avoid
  committing member data to the repository.