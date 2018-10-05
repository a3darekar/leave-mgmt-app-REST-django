# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import LeaveRecordForm, EmployeeForm
from .models import Employee
from django.http import HttpResponse, JsonResponse
from datetime import date, timedelta
from dateutil import parser
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from fcm_django.models import FCMDevice
from django.core.urlresolvers import reverse_lazy
import json

@csrf_exempt
def webhook(request):
	if request.method == 'POST':
		req = json.loads(request.body)
	try:
		action = req.get('queryResult').get('action')
	except AttributeError:
		return 'json error'
	print action
	if action == 'leave_apply':
		res = webhook_apply(req)
	print('Action: ' + action)
	print('Response: ' + res)

	return JsonResponse({'fulfillmentText': res})


def webhook_apply(request):
	error, parameters = validate_params(request['queryResult']['parameters'])
	if error:
		return error
	else:
		print parameters
		employee 	= Employee.objects.get(email = parameters['email'])
		reason 		= parameters['reason']
		from_date 	= parameters['startDate']
		to_date 	= parameters['endDate']
		leave_record = LeaveRecord(employee = employee, reason = reason, from_date = from_date, to_date = to_date)
		leave_record.save()
		return "I Applied your Leave"

def validate_params(parameters):
	"""Takes a list of parameters from a HTTP request and validates them
	Returns a string of errors (or empty string) and a list of params
	"""

	# Initialize error and params
	error_response = ''
	params = {}

	datetime_input = parameters.get('period')
	print type(datetime_input), datetime_input
	if isinstance(datetime_input, (dict)):
		startDate, endDate = parse_datetime_input(datetime_input)
		params['startDate'] = parser.parse(startDate).date()
		params['endDate'] = parser.parse(endDate).date()
	else:
		params['startDate'] = parser.parse(datetime_input).date()
		params['endDate'] = parser.parse(datetime_input).date()

	print params['startDate'], type(params['startDate'])
	print params['endDate'], type(params['endDate'])
	
	params['reason'] = parameters.get('reason')

	params['email'] = parameters.get('email')

	print params['email'], type(params['email'].lower)
	print params['reason'], type(params['reason'])

	return error_response.strip(), params


def parse_datetime_input(datetime_input):
	"""Takes a string containing date/time and intervals in ISO-8601 format
	Returns a start and end Python datetime object
	datetimes are None if the string is not a date/time
	endDate is None if the string is not a date/time interval
	"""

	# Date time
	# If the string is length 8 datetime_input has the form 17:30:00
	if len(datetime_input) == 8:
		# if only the time is provided assume its for the current date
		current_date = dt.now().strftime('%Y-%m-%dT')

		startDate = dt.strptime(
			current_date + datetime_input,
			'%Y-%m-%dT%H:%M:%S')
		endDate = None
	# If the string is length 10 datetime_input has the form 2014-08-09
	elif len(datetime_input) == 10:
		startDate = dt.strptime(datetime_input, '%Y-%m-%d').date()
		endDate = None
	# If the string is length 20 datetime_input has the form
	# 2014-08-09T16:30:00Z
	elif len(datetime_input) == 20:
		startDate = dt.strptime(datetime_input, '%Y-%m-%dT%H:%M:%SZ')
		endDate = None

	# Date Periods
	# If the string is length 17 datetime_input has the form
	# 13:30:00/14:30:00
	elif len(datetime_input) == 17:
		# if only the time is provided assume its for the current date
		current_date = dt.now().strftime('%Y-%m-%dT')

		# Split date into start and end times
		datetime_input_start = datetime_input.split('/')[0]
		datetime_input_end = datetime_input.split('/')[1]

		startDate = dt.strptime(
			current_date + datetime_input_start, '%Y-%m-%dT%H:%M:%S')
		endDate = dt.strptime(
			current_date + datetime_input_end, '%Y-%m-%dT%H:%M:%S')
	# If the string is length 21 datetime_input has the form
	# 2014-01-01/2014-12-31
	elif len(datetime_input) == 21:
		# Split date into start and end times
		datetime_input_start = datetime_input.split('/')[0]
		datetime_input_end = datetime_input.split('/')[1]

		startDate = dt.strptime(
			datetime_input_start, '%Y-%m-%d').date()
		endDate = dt.strptime(datetime_input_end, '%Y-%m-%d').date()
	# If the string is length 41 datetime_input has the form
	# 2017-02-08T08:00:00Z/2017-02-08T12:00:00Z
	elif len(datetime_input) == 41:
		# Split date into start and end times
		datetime_input_start = datetime_input.split('/')[0]
		datetime_input_end = datetime_input.split('/')[1]

		startDate = dt.strptime(
			datetime_input_start, '%Y-%m-%dT%H:%M:%SZ')
		endDate = dt.strptime(
			datetime_input_end, '%Y-%m-%dT%H:%M:%SZ')
	else:
		startDate = None
		endDate = None

	return startDate, endDate
 
