from django.db import models, transaction
from django.db.models.signals import pre_save, post_save
from django.utils.datetime_safe import datetime
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from decimal import Decimal
from djmoney.models.fields import MoneyField

from carts.models import Cart
from sklep.log import loger
from sklep.utils import uniqe_order_id_generator
from billing.models import BillingProfile
from addresses.models import Address
from money.models import ShippingPrice


ORDER_STATUS_CHOICES = (
    ('created', _('Stworzone')),
    ('done', _('Zatwierdzone')),
    ('paid', _('Zapłacone')),
    ('shipped', _('Wysłane')),
    ('refunded', _('Zwrot'))
)

ORDER_LOGGED_USER_PROMO = Decimal(5)


class OrderManager(models.Manager):
    def new_or_get(self, cart_obj, billing_profile, select_for_update=False):
        created = False
        qs = self.get_queryset().filter(
                cart=cart_obj,
                billing_profile=billing_profile,
                active=True,
                status='created'
            )

        if qs.count() == 1:
            if select_for_update:
                qs = qs.select_for_update()
            obj = qs.first()
        else:
            obj = self.model.objects.create(cart=cart_obj, billing_profile=billing_profile)
            if select_for_update:
                self.get_queryset().select_for_update().filter(id=obj.id)
            created = True
        return obj, created

    def user_orders_history(self, user):
        qs = self.get_queryset().filter(billing_profile__email=user.email).exclude(
                status='created').order_by('-timestamp')
        return qs

    def all_confirmed(self):
        qs = self.get_queryset().all().exclude(status__in=['created', 'refunded']).order_by('-timestamp')
        return qs


