from django.conf.urls import url, include
from .views import *
from .serializers import router
from django.views.generic import TemplateView
 	 	 	
urlpatterns = [
	url(r'^$', home, name='home'),
    url(r'^api/', include((router.urls, 'rest-operations'))),
    url(r'^privacy_policy', TemplateView.as_view(template_name='privacy_policy.html'), name='privacy'),
    url(r'^apply/(?P<id>[0-9]+)$', update, name='update'),
    url(r'^apply/(?P<id>[0-9]+)/delete$', delete, name='delete'),
    url(r'^apply', apply, name='apply'),
    url(r'^employees/(?P<pk>[0-9]+)/update/$', employees, name='employee-update'),
    url(r'^employees/$', EmployeeList.as_view(), name='employee-list'),
    url(r'^employees/(?P<pk>[0-9]+)/delete$', EmployeeDelete.as_view(), name='employee-delete'),
    url(r'^employees/register/$', employees, name='employee-add'),
    url(r'^approve', approve, name='approve'),
    url(r'^webhook', webhook, name='webhook'),
]