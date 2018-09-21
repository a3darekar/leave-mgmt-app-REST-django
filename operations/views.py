# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import LeaveRecordForm
from .models import Employee
from django.http import HttpResponse
from datetime import date, timedelta

from rest_framework import generics
from .serializers import EmployeeSerializer


@login_required
def home(request):
	try:
		emp = Employee.objects.get(user = request.user)
		leaves = LeavesRemain.objects.filter(employee = emp)
		context = {'emp' : emp, 'leaves' : leaves, 'user': request.user}
	except Employee.DoesNotExist:
		return render(request, "403.html", status=403)
	return render(request, 'home.html', context)

@login_required
def approve(request):
	leave_records 	= []
	employees 		= []
	try:
		emp 	= Employee.objects.get(user = request.user)
		dept 	= Department.objects.filter(head=emp.user)
	except Employee.DoesNotExist:
		return render(request, "403.html")
	except Department.DoesNotExist:
		return render(request, "403.html")
	notification = -1
	notification_status = -1
	status 		= dict(Status)
	if request.method 	== 'POST':
		leave_record 	= request.POST.get("leave_record", "")
		leave_record 	= LeaveRecord.objects.get(pk = leave_record)
		
		if 'Approve' in request.POST:
			leave_record.status = status['approved']
			notification = "Leave Approved"
			notification_status = -1
		else:
			leave_record.status = status['disapproved']
			notification = "Leave Disapproved"
			notification_status = 'failure'
		leave_record.save()
		# Get Method
	departments 	= Department.objects.filter(head=emp.user)
	for department in departments:
		employeees 		= Employee.objects.filter(department = department).exclude(user = emp.user)
		for employee in employeees:
			leave_entries = LeaveRecord.objects.filter(employee = employee, status = status['pending'])
			if leave_entries:
				for leave_entry in leave_entries:
					leave_records.append(leave_entry)
			employees.append(employee)
	context = {'leave_records' : leave_records, 'emp' : emp, 'notification' : notification, 'notification_status' : notification_status }
	return render(request,"approve.html", context)

@login_required
def apply(request):
	employee = Employee.objects.get(user=request.user)
	notification = "Leave request Sent"
	notification_status = -1
	status 		= dict(Status)
	if request.method 	== 'POST':
		form = LeaveRecordForm(request.POST)
		status 		= dict(Status)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.status = status['pending']
			instance.days_of_lave_taken = (instance.to_date - instance.from_date).days + 1
			for lday in range(instance.days_of_lave_taken):
				if (instance.from_date + timedelta(days=lday)).weekday() == 6:
					instance.days_of_lave_taken -=1
			instance.employee			= Employee.objects.get(user = request.user)
			instance.status				= status['pending']
			available_leaves 			= LeavesRemain.objects.filter(employee= instance.employee, leavetype = 'Casual').first().count
			if available_leaves > 0 and available_leaves > instance.days_of_lave_taken :
				instance.leavetype 		= 'Casual'
			else:
				instance.leavetype 		= 'Excess'
			leaves_records 				= LeaveRecord.objects.filter(employee = instance.employee, status = 'Approved')
			for leave_record in leaves_records:
					d1 	= leave_record.to_date
					d2 	= leave_record.from_date
					e1 	= instance.from_date
					e2 	= instance.to_date

					if (d1 <= e2) and (e1 <= d2):
						print('overlap')
						notification_status = "failure"
						notification = "Dates overlap"
						break
					else:
						print('no overlap')
			if notification_status != "failure":
				instance.save()
				notification = "Leave Form Submitted"
			notification_status = -1

	leaves = LeavesRemain.objects.filter(employee = employee)
	leave_records = LeaveRecord.objects.filter(employee = employee).order_by('-submit_date')
	form = LeaveRecordForm()
	context = {'employee' : employee, 'leaves' : leaves, 'user': request.user, 'leave_records': leave_records, 'form' : form}
	return render(request, "apply.html", context)