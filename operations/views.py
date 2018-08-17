# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *

from .models import Employee


@login_required
def home(request):
	try:
		emp = Employee.objects.get(user = request.user)
		leaves = LeavesRemain.objects.filter(employee = emp)
	except Employee.DoesNotExist:
		return render(request, "403.html", status=403)
	return render(request, 'home.html', {'emp' : emp, 'leaves' : leaves, 'user': request.user})
