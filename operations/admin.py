# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.admin.filters import AllValuesFieldListFilter
from django.contrib.auth.models import Group
from .models import *
from .choices import *
from django.contrib import admin

# Register your models here.

class EmployeeAdmin(admin.ModelAdmin):
	fieldsets = [
		('Login Information',	{'fields': ['user']}),
		('Account Information',	{'fields': ['first_name', 'last_name', 'email']}),
		('Department',			{'fields': ['department']}),
		('Miscellenous',		{'fields': ['contact', 'designation']})
	]
	list_display = ('full_name', 'department', 'email', 'contact')
	
	def full_name(self, obj):
		return obj.get_full_name()

class LeaveRecordAdmin(admin.ModelAdmin):

	def leave_status(self, obj):
		return ("%s" % (obj.status)).upper()
	leave_status.short_description = 'Leave Status'

	list_display = ('employee', 'leavetype', 'leave_status', 'reason', 'from_date', 'to_date', 'submit_date')
	list_filter = ['submit_date', 'status', 'leavetype', 'excess']

class LeavesRemainAdmin(admin.ModelAdmin):

	def leave_type(self, obj):
		return ("%s" % (obj.leavetype)).upper()
	leave_type.short_description = 'Type of Leave'


	list_display = ('employee', 'leave_type', 'count')
	list_filter = ['employee', ('leavetype', AllValuesFieldListFilter)]

class DepartmentAdmin(admin.ModelAdmin):
	list_display = ('name', 'Head')

admin.site.unregister(Group)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(LeavesRemain, LeavesRemainAdmin)
admin.site.register(LeaveRecord, LeaveRecordAdmin)