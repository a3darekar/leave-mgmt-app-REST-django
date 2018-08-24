from django import forms
from django.forms import ModelForm
from .models import *
from .choices import LeaveType

class LeaveRecordForm(ModelForm):
	reason		= forms.CharField( max_length=30, 
					widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'Enter reason'}), required=True)
	from_date	= forms.TextInput()
	to_date		= forms.TextInput()

	class Meta:
		model = LeaveRecord
		fields = ('reason', 'from_date', 'to_date')
