from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileEditForm, RegistrationForm


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("core:home")
    else:
        form = RegistrationForm()
    return render(request, "members/register.html", {"form": form})


@login_required
def profile(request):
    return render(request, "members/profile.html")


@login_required
def profile_edit(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("members:profile")
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, "members/profile_edit.html", {"form": form})
