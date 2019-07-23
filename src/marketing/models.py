from django.db import models
from django.conf import settings
from django.db.models.signals import post_save

from sklep.log import loger
from .utils import Mailchimp


class MarketingPref(models.Model):
    user                    = models.OneToOneField(settings.AUTH_USER_MODEL, blank=True, null=True)
    guest_user_email        = models.EmailField(blank=True, null=True)
    subscribed              = models.BooleanField(default=True)
    mailchimp_subscribed    = models.NullBooleanField(blank=True, null=True)
    mailchimp_msg           = models.TextField(null=True, blank=True)
    timestamp               = models.DateTimeField(auto_now_add=True)
    updated                 = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email_instance()

    def email_instance(self):
        return self.user.email if self.guest_user_email is None else self.guest_user_email

    def print_market_data(self):
        return f"MailchimpSubscribed: {self.mailchimp_subscribed}, Timestamp: {self.timestamp}, Updated: {self.updated}"


def marketing_pref_create_receiver(sender, instance, created, *args, **kwargs):
    if created and not kwargs.get('raw', False):
        status_code, resp_data = Mailchimp().subscribe(instance.email_instance())

post_save.connect(marketing_pref_create_receiver, sender=MarketingPref)


def marketing_pref_update_receiver(sender, instance, *args, **kwargs):
    if instance.mailchimp_subscribed != instance.subscribed and not kwargs.get('raw', False):

        if instance.subscribed:
            status_code, resp_data = Mailchimp().subscribe(instance.email_instance())
        else:
            status_code, resp_data = Mailchimp().unsubscribe(instance.email_instance())
        if status_code == 200:

            if resp_data['status'] == "subscribed":
                instance.subscribed = True
                instance.mailchimp_subscribed = True

            else:
                instance.subscribed = False
                instance.mailchimp_subscribed = False

            instance.mailchimp_msg = resp_data
            instance.save()

        else:
            loger.error(f"Mailchimp status update, expected status code 200, but got: {status_code}")
            raise ConnectionError(f"Expected status code 200, but got: {status_code}")

post_save.connect(marketing_pref_update_receiver, sender=MarketingPref)

