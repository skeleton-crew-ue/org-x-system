# Notifications – Email Broadcasts & Meeting Reminders

## Overview

The `notifications` app provides two features:

1. **Admin broadcast emails** — an admin composes and sends an email to a
   filtered group of members via the web UI.
2. **Meeting reminder emails** — a management command sends automated
   reminder emails for meetings starting in the next 12–36 hours, run
   daily by a cron job on Render.

---

## Broadcast Emails

### Pages

| URL | View | Who can access |
|---|---|---|
| `/notifications/compose/` | Compose page | Admins only |
| `/notifications/history/` | History page | Admins only |

Members attempting to access either page are redirected with a 403.

### Recipient Filters

| Filter | Who receives the email |
|---|---|
| `ALL` | Every user in the database with an email address |
| `ACTIVE` | Only users where `is_active=True` |
| `ADMINS` | Only users where `role="ADMIN"` |

### Broadcast Model

Each send creates a `Broadcast` record with:
- `subject`, `body` — the email content
- `recipient_filter` — which filter was used
- `sent_by` — the admin who sent it
- `sent_at` — timestamp (auto)
- `recipient_count` — how many emails were successfully sent

### Navbar link

The "Broadcasts" link in the navbar is only visible to admins
(`user.role == 'ADMIN'`).

---

## Meeting Reminder Emails

### Command

```bash
# Send reminders for meetings starting in 12–36 hours
python manage.py send_meeting_reminders

# Dry run — prints what would be sent, no emails dispatched
python manage.py send_meeting_reminders --dry-run
```

### Logic

- Queries `Meeting` objects with `status="SCHEDULED"` and
  `scheduled_at` between `now + 12h` and `now + 36h`.
- Sends one reminder email per meeting to every active member
  (`is_active=True`) who has an email address.
- Failures for individual recipients are logged to stderr and do not
  abort the rest of the send.

### Cron job on Render

Defined in `render.yaml` as a `cron` service:

```
schedule: "0 8 * * *"   # 08:00 UTC daily
```

At 08:00 UTC the command runs and covers any meeting scheduled between
20:00 that evening and 20:00 the following day — a comfortable 12–36 hour
window.

---

## Email Configuration

Settings are read from environment variables (see `.env.example`):

| Variable | Description |
|---|---|
| `EMAIL_HOST` | SMTP host (e.g. `sandbox.smtp.mailtrap.io` for dev) |
| `EMAIL_PORT` | SMTP port (default `587`) |
| `EMAIL_HOST_USER` | SMTP username |
| `EMAIL_HOST_PASSWORD` | SMTP password |
| `DEFAULT_FROM_EMAIL` | From address shown on emails |

### Local development with Mailtrap

1. Sign up at [mailtrap.io](https://mailtrap.io) and open your inbox.
2. Copy the SMTP credentials and add them to your `.env`:

```
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_PORT=587
EMAIL_HOST_USER=<your mailtrap username>
EMAIL_HOST_PASSWORD=<your mailtrap password>
DEFAULT_FROM_EMAIL=noreply@orgx.local
```

3. Emails will appear in your Mailtrap inbox instead of being delivered.

If `EMAIL_HOST` is not set, Django falls back to
`console.EmailBackend` — emails are printed to the terminal.

---

## How to Test

**Broadcasts**
1. Log in as an admin.
2. Go to `/notifications/compose/`.
3. Select a recipient filter, fill in subject and body, click Send.
4. Check Mailtrap inbox for the emails.
5. Go to `/notifications/history/` — the broadcast should appear.
6. Log in as a regular member and attempt to visit `/notifications/compose/` — should be blocked.

**Meeting reminders**
1. Create a `Meeting` in Django admin with `status=SCHEDULED` and
   `scheduled_at` set to 20 hours from now.
2. Run: `python manage.py send_meeting_reminders --dry-run`
   — should print the meeting title and recipient count.
3. Run without `--dry-run` and check Mailtrap for the reminder email.
4. Set `scheduled_at` to 40 hours from now and re-run — meeting should
   be skipped (outside the 12–36 hour window).
