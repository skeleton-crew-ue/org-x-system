from collections import defaultdict
from decimal import Decimal

from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import Coalesce
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
    def total_for(type_):
        result = Transaction.objects.filter(type=type_).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )
        return result['total']

    income_total = total_for('INCOME')
    expense_total = total_for('EXPENSE')
    net_balance = income_total - expense_total

    by_category = defaultdict(lambda: {'INCOME': 0, 'EXPENSE': 0})
    rows = Transaction.objects.values('category__name', 'type').annotate(total=Sum('amount'))
    for row in rows:
        name = row['category__name'] or 'Uncategorized'
        by_category[name][row['type']] = float(row['total'])

    chart_labels = list(by_category.keys())
    chart_income = [by_category[label]['INCOME'] for label in chart_labels]
    chart_expense = [by_category[label]['EXPENSE'] for label in chart_labels]

    return render(request, 'finance/summary.html', {
        'income_total': income_total,
        'expense_total': expense_total,
        'net_balance': net_balance,
        'chart_labels': chart_labels,
        'chart_income': chart_income,
        'chart_expense': chart_expense,
    })

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
