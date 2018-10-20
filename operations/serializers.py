from rest_framework import serializers
from rest_framework.serializers import ValidationError, ModelSerializer
from .models import *
from .choices import *

from datetime import date, timedelta

from rest_framework.routers import DefaultRouter
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_friendly_errors.mixins import FriendlyErrorMessagesMixin
from fcm_django.api.rest_framework import FCMDeviceViewSet, FCMDeviceAuthorizedViewSet



class EmployeeSerializer(ModelSerializer):

	class Meta:
		model = Employee
		fields = ('user', 'email', 'department', 'first_name', 'last_name', 'designation', 'contact')

class LeavesRemainSerializer(ModelSerializer):

	class Meta:
		model = LeavesRemain
		fields = ('id', 'employee', 'leavetype', 'count')

class LeavesRemainViewSet(viewsets.ModelViewSet):
	"""
	A simple ViewSet for viewing and editing accounts.
	"""
	serializer_class = LeavesRemainSerializer
	permission_classes = (IsAuthenticated,)
	
	def get_queryset(self):
		user = self.request.user
		if user.is_authenticated:
			employee = Employee.objects.filter(user = user)
			return LeavesRemain.objects.filter(employee = employee)
		else:
			return LeavesRemain.objects.none()


class LeaveRecordSerializer(ModelSerializer):

	class Meta:
		model = LeaveRecord
		fields = ('id', 'employee', 'leavetype', 'status', 'reason', 'from_date', 'to_date', 'days_of_lave_taken', 'submit_date', 'excess')
		read_only_fields = ('employee', 'leavetype', 'status', 'excess')


class LeaveRecordViewSet(viewsets.ModelViewSet):
	"""
	A simple ViewSet for viewing and editing accounts.
	"""
	# permission_classes = (IsAuthenticated,)
	serializer_class = LeaveRecordSerializer

	def get_queryset(self):
		user = self.request.user
		if user.is_authenticated:
			employee = Employee.objects.filter(user = user)
			if self.request.query_params.get('task') == 'approve':
				department = Department.objects.filter(head = user)
				employees = Employee.objects.filter(department = department)
				print department, employees
				return LeaveRecord.objects.filter(employee__in = employees).filter(status = 'pending') | LeaveRecord.objects.filter(employee__in = employees).filter(status = 'Pending')
			if self.request.query_params.get('status') == 'pending':
				return LeaveRecord.objects.filter(employee = employee).filter(status = 'pending') | LeaveRecord.objects.filter(employee = employee).filter(status = 'Pending')
			if self.request.query_params.get('status') == 'approved':
				return LeaveRecord.objects.filter(employee = employee).filter(status = 'approved') | LeaveRecord.objects.filter(employee = employee).filter(status = 'Approved')
			return LeaveRecord.objects.filter(employee = employee)
		else:
			return LeaveRecord.objects.none()


	def update(self, request, *args, **kwargs):
		instance = self.get_object()
		instance.status = request.data.get("status")
		instance.save()
		
		serializer = LeaveRecordSerializer(data=instance)
		if serializer.is_valid():
			self.perform_update(serializer)
		
		return Response(serializer.data)

router = DefaultRouter()
router.register(r'leaves', LeavesRemainViewSet, base_name='leaves_remain_rest')
router.register(r'emps', LeavesRemainViewSet, base_name='employees')
router.register(r'leaverecords', LeaveRecordViewSet, base_name='leaverecords_rest')
router.register(r'devices', FCMDeviceViewSet)
