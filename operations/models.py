# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from django.utils import six, timezone
from .choices import LeaveType, Status
from datetime import datetime, timedelta
from fcm_django.models import FCMDevice
from django.urls import reverse
import pytz
# from .twillio import *
from django.db import models
from django_currentuser.middleware import get_current_authenticated_user

# Create your models here.

class Department(models.Model):
	name 		= models.CharField(max_length = 25, default = "HR")
	head		= models.ForeignKey(User, related_name = "headofdept")

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	class Meta:
		unique_together 	= (('name','head'))
		verbose_name 		= ('Department')
		verbose_name_plural = ('Departments')


class Employee(models.Model):
	user 		= models.OneToOneField(User, help_text="Create a new user to add as an employee. This would be used as login credentials.", related_name="employee")
	email 		= models.EmailField(('email address'), unique=True)
	department 	= models.ForeignKey(Department, help_text="Assingn Department (or project to user, The Dept Head defined in Department Table would be the person managing the records of specific employee.")
	first_name 	= models.CharField(('first name'), max_length=30, blank=True)
	last_name 	= models.CharField(('last name'), max_length=30, blank=True)
	designation = models.CharField(max_length = 60)
	contact 	= PhoneNumberField(help_text="Please use the following format: <em>+91__________</em>.")

	USERNAME_FIELD = 'user'
	REQUIRED_FIELDS = ['email', 'first_name', 'last_name', ]
	
	def save(self, **kwargs):
		if self.pk:
			super(Employee, self).save()
		else:		
			super(Employee, self).save()
			leavetype = dict(LeaveType)
			l = LeavesRemain(employee = self, leavetype = leavetype['excess'], count = 0)
			l.save()
			l = LeavesRemain(employee = self, leavetype = leavetype['casual'], count = 15)
			l.save()
		return self

	def __str__(self):
		return self.get_full_name()

	class Meta:
		verbose_name 		= ('employee')
		verbose_name_plural = ('employees')

	def get_full_name(self):
		full_name = '%s %s' % (self.first_name, self.last_name)
		return full_name.strip()

	def get_short_name(self):
		return self.first_name

	def email_employee(self, subject, message, from_email=None, **kwargs):
		"""
		Sends an email to this User.
		"""
		send_mail(subject, message, from_email, [self.email], **kwargs)

	def get_absolute_url(self):
		return reverse('employee-list')


class LeavesRemain(models.Model):
	employee	= models.ForeignKey(Employee)
	leavetype 	= models.CharField(max_length=25, choices = LeaveType)
	count 		= models.PositiveIntegerField(default=10)

	class Meta:
		verbose_name 		= ('Leave Remain')
		verbose_name_plural = ('Leave Remains')


class LeaveRecord(models.Model):
	employee 			= models.ForeignKey(Employee)									
	leavetype 			= models.CharField('Leave Type', max_length=25, choices = LeaveType)			
	status				= models.CharField(max_length=25, choices = Status)				
	reason				= models.CharField(max_length=400, default = "Casual leave")	
	from_date			= models.DateField()
	to_date				= models.DateField()
	days_of_lave_taken	= models.PositiveIntegerField(default=1)
	submit_date			= models.DateField(default=datetime.now)
	excess				= models.BooleanField(default=False)
	
	class Meta:
		verbose_name 		= ('Leave Record')
		verbose_name_plural = ('Leave Records')

	def notify(self, to, body, *args, **kwargs):
		devices = FCMDevice.objects.filter( name = to.email )
		print devices
		for device in devices:
			device.send_message(title="Leave Request Update!", body=body)

	def save(self, *args, **kwargs):
		status 		= dict(Status)
		if self.pk:
			leavetype 	= dict(LeaveType)
			dept 	 	= self.employee.department
			dept_head 	= Employee.objects.get(user=Department.objects.get(id=dept.id).head)
			if self.status ==  status['approved']:
				self.status = status['approved']
				print self.leavetype
				self.notify(to = self.employee, body = "Your Leave submitted on" + str(self.submit_date) + " is Approved.")
				leavesremain 	= LeavesRemain.objects.get(leavetype = self.leavetype, employee = self.employee)
				self.available 	= leavesremain.count
				if leavesremain.count > 0 and leavesremain.count >= self.days_of_lave_taken:
					# This registers leaves in allowed quota
					leavesremain.count = leavesremain.count - self.days_of_lave_taken
					self.available = leavesremain.count
				else:
					# This registers leaves in Excess quota
					self.excess  = True
					leavesremain = LeavesRemain.objects.filter(leavetype = leavetype['excess']).get(employee = self.employee)
					leavesremain.count = leavesremain.count + self.days_of_lave_taken
				leavesremain.save()
			elif self.status == status['disapproved']:
				leavesremain 	= LeavesRemain.objects.get(leavetype = self.leavetype, employee = self.employee)
				self.available = leavesremain.count
				self.notify(to = self.employee, body = "Your Leave submitted on" + str(self.submit_date) + "was disapproved.")
			else:
				pass
		else:
			self.status = status['pending']
			if self.to_date < self.from_date:
				print "swapping"
				temp 			= self.to_date
				self.to_date 	= self.from_date
				self.from_date 	= temp

			self.days_of_lave_taken = (self.to_date - self.from_date).days + 1
			for lday in range(self.days_of_lave_taken):
				if (self.from_date + timedelta(days=lday)).weekday() == 6:
					self.days_of_lave_taken -=1

			user = get_current_authenticated_user()
			if not self.employee:
				self.employee = Employee.objects.get(user = user)
			available_leaves 			= LeavesRemain.objects.filter(employee= self.employee, leavetype = 'Casual').first().count
			if available_leaves > 0 and available_leaves > self.days_of_lave_taken :
				self.leavetype 		= 'Casual'
			else:
				self.leavetype 		= 'Excess'	
			leaves_records	= LeaveRecord.objects.filter(employee = self.employee, status = 'Approved')
			utc = pytz.utc
			if isinstance(self.from_date, datetime) :
				self.from_date = utc.localize(self.from_date)
				self.from_date = self.from_date.date()

			if isinstance(self.to_date, datetime) :
				self.to_date = utc.localize(self.to_date)
				self.to_date = self.to_date.date()
				
			for leave_record in leaves_records:
				d1 	= leave_record.to_date
				d2 	= leave_record.from_date
				e1 	= self.from_date
				e2 	= self.to_date
			self.notify(to = self.employee, body="New Leave Request. Log in to Leave Management System to see details.")
		super(LeaveRecord, self).save()
