from django.shortcuts import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from .models import MarketingPref
from .utils import check_email, MAILCHIMP_EMAIL_LIST_ID, Mailchimp
from django.utils.translation import ugettext as _


def subscribe_view(request):
    guest_email = request.POST.get('guest_email')

    if guest_email:
        checked_email = check_email(guest_email)

        if checked_email:
            MarketingPref.objects.get_or_create(user=None, guest_user_email=checked_email)
            messages.success(request, _('Zostałeś dodany do naszego Newslettera!'))
        else:
            messages.warning(request, _("Niepoprawny e-mail"))

    else:
        MarketingPref.objects.get_or_create(user=request.user)
        messages.success(request, _('Zostałeś dodany do naszego Newslettera!'))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def webhook_view(request):
    data = request.POST
    list_id = data.get("data[list_id]")

    if str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID):
        email = data.get("data[email]")

        resp_status, resp = Mailchimp().check_subscription_status(email)
        status = resp['status']

        qs = MarketingPref.objects.filter(guest_user_email__iexact=email)
        if not qs.exists():
            qs = MarketingPref.objects.filter(user__email__iexact=email)

        if qs.exists():
            if status == "unsubscribed":
                qs.update(mailchimp_msg=str(data), subscribed=False, mailchimp_subscribed=False)
            elif status == "subscribed":
                qs.update(mailchimp_msg=str(data), subscribed=True, mailchimp_subscribed=True)

    return HttpResponse("Mailchimp data received", status=200)