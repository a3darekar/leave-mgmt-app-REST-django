from django.conf.urls import url, include
from .views import signup, settings, password
from django.contrib.auth.views import logout, login

urlpatterns = [
	url(r'^login/$', login, name='login'),
	url(r'^logout/$', logout, name='logout'),
	url(r'^rest/', include('rest_auth.urls')),
	url(r'^rest/', include('rest_social_auth.urls_session')),
	url(r'^rest/', include('rest_social_auth.urls_token')),
	url(r'^', include('social_django.urls', namespace='social')),
	url(r'^signup/', signup, name='signup'),
	url(r'^settings/$', settings, name='settings'),
	url(r'^settings/password/$', password, name='password'),
]