class Order(models.Model):
    order_id            = models.CharField(max_length=60, blank=True)
    timestamp           = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    status              = models.CharField(max_length=20, default='created', choices=ORDER_STATUS_CHOICES)
    active              = models.BooleanField(default=True)

    billing_profile     = models.ForeignKey(BillingProfile, null=True, blank=True)
    shipping_address    = models.ForeignKey(Address, related_name="shipping_address", null=True, blank=True)
    billing_address     = models.ForeignKey(Address, related_name="billing_address", null=True, blank=True)
    shipping_type       = models.CharField(max_length=20, default='local')

    cart                = models.ForeignKey(Cart)
    products_cost       = MoneyField(decimal_places=2, max_digits=10, null=True, blank=True, default_currency=settings.DEFAULT_CURRENCY)
    shipping_price      = MoneyField(decimal_places=2, max_digits=10, null=True, blank=True, default_currency=settings.DEFAULT_CURRENCY)
    total               = MoneyField(decimal_places=2, max_digits=10, null=True, blank=True, default_currency=settings.DEFAULT_CURRENCY)
    logged_user_promo   = models.DecimalField(default=0, max_digits=10, decimal_places=0)
    currency            = models.CharField(max_length=3, default=settings.DEFAULT_CURRENCY)

    comment             = models.TextField(blank=True, null=True, default="", max_length=500)
    shipping_info       = models.TextField(blank=True, null=True, default="", max_length=200)

    objects = OrderManager()

    def __str__(self):
        return self.order_id

    def update_date(self):
        self.timestamp = datetime.now()
        self.save()

    def update_logged_user_promo(self):
        if self.billing_profile.user is not None:
            self.logged_user_promo = ORDER_LOGGED_USER_PROMO

    def create_or_update_shipping(self, new_shipping_type, currency):
        shipping_price_obj = ShippingPrice.objects.first()
        if new_shipping_type:
            new_shipping_price = getattr(shipping_price_obj, f'get_{new_shipping_type}')(currency)
            self.shipping_price = new_shipping_price
            self.shipping_type = new_shipping_type
            loger.info(f'Set new shipping type: {new_shipping_type} with price {new_shipping_price} in order {self}')
        else:
            new_shipping_price = getattr(shipping_price_obj, f'get_{self.shipping_type}')(currency)
            self.shipping_price = new_shipping_price
            loger.info(f'Set new shipping price {new_shipping_price} in order {self}')

        return new_shipping_price

    def update_all(self, new_shipping_type=None):
        self.update_logged_user_promo()
        self.currency =  self.cart.currency
        shipping_price = self.create_or_update_shipping(new_shipping_type, self.cart.currency)
        self.products_cost = self.cart.total
        promotion_factor = Decimal((100 - self.logged_user_promo) / 100)
        self.total = self.cart.total * promotion_factor + shipping_price
        self.save()

        loger.info(f'Updated all stuff in order {self}')

    def check_if_done(self):
        if self.billing_profile and self.shipping_address and self.billing_address and self.total.amount > 0:
            loger.info(f'Order {self} is done')
            return True
        loger.info(
            f'Order {self} is NOT done,'
            f' billing_profile={self.billing_profile},'
            f' billing_address={self.billing_address},'
            f' shipping_address={self.shipping_address},'
            f' total amount={self.total.amount}')
        return False

    def mark_as_done(self):
        self.status = 'done'
        self.save()

    def add_comment(self, comment):
        self.comment = comment
        self.save()

    def print_order(self):
        a = _("Zamówienie nr:")
        b = _("Adres dostawy:")
        c = _("Status:")
        d = _("Całkowity koszt:")
        return f" {a} {self.order_id} \n {b} {self.shipping_address} \n {c} {self.status} \n {d} {self.total}"

    def print_order_html(self):
        a = _("Data zamówienia:")
        b = _("Adres dostawy:")
        c = _("Dane kupującego:")
        d = _("Koszt produktów")
        e = _("Koszt przesyłki")
        f = _("Rabat")
        g = _("Całkowity koszt")
        h = _("Komentarz:")
        i = _("Status:")
        j = _("Dane przesyłki:")

        order_list = [
            f"{a} {self.timestamp.strftime('%Y-%m-%d')}",
            f"{b} {self.shipping_address.print_address() if self.shipping_address else '-'}",
            f"{c} {self.billing_address.print_address() if self.billing_address else '-'}",
            f"{d} {self.products_cost}",
            f"{e} {self.shipping_price}",
            f"{f} {self.logged_user_promo} %",
            f"{g} {self.total}",
            f"{h} {self.comment}",
            f"{i} {self.get_status_display()}",
            f"{j} {self.shipping_info}"
        ]
        return  order_list

    def products(self):
        return self.cart.products.all()


def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not kwargs.get('raw', False):
        if not instance.order_id:
            instance.order_id = uniqe_order_id_generator(instance)
            loger.info(f'Created new order_id {instance.order_id} for order {instance}')
        qs = Order.objects.filter(cart=instance.cart).exclude(billing_profile=instance.billing_profile)
        if qs.exists():
            qs.update(active=False)
            loger.info(f'Stale orders qs was marked as active=false, qs: {qs}')


pre_save.connect(pre_save_create_order_id, sender=Order)

@transaction.atomic()
def post_save_cart_total(sender, instance, created,  *args, **kwargs):
    if not created and not kwargs.get('raw', False):
        cart_obj = instance
        cart_id = cart_obj.id
        qs = Order.objects.select_for_update().filter(cart__id=cart_id, active=True)
        if qs.count() == 1:
            order_obj = qs.first()
            order_obj.update_all()

            loger.info(f'Cart {cart_id} was changed so updated order {order_obj}')

post_save.connect(post_save_cart_total, sender=Cart)

@transaction.atomic()
def post_save_order_total(sender, instance, created, *args, **kwargs):
    if created and not kwargs.get('raw', False):
        order_id = instance.id
        qs = Order.objects.select_for_update().filter(id=order_id)
        if qs.count() == 1:
            order_obj = qs.first()
            order_obj.update_all()

            loger.info(f'Order {order_obj} was changed so it was updated')

post_save.connect(post_save_order_total, sender=Order)
