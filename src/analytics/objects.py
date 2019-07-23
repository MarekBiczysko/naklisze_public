from billing.models import BillingProfile
from addresses.models import Address
from geolocation.models import Geolocation
from marketing.models import MarketingPref
from orders.models import Order

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone

import datetime


class UserHistoryData(object):
    def __init__(self, user):
        self.user               = user
        self.date               = datetime.datetime.now()
        self.username           = self.user.username
        self.email              = self.user.email
        self.pdf_filename       = f"{self.email}_user_data_naklisze.pdf"
        self.billing_profiles   = BillingProfile.objects.filter(user=user)  # email, active, update, timestamp
        self.addresses          = Address.objects.filter(billing_profile__in=self.billing_profiles)
        self.orders             = Order.objects.filter(billing_profile__in=self.billing_profiles)
        self.geolocation        = Geolocation.objects.filter(user=user)
        self.marketing          = MarketingPref.objects.filter(user=user)


class AccountsInfo(object):
    def __init__(self):
        self.all_users = self.all_existing_users()
        self.active_sessions = self.get_active_sessions()
        self.active_users = self.get_active_users()

    def all_existing_users(self):
        return User.objects.all().order_by('-date_joined')

    def get_active_sessions(self):
        return Session.objects.filter(expire_date__gte=timezone.now())


    def get_active_users(self):
        user_id_list = []
        for session in self.active_sessions:
            data = session.get_decoded()
            user_id_list.append(data.get('_auth_user_id', None))
        return User.objects.filter(id__in=user_id_list)