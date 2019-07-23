from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from accounts.models import GuestEmail
from sklep.log import loger

User = settings.AUTH_USER_MODEL


class BillingProfileManager(models.Manager):
    def new_or_get(self, request):
        guest_email_id = request.session.get("guest_email_id")
        user = request.user
        created = False
        obj = None

        if user.is_authenticated():  # Logged in user checkout, guest email no needed anymore
            if user.email:
                try:
                    del request.session["guest_email_id"]
                except:
                    pass
                obj, created = self.model.objects.get_or_create(user=user, email=user.email)

        elif guest_email_id is not None:  # Guest user checkout
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            obj, created = self.model.objects.get_or_create(
                user=None,
                email=guest_email_obj.email)

        else:
            loger.info(f'Could not create BillingProfile, not logged user and no guest email')

        return obj, created


class BillingProfile(models.Model):
    user        = models.OneToOneField(User, null=True, blank=True)
    email       = models.EmailField()
    active      = models.BooleanField(default=True)
    update      = models.DateTimeField(auto_now=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    objects = BillingProfileManager()

    def __str__(self):
        return self.email

def user_created_receiver(sender, instance, created, *args, **kwargs):
    if (created and instance.email and not kwargs.get('raw', False)):
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(user_created_receiver, sender=User)
