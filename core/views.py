"""Core views — the home page / dashboard shell.

Bootstrap version just proves the skeleton renders. Mr T builds the real
dashboard on top of base.html.
"""

from django.shortcuts import render


def home(request):
    return render(request, "home.html")
