from django.views.generic import RedirectView
from django.conf.urls import url

from .views import wix_page

urlpatterns = [
    # url(r'^$', RedirectView.as_view(url='https://biczysko.wix.com/foto')),
    url(r'^$', wix_page, name='wix'),
    url(r'^', RedirectView.as_view(url='/')),
]
