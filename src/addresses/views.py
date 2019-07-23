from sklep.log import loger
from .forms import AddressForm
from django.utils.http import is_safe_url
from django.shortcuts import redirect
from billing.models import BillingProfile
from django.contrib import messages
from .models import Address
from django.utils.translation import ugettext as _


def checkout_address_create_view(request):
    form = AddressForm(request.POST or None)

    next_get_url = request.GET.get('next_url')
    next_post_url = request.POST.get('next_url')
    redirect_path = (next_post_url or next_get_url) or None

    if form.is_valid():

        instance = form.save(commit=False)
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)

        if billing_profile is not None:
            address_type = request.POST.get('address_type', 'shipping')
            instance.billing_profile = billing_profile
            instance.address_type = address_type
            instance.save()

            loger.info(f'Created address type for billing profile {billing_profile.id}: {address_type} \n {instance.print_address()}')
            request.session[address_type + "_address_id"] = instance.id

        else:
            return redirect("carts:checkout")

        if is_safe_url(redirect_path, request.get_host()):
            return redirect(redirect_path)

    elif request.POST:
        messages.warning(request, _('Formularz został wypełniony niepoprawnie!'))

    return redirect("carts:checkout")

def checkout_address_reuse_view(request):

    next_get_url = request.GET.get('next_url')
    next_post_url = request.POST.get('next_url')
    redirect_path = (next_post_url or next_get_url) or None

    reuse_address = request.POST.get('reuse_address')

    if reuse_address:  # use same shipping address object for billing address
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        address_id = request.POST.get('address_id')
        address_type = request.POST.get('address_type', 'shipping')

        if address_id is not None:
            qs = Address.objects.filter(billing_profile=billing_profile, id=address_id)
            if qs.exists():
                loger.info(f'Reused address for checkout: {qs.first().print_address()}')
                request.session[address_type + "_address_id"] = address_id

            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)

    elif request.POST:
        messages.warning(request, _('Formularz został wypełniony niepoprawnie!'))

    return redirect("carts:checkout")