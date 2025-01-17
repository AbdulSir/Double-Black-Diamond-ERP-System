from django.shortcuts import render, redirect 
from django.http import HttpResponse, FileResponse, HttpResponseNotFound, JsonResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.core import serializers
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.contrib.auth.models import Group

from .decorators import *
from .forms import *

from manufacturing.models import *
from inventory.models import *
from sales.models import *
from accounting.models import *

from datetime import datetime
from decimal import Decimal

import logging
import io
import csv
import json

from reportlab.pdfgen import canvas

#from reportlab.pdfgen import canvas

# Create logger
logger = logging.getLogger(__name__)

# Create your views here.
@login_required(login_url='login')
def home(request):
    #Returning all users for display in the dropdown when changing permission levels
    User = get_user_model()
    users = User.objects.all()
    #Returning all top three items to display in the doughnut chart
    top_three_items = SoldItems.objects.select_related().order_by('-count')[:3]
    #Returning the # of sales, manufacturing, order transactions to display in the bar chart
    sales_transactions = Transaction.objects.filter(t_type='SALE').all().aggregate(profit=Sum('t_balance'))
    num_of_sales_transactions = Transaction.objects.filter(t_type='SALE').all().aggregate(num_sales=Count('pk'))
    manu_transactions = Transaction.objects.filter(t_type='MANUFACTURE').all().aggregate(manu_expense=Sum('t_balance'))
    num_of_manu_transactions = Transaction.objects.filter(t_type='MANUFACTURE').all().aggregate(num_manu=Count('pk'))
    orders_transactions = Transaction.objects.filter(t_type='ORDER').all().aggregate(order_expense=Sum('t_balance'))
    num_of_orders_transactions = Transaction.objects.filter(t_type='ORDER').all().aggregate(num_orders=Count('pk'))
    total = 0
    #Doing checks that the queried results do not return none, and if they do we handle them according
    if sales_transactions['profit'] is not None:
        total = total + sales_transactions['profit']
        sales_transactions = sales_transactions['profit']
    else:
        sales_transactions = 0
    if manu_transactions['manu_expense'] is not None:
        total = total + manu_transactions['manu_expense']
        manu_transactions = manu_transactions['manu_expense']
    else:
        manu_transactions = 0
    if orders_transactions['order_expense'] is not None:
        total = total + orders_transactions['order_expense']
        orders_transactions = orders_transactions['order_expense']
    else:
        orders_transactions = 0   
    context = {
        'sales_transactions': sales_transactions,
        'manu_transactions': manu_transactions,
        'orders_transactions': orders_transactions,
        'total': total,
        'num_of_sales_transactions': num_of_sales_transactions,
        'num_of_manu_transactions': num_of_manu_transactions,
        'num_of_orders_transactions': num_of_orders_transactions,
        'num_of_orders_transactions': num_of_orders_transactions,
        'top_three_items': top_three_items,
        'users': users,
    }
    return render(request, "landing.html", context=context)

#A view that registers new users.
@unauthenticated_user
def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():           
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            logger.debug("creating account with name: " + user)
            return redirect('login')             
    context = {'form': form}
    return render(request, 'register.html', context)

# A login view that login users when they are unauthenticated
@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password =request.POST.get('password1')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.debug(username + " has logged in")
            return redirect('home')
        else:
            messages.info(request, 'Username OR password is incorrect')
            logger.debug(username + " entered incorrect password")
    context = {}
    return render(request, 'login.html', context)

def logoutUser(request):
    logout(request)
    logger.debug("User has logged out")
    return redirect('login')

#decided to combine the two endpoints together
def generateReport(request):
    if request.method =='GET':
        queryDict = request.GET
        reportFormat = queryDict.get('format', None)
        if reportFormat == 'CSV':
            return generateCSV(request)
        if reportFormat == 'PDF':
            return generatePDF(request)
        else:
            return HttpResponseNotFound("No report in supplied format")
    else:
        return HttpResponseNotFound("Could not process your request") 


def generatePDF(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    #register valid get requests
    p=None
    report =None
    if request.method == 'GET':
        queryDict = request.GET
        report = queryDict.get('report', None)
        if report=='TEST':
            p = drawTestReport(buffer)
        else:
            return HttpResponseNotFound("There is no valid report")
    else:
        return HttpResponseNotFound("Could not process your request")
    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=report+'.pdf')

"""
#   Setup the different PDF templates here (draw+reportName)
"""

def drawTestReport(buffer):
    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")
    return p

def generateCSV(request):
    response = None
    report =None
    if request.method == 'GET':
        queryDict = request.GET
        report = queryDict.get('report', None)
        if report=='TEST':
            response = writeTestReport()
        else:
            return HttpResponseNotFound("There is no valid report")
    else:
        return HttpResponseNotFound("Could not process your request")
    return response

"""
#   Setup the different CSV tamplates here (write+reportName)
"""

def writeTestReport():
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="test.csv"'

    writer = csv.writer(response)
    writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
    writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])
    return response

"""
    Ajax endpoint for returning the groups of the logged in user in json format
"""
def getUserGroups(request):
    user_pk = request.GET.get('user_pk')
    if user_pk == "none":
        return JsonResponse([], safe=False)
    else:
        user = get_user_model().objects.get(pk=user_pk)
        list = []
        for g in user.groups.all():
            list.append(g.name)
        return JsonResponse(list, safe=False)

# This view updates the users groups based on the post request in the modal from the base.html
def updateUserGroups(request):
    if request.method == "POST":
        user_selected = request.POST.get('user-selected')
        manu_checkbox = request.POST.get('manufacturingCheckbox')
        inventory_checkbox = request.POST.get('inventoryCheckbox')
        sales_checkbox = request.POST.get('salesCheckbox')

        if user_selected == "none":
            messages.info(request, 'No user selected to save group settings.')
            return redirect('home')
        else:
            user = get_user_model().objects.get(pk=int(user_selected))
            if manu_checkbox:
                # add user to group if not already in it
                group = Group.objects.get(name='manufacturing_account')
                try:
                    user.groups.get(pk=group.pk)
                except Group.DoesNotExist:
                    group.user_set.add(user)
            else:
                # remove user from group if already in it
                group = Group.objects.get(name='manufacturing_account')
                try:
                    if user.groups.get(pk=group.pk) is not None:
                        group.user_set.remove(user)
                except Group.DoesNotExist:
                    # do nothing, user already removed from group
                    i = 0       
            if inventory_checkbox:
                # add user to group if not already in it
                group = Group.objects.get(name='inventory_account')
                try:
                    user.groups.get(pk=group.pk)
                except Group.DoesNotExist:
                    group.user_set.add(user)
            else:
                # remove user from group if already in it
                group = Group.objects.get(name='inventory_account')
                try:
                    if user.groups.get(pk=group.pk) is not None:
                        group.user_set.remove(user)
                except Group.DoesNotExist:
                    # do nothing, user already removed from group
                    i = 0
            
            if sales_checkbox:
                # add user to group if not already in it
                group = Group.objects.get(name='sales_account')
                try:
                    user.groups.get(pk=group.pk)  
                except Group.DoesNotExist:
                    group.user_set.add(user)
            else:
                # remove user from group if already in it
                group = Group.objects.get(name='sales_account')
                try:
                    if user.groups.get(pk=group.pk) is not None:
                        group.user_set.remove(user)
                except Group.DoesNotExist:
                    # do nothing, user already removed from group
                    i = 0
        messages.info(request, 'User groups updated.')
        return redirect('home')