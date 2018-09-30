from django.conf.urls import url, include
from .views import *
from .serializers import router
from django.views.generic import TemplateView
 	 	 	
urlpatterns = [
	url(r'^$', home, name='home'),
    url(r'^api/', include((router.urls, 'rest-operations'))),
    url(r'^privacy_policy', TemplateView.as_view(template_name='privacy_policy.html'), name='privacy'),
    url(r'^apply', apply, name='apply'),
    url(r'^approve', approve, name='approve'),
    url(r'^webhook', webhook, name='webhook'),
]