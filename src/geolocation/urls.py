from django.conf.urls import url

from .views import (
    ip_geo_view,
    GeoListView,
)


urlpatterns = [
    url(r'^list/$', GeoListView.as_view(), name='list'),
    url(r'^ip/(?P<ip>.+)/$', ip_geo_view, name='ip'),
]
