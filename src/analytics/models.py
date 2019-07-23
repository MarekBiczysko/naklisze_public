from django.db import models, transaction
from django.conf import settings

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .signals import object_viewed_signal
from .utils import get_client_ip
from accounts.models import GuestEmail

User = settings.AUTH_USER_MODEL

PRODUCTS_CLASSES = ['Camera', 'Strap', 'Button']


class ObjectViewedManager(models.Manager):
    def viewed_products(self):
        c_types = [ ContentType.objects.get(app_label='products', model=model_class) for model_class in PRODUCTS_CLASSES ]
        return self.get_queryset().filter(content_type__in=c_types).order_by('-timestamp')

    def viewed_products_for_user(self, user):
        from django.apps import apps  # to avoid circular imports
        product_model = apps.get_model('products', 'Product')
        viewed_history = user.objectviewed_set.viewed_products()
        viewed_products_ids = [x.object_id for x in viewed_history]
        # viewed_products = Product.objects.filter(id__in=viewed_products_ids)  # no chronology!
        # viewed_products = [Product.objects.get(id=prod_id) for prod_id in viewed_products_ids]  # proper chronology but no exception handling

        # only proper solution
        viewed_products = []
        for prod_id in viewed_products_ids:
            try:
                viewed_products.append(product_model.objects.get(id=prod_id))
            except product_model.DoesNotExist:
                pass

        unique_viewed_products = product_model.make_qs_unique(viewed_products)

        return unique_viewed_products[:10]


class ObjectViewed(models.Model):
    user            = models.ForeignKey(User, blank=True, null=True) # User instance
    guest_email     = models.ForeignKey(GuestEmail, blank=True, null=True)
    ip_address      = models.CharField(max_length=120, blank=True, null=True)
    content_type    = models.ForeignKey(ContentType) # Product, Order, Cart, Address...
    object_id       = models.PositiveIntegerField() # UserId, ProductId, OrderId...
    content_object  = GenericForeignKey('content_type', 'object_id') # Product instance, ....
    timestamp       = models.DateTimeField(auto_now_add=True)

    objects = ObjectViewedManager()

    def __str__(self):
        return f"{self.user} viewed {self.content_object} on {self.timestamp}"


    class Meta:
        ordering = ['-timestamp'] # most recent showed first
        verbose_name = 'Object viewed'
        verbose_name_plural = 'Objects viewed'

def object_viewed_receiver(sender, instance, request, *args, **kwargs):
    c_type = ContentType.objects.get_for_model(sender)  #  same as instance.__class__

    user = None
    guest_email = None

    if request.user.is_authenticated():
        user = request.user
    else:
        guest_email_id = request.session.get('guest_email_id')
        if guest_email_id:
            guest_email = GuestEmail.objects.get(id=guest_email_id)

    new_view_obj = ObjectViewed.objects.create(
        user = user,
        guest_email = guest_email,
        content_type = c_type,
        ip_address = get_client_ip(request),
        object_id = instance.id

    )

object_viewed_signal.connect(object_viewed_receiver)


class SearchQueriesManager(models.Manager):

    @transaction.atomic()
    def new(self, request, query):
        guest_email_id = request.session.get("guest_email_id")
        user = request.user

        if user.is_authenticated:
            return self.model.objects.create(user=user, query=query)

        elif guest_email_id:
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            return self.model.objects.create(guest_email=guest_email_obj, query=query)
        else:
            return self.model.objects.create(query=query)

    def clients_queries(self):
        return self.model.objects.all().order_by('-timestamp').exclude(user__username='admin')


class SearchQueries(models.Model):
    user            = models.ForeignKey(User, blank=True, null=True) # User instance
    guest_email     = models.ForeignKey(GuestEmail, blank=True, null=True)
    query           = models.CharField(max_length=120, blank=True, null=True)
    timestamp       = models.DateTimeField(auto_now_add=True)

    objects = SearchQueriesManager()
