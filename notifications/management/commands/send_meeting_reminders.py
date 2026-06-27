"""
Management command: send_meeting_reminders

Sends a reminder email to every active member for each SCHEDULED meeting
that starts between 12 and 36 hours from now.

Designed to be run once daily by a cron job on Render.

Usage:
    python manage.py send_meeting_reminders
    python manage.py send_meeting_reminders --dry-run
"""

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from meetings.models import Meeting
from members.models import User

import datetime


class Command(BaseCommand):
    help = "Send reminder emails for meetings starting in 12–36 hours"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be sent without actually sending emails",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        now     = timezone.now()

        window_start = now + datetime.timedelta(hours=12)
        window_end   = now + datetime.timedelta(hours=36)

        meetings = Meeting.objects.filter(
            status="SCHEDULED",
            scheduled_at__gte=window_start,
            scheduled_at__lte=window_end,
        )

        if not meetings.exists():
            self.stdout.write("No meetings in the 12–36 hour window. Nothing to send.")
            return

        recipients = User.objects.filter(
            is_active=True,
        ).exclude(email="").values_list("email", flat=True)

        recipient_list = list(recipients)

        if not recipient_list:
            self.stdout.write("No active members with email addresses found.")
            return

        total_sent = 0
        total_errors = 0

        for meeting in meetings:
            subject = f"Reminder: {meeting.title} is coming up"

            # Build a plain-text reminder body
            when = meeting.scheduled_at.strftime("%A, %d %B %Y at %H:%M %Z")
            location = meeting.location_or_link or "TBC"
            body = (
                f"Hi,\n\n"
                f"This is a reminder that the following meeting is scheduled soon:\n\n"
                f"  Title:    {meeting.title}\n"
                f"  When:     {when}\n"
                f"  Where:    {location}\n"
                f"  Duration: {meeting.duration_minutes} minutes\n"
            )
            if meeting.description:
                body += f"\n  Details:  {meeting.description}\n"

            body += (
                f"\nPlease make sure you are prepared and on time.\n\n"
                f"– Org X System"
            )

            if dry_run:
                self.stdout.write(
                    f"[DRY RUN] Would send '{subject}' to {len(recipient_list)} recipients"
                )
                continue

            for email in recipient_list:
                try:
                    send_mail(
                        subject=subject,
                        message=body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=False,
                    )
                    total_sent += 1
                except Exception as e:
                    self.stderr.write(f"Failed to send to {email}: {e}")
                    total_errors += 1

        if not dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"Reminders sent: {total_sent} | Errors: {total_errors}"
            ))
