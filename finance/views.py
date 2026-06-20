from django.shortcuts import render
from core.decorators import admin_required
from .models import Transaction

@admin_required
def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-transaction_date')
    return render(request, 'finance/list.html', {'transactions': transactions})

@admin_required
def finance_summary(request):
    # This will be where you add the Chart.js logic later
    return render(request, 'finance/summary.html')

@admin_required
def transaction_add(request):
    return render(request, 'finance/add.html')
    