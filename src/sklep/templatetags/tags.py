from django import template
from django.utils.translation import get_language

from money.models import ShippingPrice

register = template.Library()

@register.filter(name='get')
def get(d, k):
    try:
        return d.get(k, '')
    except AttributeError:
        return ''

@register.simple_tag
def current_language():
    return get_language()

@register.simple_tag(takes_context=True)
def get_regular_price(context, prices, currency=None):
    if not currency:
        currency = context.get('request').session.get('currency')
    return prices.get_regular(currency)

@register.simple_tag(takes_context=True)
def get_promo_price(context, prices, currency=None):
    if not currency:
        currency = context.get('request').session.get('currency')
    return prices.get_promo(currency)

shipping_price_obj = ShippingPrice.objects.first()

@register.simple_tag(takes_context=True)
def local_shipping_price(context):
    current_currency = context.get('request').session.get('currency')
    return shipping_price_obj.get_local(current_currency)

@register.simple_tag(takes_context=True)
def international_shipping_price(context):
    current_currency = context.get('request').session.get('currency')
    return shipping_price_obj.get_international(current_currency)
