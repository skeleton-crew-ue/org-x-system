# Member Data Migration – Cleaning Rules

## Cleaning Rules

- Trim whitespace
- Convert emails to lowercase
- Remove blank emails
- Remove invalid emails
- Remove duplicate emails
- Generate missing member IDs
- Normalize phone numbers
- Set invalid dates to NULL

## Decision Log

- Synthetic dataset used because no production member data was available.
- Duplicate emails removed.
- Invalid emails skipped.
- Missing member IDs generated automatically.