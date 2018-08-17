# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from django.utils import six, timezone
from .choices import LeaveType, Status
from datetime import datetime
# from .twillio import *
from django.db import models

# Create your models here.

class Department(models.Model):
	name 		= models.CharField(max_length=25, default="HR")
	head		= models.ForeignKey(User)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name 		= ('Department')
		verbose_name_plural = ('Departments')


class Employee(models.Model):
	user 		= models.OneToOneField(User, help_text="Create a new user to add as an employee. This would be used as login credentials.")
	email 		= models.EmailField(('email address'), unique=True)
	department 	= models.OneToOneField(Department, help_text="Assingn Department (or project to user, The Dept Head defined in Department Table would be the person managing the records of specific employee.")
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
	from_date			= models.DateField(default=datetime.now)
	to_date				= models.DateField(default=datetime.now)
	days_of_lave_taken	= models.PositiveIntegerField(default=1)
	submit_date			= models.DateField(default=datetime.now)
	available			= models.PositiveIntegerField(default=0)
	excess				= models.BooleanField(default=False)
	
	class Meta:
		verbose_name 		= ('Leave Record')
		verbose_name_plural = ('Leave Records')

	def notify(self, to, from_, body, *args, **kwargs):
		try:
			message = client.messages.create( to = to, from_ = from_, body = body)
			print(message.sid)
		except TwilioRestException as e:
			print(e)

	def save(self):
		leavetype 	= dict(LeaveType)
		status 		= dict(Status)
		dept 	 	= self.employee.department
		dept_head 	= Employee.objects.get(user=Department.objects.get(id=dept.id).head)
		if self.pk:
			if self.status ==  status['approved']:
				self.status = status['approved']
				# self.notify(to = str(self.employee.contact), from_ = phone_number, body="Your Leave submitted on" + str(self.submit_date) + " is Approved.")
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
				# self.notify(to = str(self.employee.contact), from_ = phone_number, body="Your Leave submitted on" + str(self.submit_date) + "was disapproved.")
			else:
				pass
		else:
			pass
			# self.notify(to =str(employee.contact), from_ = phone_number, body="New Leave Request. Log in to Leave Management System to see details.")
		super(LeaveRecord, self).save()
