from django.contrib import messages
from django.shortcuts import redirect, render
from core.decorators import admin_required
from .forms import TransactionForm
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
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.recorded_by = request.user
            transaction.save()
            messages.success(request, 'Transaction added.')
            return redirect('finance:list')
    else:
        form = TransactionForm()
    return render(request, 'finance/add.html', {'form': form})
