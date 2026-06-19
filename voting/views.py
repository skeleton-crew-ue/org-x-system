from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Ballot, BallotOption, Vote


@login_required
def ballot_list(request):
    now = timezone.now()
    open_ballots = Ballot.objects.filter(
        is_active=True, opens_at__lte=now, closes_at__gte=now
    ).order_by("closes_at")
    closed_ballots = Ballot.objects.filter(
        is_active=True, closes_at__lt=now
    ).order_by("-closes_at")

    voted_ids = set(
        Vote.objects.filter(voter=request.user).values_list("ballot_id", flat=True)
    )

    return render(request, "voting/list.html", {
        "open_ballots": open_ballots,
        "closed_ballots": closed_ballots,
        "voted_ids": voted_ids,
    })


@login_required
def ballot_detail(request, ballot_id):
    ballot = get_object_or_404(Ballot, pk=ballot_id, is_active=True)
    now = timezone.now()

    already_voted = Vote.objects.filter(ballot=ballot, voter=request.user).exists()

    if ballot.closes_at < now:
        return redirect("voting:results", ballot_id=ballot_id)

    if already_voted or ballot.opens_at > now:
        messages.info(request, "You have already voted on this ballot or it is not yet open.")
        return redirect("voting:list")

    return render(request, "voting/detail.html", {"ballot": ballot})


@login_required
@require_POST
def cast_vote(request, ballot_id):
    ballot = get_object_or_404(Ballot, pk=ballot_id, is_active=True)
    now = timezone.now()

    if not (ballot.opens_at <= now <= ballot.closes_at):
        messages.error(request, "Voting is closed.")
        return redirect("voting:list")

    option_id = request.POST.get("option")
    option = get_object_or_404(BallotOption, pk=option_id, ballot=ballot)

    try:
        with transaction.atomic():
            if Vote.objects.filter(ballot=ballot, voter=request.user).exists():
                raise IntegrityError("already_voted")
            Vote.objects.create(ballot=ballot, option=option, voter=request.user)
    except IntegrityError:
        messages.error(request, "You have already voted on this ballot.")
        return redirect("voting:list")

    messages.success(request, "Vote recorded.")
    return redirect("voting:list")


@login_required
def ballot_results(request, ballot_id):
    ballot = get_object_or_404(Ballot, pk=ballot_id, is_active=True)
    now = timezone.now()

    if ballot.closes_at > now:
        messages.info(request, "Results will be available after the ballot closes.")
        return redirect("voting:list")

    options = ballot.options.all()
    total_votes = ballot.votes.count()

    results = []
    for option in options:
        count = option.votes.count()
        results.append({
            "text": option.text,
            "count": count,
            "percent": round(count / total_votes * 100, 1) if total_votes else 0,
        })

    return render(request, "voting/results.html", {
        "ballot": ballot,
        "results": results,
        "total_votes": total_votes,
    })
