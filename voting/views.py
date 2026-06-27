from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Ballot, Vote, BallotOption

@login_required
def ballot_list(request):
    all_ballots = Ballot.objects.filter(is_active=True).order_by('-opens_at')
    open_ballots = [b for b in all_ballots if b.is_open()]
    closed_ballots = [b for b in all_ballots if b.is_closed()]
    return render(request, 'voting/list.html', {'open_ballots': open_ballots, 'closed_ballots': closed_ballots})

@login_required
def ballot_detail(request, pk): # Cambiado ballot_id a pk
    ballot = get_object_or_404(Ballot, pk=pk)
    already_voted = Vote.objects.filter(ballot=ballot, voter=request.user).exists()
    return render(request, 'voting/detail.html', {'ballot': ballot, 'already_voted': already_voted})

@login_required
def cast_vote(request, pk): # Cambiado ballot_id a pk
    ballot = get_object_or_404(Ballot, pk=pk)
    if request.method == "POST":
        if not ballot.is_open():
            messages.error(request, "This ballot is closed.")
            return redirect("voting:list")
        if Vote.objects.filter(ballot=ballot, voter=request.user).exists():
            messages.error(request, "You have already voted in this ballot.")
            return redirect("voting:list")
        option_id = request.POST.get('option')
        if option_id:
            option = get_object_or_404(BallotOption, pk=option_id, ballot=ballot)
            Vote.objects.create(ballot=ballot, option=option, voter=request.user)
            messages.success(request, "Your vote has been cast successfully.")
        else:
            messages.error(request, "Please select an option.")
    return redirect("voting:detail", pk=pk) # Cambiado ballot_id a pk

@login_required
def ballot_results(request, pk): # Cambiado ballot_id a pk
    ballot = get_object_or_404(Ballot, pk=pk)
    options = ballot.options.annotate(vote_count=Count('votes'))
    return render(request, 'voting/results.html', {'ballot': ballot, 'options': options})