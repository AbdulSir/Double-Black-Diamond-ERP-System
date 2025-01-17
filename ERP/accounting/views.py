from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Transaction
import csv, io

"""
    View for displaying the accounting tab.
"""
@login_required(login_url='login')
def accounting(request):
    User = get_user_model()
    users = User.objects.all()
    # query for fetching all the transactions
    t_query = Transaction.objects.order_by('-t_date').all()
    context = {
      't_query': t_query,
      'users': users
    }
    return render(request, 'accounting.html', context)

# A view to download accounting history
@login_required(login_url='login')
def download_accounting_history(request):
    items = Transaction.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transaction-history.csv"'
    writer = csv.writer(response, delimiter=',')
    # writing attributes
    writer.writerow(['Date', 'Type', 'Name', 'Serial Number', 'Quantity', 'Balance'])
    # writing data corresponding to attributes
    for obj in items:
        writer.writerow([obj.t_date, obj.t_type, obj.t_item_name, obj.t_serial, obj.t_quantity, obj.t_balance])
    return response

# A view to download profits history
@login_required(login_url='login')
def download_accounting_profits_history(request):
    items = Transaction.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="profits-history.csv"'
    writer = csv.writer(response, delimiter=',')
    # writing attributes
    writer.writerow(['Date', 'Type', 'Name', 'Serial Number', 'Quantity', 'Balance'])
    # writing data corresponding to attributes
    for obj in items:
        if obj.t_balance >= 0:
            writer.writerow([obj.t_date, obj.t_type, obj.t_item_name, obj.t_serial, obj.t_quantity, obj.t_balance])
    return response

# A view to download expenses history
@login_required(login_url='login')
def download_accounting_expenses_history(request):
    items = Transaction.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses-history.csv"'
    writer = csv.writer(response, delimiter=',')
    # writing attributes
    writer.writerow(['Date', 'Type', 'Name', 'Serial Number', 'Quantity', 'Balance'])
    # writing data corresponding to attributes
    for obj in items:
        if obj.t_balance < 0:
            writer.writerow([obj.t_date, obj.t_type, obj.t_item_name, obj.t_serial, obj.t_quantity, obj.t_balance])
    return response
