from django.conf.urls import url
from .views import GeneratePdfOrderView


urlpatterns = [
    url(r'^order_data_pdf/(?P<order_id>\d*)$', GeneratePdfOrderView.as_view(), name='order_data_pdf'),
]
