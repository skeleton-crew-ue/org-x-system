from django.shortcuts import render
# Importa admin_required desde core.decorators
from core.decorators import admin_required
from django.db.models import Sum
from .models import Transaction

@admin_required # Cambiado de @login_required a @admin_required
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

@admin_required # Cambiado de @login_required a @admin_required
def finance_summary(request):
    return transaction_list(request)