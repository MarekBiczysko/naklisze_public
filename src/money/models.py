from django.db import models
from djmoney.models.fields import MoneyField
from django.conf import settings
from decimal import Decimal

from products.models import Product


PLN_CONVERT_FACTOR = {
    'USD': Decimal(3.0),
    'EUR': Decimal(4.0)
}

def convert_money(value, factor, currency):
    amount = value.amount / factor[currency]
    return value.__class__(amount, currency)


class ProductPrice(models.Model):
    product         = models.OneToOneField(Product, related_name='prices', on_delete=models.CASCADE)
    regular_PLN     = MoneyField(decimal_places=2, max_digits=8, default_currency=settings.DEFAULT_CURRENCY)
    regular_USD     = MoneyField(decimal_places=2, max_digits=8, blank=True, null=True, default_currency='USD')
    regular_EUR     = MoneyField(decimal_places=2, max_digits=8, blank=True, null=True, default_currency='EUR')
    promo_PLN       = MoneyField(decimal_places=2, max_digits=8, null=True, blank=True, default_currency=settings.DEFAULT_CURRENCY)
    promo_USD       = MoneyField(decimal_places=2, max_digits=8, null=True, blank=True,
                       default_currency='USD')
    promo_EUR       = MoneyField(decimal_places=2, max_digits=8, null=True, blank=True,
                       default_currency='EUR')

    def save(self, *args, **kwargs):
        force_update = False
        if self.id:
            force_update = True
        self.regular_USD = convert_money(self.regular_PLN, PLN_CONVERT_FACTOR, 'USD')
        self.regular_EUR = convert_money(self.regular_PLN, PLN_CONVERT_FACTOR, 'EUR')
        if self.promo_PLN:
            self.promo_USD = convert_money(self.promo_PLN, PLN_CONVERT_FACTOR, 'USD')
            self.promo_EUR = convert_money(self.promo_PLN, PLN_CONVERT_FACTOR, 'EUR')
        self.promo
        self.regular
        super(ProductPrice, self).save(force_update=force_update)

    def get_regular(self, currency=None):
        if not currency:
            return self.regular_PLN
        # current_currency = request.session.get('currency')
        return getattr(self, f'regular_{currency}')
    regular = property(get_regular)


    def get_promo(self, currency=None):
        if not currency:
            return self.promo_PLN
        return getattr(self, f'promo_{currency}')
    promo = property(get_promo)


class ShippingPrice(models.Model):
    local_PLN           = MoneyField(decimal_places=2, max_digits=8, default_currency=settings.DEFAULT_CURRENCY)
    local_USD           = MoneyField(decimal_places=2, max_digits=8, null=True, blank=True, default_currency='USD')
    local_EUR           = MoneyField(decimal_places=2, max_digits=8, null=True, blank=True, default_currency='EUR')
    international_PLN   = MoneyField(decimal_places=2, max_digits=8, default_currency=settings.DEFAULT_CURRENCY)
    international_USD   = MoneyField(decimal_places=2, max_digits=8, null=True, blank=True,
                       default_currency='USD')
    international_EUR   = MoneyField(decimal_places=2, max_digits=8, null=True, blank=True,
                       default_currency='EUR')
    self_PLN = MoneyField(decimal_places=2, max_digits=8, default=0, default_currency=settings.DEFAULT_CURRENCY)
    self_USD = MoneyField(decimal_places=2, max_digits=8, default=0, default_currency='USD')
    self_EUR = MoneyField(decimal_places=2, max_digits=8, default=0, default_currency='EUR')

    def save(self, *args, **kwargs):
        force_update = False
        if self.id:
            force_update = True
        self.local_USD = convert_money(self.local_PLN, PLN_CONVERT_FACTOR, 'USD')
        self.local_EUR = convert_money(self.local_PLN, PLN_CONVERT_FACTOR, 'EUR')
        self.international_USD = convert_money(self.international_PLN, PLN_CONVERT_FACTOR, 'USD')
        self.international_EUR = convert_money(self.international_PLN, PLN_CONVERT_FACTOR, 'EUR')
        super(ShippingPrice, self).save(force_update=force_update)

    def get_local(self, currency=None):
        if not currency:
            return self.local_PLN
        return getattr(self, f'local_{currency}')
    local = property(get_local)

    def get_international(self, currency=None):
        if not currency:
            return self.international_PLN
        return getattr(self, f'international_{currency}')
    international = property(get_international)

    def get_self(self, currency=None):
        if not currency:
            return self.self_PLN
        return getattr(self, f'self_{currency}')
    self = property(get_self)