class EmployeeList(ListView):
    context_object_name = 'employee_list'
    template_name = 'operattions/employee_list.html'

    def get_queryset(self):
        return Employee.objects.all()

class EmployeeDelete(DeleteView):
    model = Employee
    success_url = reverse_lazy('employee-list')

@login_required
def employees(request, pk = None):
	employee = Employee.objects.get(user = request.user)
	employees = Employee.objects.all()
	instance = Employee.objects.filter(id = pk).first()
	if request.user.is_superuser:
		form = EmployeeForm(request.POST or None, instance=instance)
		if instance is not None:
			form.fields['user'].widget.attrs['readonly'] = True
		if request.method == "POST":
			if form.is_valid():
				instance = form.save()
				return redirect(reverse_lazy('employee-list'))
	else:
		error = "Your account doesn't have access to this page. To proceed, please login with an account that has access."
		return render(request, "403.html", { 'error' : error,})	
	context = { 'employee' : employee, 'employees' : employees, 'form': form, 'instance': instance, 'user': request.user}
	return render(request, "employee.html", context)

@login_required
def home(request):
	try:
		emp = Employee.objects.get(user = request.user)
		department_head = Department.objects.filter(head = request.user)
		leaves = LeavesRemain.objects.filter(employee = emp)
		context = {'emp' : emp, 'leaves' : leaves, 'department_head': department_head, 'user': request.user}
	except Employee.DoesNotExist:
		error = "It appears that you are not connected to the Leave Management application. Please Contact Administrator to Setup your account."
		return render(request, "403.html", { 'error' : error,})
	return render(request, 'home.html', context)

@login_required
def delete(request,id=None):
    object = LeaveRecord.objects.get(id=id)
    object.delete()
    return redirect('/apply/')


@login_required
def employees_delete(request,id=None):
    object = Employee.objects.get(id=id)
    object.delete()
    return redirect('/employees/')

@login_required
def approve(request):
	leave_records 	= []
	employees 		= []
	try:
		emp 	= Employee.objects.get(user = request.user)
		dept 	= Department.objects.filter(head=emp.user)
	except Employee.DoesNotExist:
		error = "It appears that you are not connected to the Leave Management application. Please Contact Administrator to Setup your account."
		return render(request, "403.html", { 'error' : error,})
	except Department.DoesNotExist:
		error = "It appears that you are not connected to the Leave Management application. Please Contact Administrator to Setup your account."
		return render(request, "403.html", { 'error' : error,})
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
	department_head = Department.objects.filter(head = request.user)
	context = {'leave_records' : leave_records, 'emp' : emp, 'department_head': department_head, 'notification' : notification, 'notification_status' : notification_status }
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

	department_head = Department.objects.filter(head = request.user)
	leaves = LeavesRemain.objects.filter(employee = employee)
	leave_records = LeaveRecord.objects.filter(employee = employee).order_by('-submit_date').order_by('-status')
	form = LeaveRecordForm()
	context = {'employee' : employee, 'leaves' : leaves, 'department_head': department_head, 'user': request.user, 'leave_records': leave_records, 'form' : form}
	return render(request, "apply.html", context)


def update(request, id):
	employee 	= Employee.objects.get(user = request.user)
	instance 	= LeaveRecord.objects.get(id=id)
	if instance.employee == employee and instance.status <> 'Approved':
		form 		= LeaveRecordForm(request.POST or None, instance=instance)
		if request.method == "POST":
			if form.is_valid():
				edited_instance = form.save()
				print edited_instance
			return redirect('/apply/')
		department_head = Department.objects.filter(head = request.user)
		context 	= {'employee' : employee, 'department_head': department_head, 'user': request.user, 'form' : form}
		return render(request, "update.html", context)
	else:
		return redirect('/apply/')
