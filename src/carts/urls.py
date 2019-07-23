from django.conf.urls import url
from .views import cart_home, cart_update, checkout_home, checkout_success, check_availability
from addresses.views import checkout_address_create_view, checkout_address_reuse_view


urlpatterns = [
    url(r'^$', cart_home, name='home'),
    url(r'^update/$', cart_update, name='update'),
    url(r'^availability/$', check_availability, name='check_availability'),
    url(r'^checkout/$', checkout_home, name='checkout'),
    url(r'^checkout/address/create/$', checkout_address_create_view, name='checkout_address_create'),
    url(r'^checkout/address/reuse/$', checkout_address_reuse_view, name='checkout_address_reuse'),
    url(r'^checkout/success$', checkout_success, name='checkout_success'),
]
