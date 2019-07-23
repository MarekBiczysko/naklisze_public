from django.conf.urls import url
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import RedirectView

from .views import AnalyticsView, GeneratePdfUserDataView, sklep_django_log_view, sklep_log_view


urlpatterns = [
    url(r'^panel/$', AnalyticsView.as_view(), name='panel'),
    url(r'^user_data_pdf/$', GeneratePdfUserDataView.as_view(), name='user_data_pdf'),
    url(r'^sklep_log/$', sklep_log_view, name='sklep_log'),
    url(r'^django_log/$', sklep_django_log_view, name='django_log'),
]
