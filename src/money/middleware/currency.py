from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

from carts.models import Cart
from sklep.log import loger


class SetCurrency(MiddlewareMixin):
    def process_request(self, request):
        current_currency = request.session.get('currency')
        if not current_currency:
            current_currency = request.session['currency'] = settings.DEFAULT_CURRENCY

        cart_obj = Cart.objects.get(request)
        if cart_obj:
            if cart_obj.currency != current_currency:
                cart_obj.recalculate_values(new_currency=current_currency)
                loger.info(f'Recalculated cart values with new currency: {current_currency}')
