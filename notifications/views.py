import logging
import threading

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import get_connection, EmailMessage
from django.shortcuts import redirect, render
from django.conf import settings

from core.decorators import admin_required
from members.models import User
from .forms import BroadcastForm
from .models import Broadcast

logger = logging.getLogger(__name__)


def _resolve_recipients(recipient_filter):
    """Return a queryset of Users matching the chosen filter."""
    qs = User.objects.exclude(email="").filter(email__isnull=False)

    if recipient_filter == Broadcast.RecipientFilter.ACTIVE:
        qs = qs.filter(is_active=True)
    elif recipient_filter == Broadcast.RecipientFilter.ADMINS:
        qs = qs.filter(role="ADMIN")
    # ALL — no extra filter

    return qs


def _send_broadcast_emails(broadcast_id, email_list, subject, body, from_email):
    """
    Send broadcast emails in a background thread using a single shared
    SMTP connection. Updates Broadcast.recipient_count when done.

    Running this in a daemon thread means the HTTP response is returned
    immediately — the admin is not blocked waiting for thousands of sends.
    """
    sent = 0
    errors = 0

    try:
        connection = get_connection()
        connection.open()

        messages_to_send = [
            EmailMessage(
                subject=subject,
                body=body,
                from_email=from_email,
                to=[email],
                connection=connection,
            )
            for email in email_list
        ]

        for msg in messages_to_send:
            try:
                msg.send()
                sent += 1
            except Exception as e:
                errors += 1
                logger.warning(f"Broadcast {broadcast_id}: failed to send to {msg.to}: {e}")

        connection.close()

    except Exception as e:
        logger.error(f"Broadcast {broadcast_id}: could not open SMTP connection: {e}")

    # Update the saved broadcast with the final sent count
    try:
        broadcast = Broadcast.objects.get(pk=broadcast_id)
        broadcast.recipient_count = sent
        broadcast.save(update_fields=["recipient_count"])
        logger.info(f"Broadcast {broadcast_id}: sent={sent}, errors={errors}")
    except Exception as e:
        logger.error(f"Broadcast {broadcast_id}: could not update recipient_count: {e}")


@login_required
@admin_required
def broadcast_compose(request):
    """Admin compose page — build and send a broadcast email."""
    form = BroadcastForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        broadcast = form.save(commit=False)
        broadcast.sent_by = request.user

        recipients  = _resolve_recipients(broadcast.recipient_filter)
        email_list  = list(recipients.values_list("email", flat=True))

        # Save the broadcast row immediately so we have a PK for the
        # background thread to update. recipient_count starts at 0 and
        # is updated once sending is complete.
        broadcast.recipient_count = 0
        broadcast.save()

        # Fire off sending in a background thread so the request returns
        # immediately — avoids gunicorn's 30-second worker timeout.
        thread = threading.Thread(
            target=_send_broadcast_emails,
            args=(
                broadcast.pk,
                email_list,
                broadcast.subject,
                broadcast.body,
                settings.DEFAULT_FROM_EMAIL,
            ),
            daemon=True,
        )
        thread.start()

        messages.success(
            request,
            f"Broadcast queued for {len(email_list)} recipient"
            f"{'s' if len(email_list) != 1 else ''}. "
            f"Emails are being sent in the background."
        )
        return redirect("notifications:history")

    return render(request, "notifications/compose.html", {"form": form})


@login_required
@admin_required
def broadcast_history(request):
    """Admin broadcast history page."""
    broadcasts = Broadcast.objects.select_related("sent_by").all()
    return render(request, "notifications/history.html", {"broadcasts": broadcasts})