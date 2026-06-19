from django.shortcuts import render
from django.db.models import Sum
from .models import Transaction

def finance_summary(request):
    # Traemos todas las transacciones ordenadas por fecha reciente
    transactions = Transaction.objects.all().order_by('-date')
    
    # Calculamos los totales usando agregaciones de Django (si da None, ponemos 0)
    total_income = Transaction.objects.filter(transaction_type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(transaction_type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculamos el balance neto
    net_balance = total_income - total_expense

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
    }
    
    return render(request, 'finance/finance_summary.html', context)
    