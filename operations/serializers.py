from rest_framework import serializers
from .models import *
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets


class LeavesRemainSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeavesRemain
        fields = ('id', 'employee', 'leavetype', 'count')

class LeavesRemainViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = LeavesRemain.objects.all()
    serializer_class = LeavesRemainSerializer

class LeaveRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveRecord
        fields = ('employee', 'leavetype', 'status', 'reason', 'from_date', 'to_date', 'days_of_lave_taken', 'submit_date', 'available', 'excess')

class LeaveRecordViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = LeaveRecord.objects.all()
    serializer_class = LeaveRecordSerializer

router = DefaultRouter()
router.register(r'leaves', LeavesRemainViewSet, base_name='leaves_rest')
router.register(r'leaverecords', LeaveRecordViewSet, base_name='leaverecords_rest')
