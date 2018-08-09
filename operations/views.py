# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *

from django.contrib import messages
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from social_django.models import UserSocialAuth

@login_required
def home(request):
	try:
		emp = Employee.objects.get(user = request.user)
		leaves = LeavesRemain.objects.filter(employee = emp)
		print request.user
	except Employee.DoesNotExist:
		return render(request, "403.html", status=403)
	return render(request, 'home.html', {'emp' : emp, 'leaves' : leaves, 'user': request.user})

def signup(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)
			return redirect('home')
	else:
		form = UserCreationForm()
	return render(request, 'registration/signup.html', {'form': form})


@login_required
def settings(request):
	user = request.user

	try:
		google_oauth2_login = user.social_auth.get(provider='google-oauth2')
	except UserSocialAuth.DoesNotExist:
		google_oauth2_login = None

	can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

	return render(request, 'settings.html', {
		'google_oauth2_login': google_oauth2_login,
		'can_disconnect': can_disconnect
	})

@login_required
def password(request):
	if request.user.has_usable_password():
		PasswordForm = PasswordChangeForm
	else:
		PasswordForm = AdminPasswordChangeForm

	if request.method == 'POST':
		form = PasswordForm(request.user, request.POST)
		if form.is_valid():
			form.save()
			update_session_auth_hash(request, form.user)
			messages.success(request, 'Your password was successfully updated!')
			return redirect('settings')
		else:
			messages.error(request, 'Please correct the error below.')
	else:
		form = PasswordForm(request.user)
	return render(request, 'registration/password.html', {'form': form})