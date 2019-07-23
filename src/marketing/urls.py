from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from .views import (
    subscribe_view,
    webhook_view
)


urlpatterns = [
    url(r'^subscribe/', subscribe_view, name='subscribe'),
    url(r'^sync/', csrf_exempt(webhook_view), name='sync'),
]
