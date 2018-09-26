from rest_framework import serializers
from .models import *
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('user', 'email', 'department', 'first_name', 'last_name', 'designation', 'contact')

class LeavesRemainSerializer(serializers.ModelSerializer):

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


class LeaveRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveRecord
        fields = ('id', 'employee', 'leavetype', 'status', 'reason', 'from_date', 'to_date', 'days_of_lave_taken', 'submit_date', 'excess')
        read_only_fields = ('employee', 'status', 'days_of_lave_taken', 'submit_date', 'leavetype', 'excess')

class LeaveRecordViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    serializer_class = LeaveRecordSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            employee = Employee.objects.filter(user = user)
            if self.request.query_params.get('status') == 'pending':
                records =  LeaveRecord.objects.filter(employee = employee).filter(status = 'pending')
                print records
                return records
            return LeaveRecord.objects.filter(employee = employee)
        else:
            return LeaveRecord.objects.none()


    def update(self, instance, validated_data):
        instance.reason = validated_data.get('reason', instance.email)
        instance.from_date = validated_data.get('from_date', instance.from_date)
        instance.to_date = validated_data.get('to_date', instance.to_date)
        return instance

router = DefaultRouter()
router.register(r'leaves', LeavesRemainViewSet, base_name='leaves_rest')
router.register(r'emps', LeavesRemainViewSet, base_name='leaves_rest')
router.register(r'leaverecords', LeaveRecordViewSet, base_name='leaverecords_rest')
