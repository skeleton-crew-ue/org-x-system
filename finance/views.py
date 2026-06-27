from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Transaction

@login_required
def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-transaction_date')
    
    # Calcular balance
    total_income = Transaction.objects.filter(type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense
    
    return render(request, 'finance/list.html', {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
    })

@login_required
def finance_summary(request):
    # Esta es una versión simplificada que reutiliza la lógica anterior
    return transaction_list(request)