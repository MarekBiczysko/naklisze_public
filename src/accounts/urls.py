from django.conf.urls import url

from .views import logout_page, GuestRegisterView, SettingsPageView,\
    activation_view, send_activation_mail, LoginView, RegisterView


urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(
        r'^activation/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        activation_view,
        name='activation'
    ),
    url(r'^reactivate/(?P<user>[0-9A-Za-z_\-]+)/(?P<email>[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)/$',
        send_activation_mail,
        name='reactivate'
        ),
    url(r'^register/guest/$', GuestRegisterView.as_view(), name='guest_register'),
    url(r'^logout/$', logout_page, name='logout'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^settings/$', SettingsPageView.as_view(), name='settings'),
    ]
