from django.db import models, transaction
from djmoney.money import Money
from django.db.models.signals import pre_save, post_save, m2m_changed
from django.conf import settings

from djmoney.models.fields import MoneyField

from products.models import Product

import sys

from sklep.log import loger

User = settings.AUTH_USER_MODEL


class CartManager(models.Manager):

    @transaction.atomic()
    def new_or_get(self, request, select_for_update=False):
        cart_id = request.session.get("cart_id", None)
        # qs = Cart.objects.filter(id=cart_id)
        qs = self.get_queryset().filter(id=cart_id)

        if qs.count() == 1:
            if select_for_update:
                qs = qs.select_for_update()

            new_obj = False
            cart_obj = qs.first()
            if request.user.is_authenticated() and cart_obj.user is None:
                cart_obj.user = request.user
                cart_obj.save()
        else:
            new_obj = True
            cart_obj = self.new(user=request.user)
            if select_for_update:
                self.get_queryset().filter(id=cart_obj.id).select_for_update()

            request.session['cart_id'] = cart_obj.id

        return cart_obj, new_obj

    @transaction.atomic()
    def get(self, request):
        cart_id = request.session.get("cart_id", None)

        if cart_id:
            qs = self.get_queryset().filter(id=cart_id)
            if qs:
                qs = qs.select_for_update()
                cart_obj = qs.first()
                if request.user.is_authenticated() and cart_obj.user is None:
                    cart_obj.user = request.user
                    cart_obj.save()

                return cart_obj

        return None

    @transaction.atomic()
    def new(self, user=None):
        user_obj = None
        if user is not None:
            if user.is_authenticated():
                user_obj = user

        return self.model.objects.create(user=user_obj)


class Cart(models.Model):
    user                = models.ForeignKey(User, null=True, blank=True)
    products            = models.ManyToManyField(Product, blank=True)
    total               = MoneyField(decimal_places=2, max_digits=10, null=True, blank=True, default_currency=settings.DEFAULT_CURRENCY)
    timestamp           = models.DateTimeField(auto_now_add=True)
    updated             = models.DateTimeField(auto_now=True)
    currency            = models.CharField(max_length=3, default=settings.DEFAULT_CURRENCY)

    objects = CartManager()

    def __str__(self):
        return  str(self.id)

    def product_list(self):
        return [product.id for product in self.products.all()]

    @transaction.atomic()
    def recalculate_values(self, new_currency=None):
        loger.info(
            f'Recalculating cart {self.id} values, currency: {self.currency}, entry total cart value: {self.total}')

        products = self.products.all().select_for_update()
        currency = self.currency

        if new_currency:
            if new_currency != self.currency:
                self.currency = new_currency
                currency = new_currency

        if products:
            total = sum(
                [product.prices.get_promo(currency) if (product.promo_active)
                 else product.prices.get_regular(currency) for product in products]
            )
        else:
            total = Money(0.00, currency)
        self.total = total
        self.save()

        loger.info(
            f'Recalculated cart {self.id} values, currency: {self.currency}, new total cart value: {self.total}')


def m2m_changed_cart_receiver(sender, instance, action, *args, **kwargs):
    """Update cart on cart.products quantity change"""
    if (action in ['post_remove', 'post_add', 'post_clear'] and not 'loaddata' in sys.argv):
        instance.recalculate_values()

m2m_changed.connect(m2m_changed_cart_receiver, sender=Cart.products.through)
