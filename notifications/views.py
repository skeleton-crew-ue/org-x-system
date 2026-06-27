from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.conf import settings

from core.decorators import admin_required
from members.models import User
from .forms import BroadcastForm
from .models import Broadcast


def _resolve_recipients(recipient_filter):
    """Return a queryset of Users matching the chosen filter."""
    qs = User.objects.exclude(email="").filter(email__isnull=False)

    if recipient_filter == Broadcast.RecipientFilter.ACTIVE:
        qs = qs.filter(is_active=True)
    elif recipient_filter == Broadcast.RecipientFilter.ADMINS:
        qs = qs.filter(role="ADMIN")
    # ALL — no extra filter

    return qs


@login_required
@admin_required
def broadcast_compose(request):
    """Admin compose page — build and send a broadcast email."""
    form = BroadcastForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        broadcast = form.save(commit=False)
        broadcast.sent_by = request.user

        recipients = _resolve_recipients(broadcast.recipient_filter)
        email_list  = list(recipients.values_list("email", flat=True))

        # Send emails
        sent = 0
        for email in email_list:
            try:
                send_mail(
                    subject=broadcast.subject,
                    message=broadcast.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                sent += 1
            except Exception:
                # Log and continue — don't abort the whole broadcast for one failure
                pass

        broadcast.recipient_count = sent
        broadcast.save()

        messages.success(
            request,
            f"Broadcast sent to {sent} recipient{'s' if sent != 1 else ''}."
        )
        return redirect("notifications:history")

    return render(request, "notifications/compose.html", {"form": form})


@login_required
@admin_required
def broadcast_history(request):
    """Admin broadcast history page."""
    broadcasts = Broadcast.objects.select_related("sent_by").all()
    return render(request, "notifications/history.html", {"broadcasts": broadcasts})
