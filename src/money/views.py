from django.views.generic import RedirectView
from django.conf import settings
from django.shortcuts import HttpResponseRedirect

from sklep.log import loger


class ChangeCurrencyView(RedirectView):
    def get(self, request, *args, **kwargs):
        currency = self.kwargs.get('currency')
        if currency:
            if currency in settings.CURRENCIES:
                request.session['currency'] = currency
                loger.info(f'Set new currency in ChangeCurrencyView: {currency}')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
