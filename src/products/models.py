import os
import random

from io import BytesIO
from PIL import Image
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from django.db import models
from django.db.models.signals import post_save
from django.db.models import Q

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager
from polymorphic.query import  PolymorphicQuerySet

from analytics.models import ObjectViewed
from sklep.log import loger
from sklep.utils import unique_slug_generator

from .schemes.txt_data_button import BUTTON_MODEL_CHOICES, BUTTON_DESCRIPTION_PL, BUTTON_DESCRIPTION_EN
from .schemes.txt_data_strap import STRAP_DESCRIPTION_PL, STRAP_DESCRIPTION_EN, STRAP_MODEL_CHOICES, STRAP_TYPE_CHOICES
from .schemes.txt_data_camera import CAMERA_DEFAULT_DESCRIPTION, DEFAULT_SPEC_TABLE, DEFAULT_SET_DESCRIPTION


CATEGORIES_CHOICES = (
    ('range', _('Aparaty dalmierzowe')),
    ('half', _('Aparaty połówkowe')),
    ('compact', _('Aparaty kompaktowe')),
    ('medium', _('Aparaty średnioformatowe')),
    ('straps', _('Paski')),
    ('buttons', _('Przyciski spustu'))
)

DICT_CATEGORIES_CHOICES = dict(CATEGORIES_CHOICES)


def split_filename(filename):
    base_name = os.path.basename(filename)
    name, ext = os.path.splitext(base_name)
    return name, ext

def upload_image_path(instance, filename):
    new_filename = random.randint(1, 999999)
    name, ext = split_filename(filename)
    final_filename = f"{new_filename}{ext}"
    return f"products/{instance.product.slug}/{final_filename}"

def _create_thumbnail(img_obj):
    THUMBNAIL_SIZE = (300, 200)
    org_img_path = img_obj.image.name

    if org_img_path.endswith(".jpg"):
        PIL_TYPE = 'jpeg'
        FILE_EXTENSION = 'jpg'
        DJANGO_TYPE = 'image/jpeg'

    elif org_img_path.endswith(".png"):
        PIL_TYPE = 'png'
        FILE_EXTENSION = 'png'
        DJANGO_TYPE = 'image/png'

    else:
        loger.error(f'Not supported file format {org_img_path}, not creating thumbnail')
        return

    original_img = Image.open(BytesIO(img_obj.image.read()))
    original_img.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

    tmp_handle = BytesIO()
    original_img.save(tmp_handle, PIL_TYPE)
    tmp_handle.seek(0)

    suf = SimpleUploadedFile(os.path.split(img_obj.image.name)[-1],
                             tmp_handle.read(), content_type=DJANGO_TYPE)

    img_obj.thumbnail.save(
        f"tmpname.{FILE_EXTENSION}",
        suf,
        save=False
        )


class ProductQuerySet(PolymorphicQuerySet):
    def featured(self):
        return self.filter(featured=True)

    def active(self):
        return self.filter(active=True)

    def available(self):
        return self.filter(selled=False)

    def sold(self):
        return self.filter(selled=True)

    def promoted(self):
        return self.filter(promo_active=True)

    def search(self, query):
        queries = query.split(' ')
        q_names = Q()
        q_tags = Q()
        for query in queries:
            q_names |= Q(title__icontains=query)
            q_tags |= Q(tags__icontains=query)
        lookups = q_names | q_tags
        return self.filter(lookups).distinct()


class ProductManager(PolymorphicManager):
    def all(self):
        return self.get_queryset()

    def all_active(self):
        return self.get_queryset().active()

    def all_available(self):
        return self.get_queryset().active().available()

    def visible_sold(self):
        return self.get_queryset().active().sold()

    def all_promo(self):
        return self.all_available().promoted()

    def latest(self):
        qs = self.all_available().order_by('-timestamp')
        return qs

    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)
        if qs.count() == 1:
            return qs.first()
        else:
            return None

    def featured(self):
        return self.all_available().filter(featured=True)

    def search(self, query):
        return self.all_available().search(query)


class Product(PolymorphicModel):
    title           = models.CharField(null=True, blank=True, max_length=120)
    slug            = models.SlugField(null=True, blank=True, unique=True)
    promo_active    = models.BooleanField(default=False)
    featured        = models.BooleanField(default=False)
    active          = models.BooleanField(default=True)
    timestamp       = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    tags            = models.TextField(null=True, blank=True)
    selled          = models.BooleanField(default=False)
    category        = models.CharField(max_length=120, null=True, blank=True, choices=CATEGORIES_CHOICES)

    CAMERA_CATEGORIES = ['range', 'half', 'compact', 'medium']
    MULTIPLE_PRODUCTS_CATEGORIES = ['straps', 'buttons']

    objects = ProductManager()

    def __str__(self):
        return self.title

    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self.__class__)

    @property
    def no_of_views(self):
        return ObjectViewed.objects.filter(
            content_type=self.content_type, object_id=self.id
        ).exclude(
            user__username='admin'
        ).count()

    @staticmethod
    def make_qs_unique(qs):
        # sqllite limitation in distinct per model field workaround
        unique_items, item_model = [], []
        for item in qs:
            if hasattr(item, 'serial_number'): # only Camera products have serial number so they are unique by definition
                unique_items.append(item)
            elif item.model not in item_model:
                unique_items.append(item)
                item_model.append(item.model)
        return unique_items


    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})

    def get_category_url(self):
        if self.category in self.CAMERA_CATEGORIES:
            return reverse('products:list', kwargs={'category': self.category})
        elif self.category in self.MULTIPLE_PRODUCTS_CATEGORIES:
            return reverse('products:multiple_list', kwargs={'category': self.category})
        else:
            return "/products/offer/"

    def get_category_name(self):
        return self.get_category_display()

    def make_inactive(self):
        self.active = False
        self.save()

    def make_selled(self):
        self.selled = True
        self.save()

    def is_camera(self):
        return isinstance(self, Camera)

    def is_multiple(self):
        return (self.category in self.MULTIPLE_PRODUCTS_CATEGORIES)

    def title_image(self):
        self.check_or_create_default_image()
        return self.images.all()[0].thumbnail.url

    def all_images(self):
        self.check_or_create_default_image()
        return [obj for obj in self.images.all()]

    def all_thumbs(self):
        return [obj.thumbnail.url for obj in self.images.all()]

    def check_or_create_default_image(self):
        try:
            img = self.images.all()[0]
        except IndexError:
            loger.debug(f'No default image for Product {self}, creating it')
            ProductImage.create_default(self)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_image_path, default='default_min.jpg')
    thumbnail = models.ImageField(upload_to=upload_image_path, max_length=500, default='default_min.jpg')

    @staticmethod
    def create_default(product_obj):
        product_images = ProductImage.objects.filter(product=product_obj)
        if not product_images:
            ProductImage.objects.create(product=product_obj)

    def save(self, *args, **kwargs):
        _create_thumbnail(self)
        force_update = False
        if self.id:
            force_update = True
        super(ProductImage, self).save(force_update=force_update)


class Camera(Product):
    brand           = models.CharField(max_length=60, blank=True, null=True)
    model           = models.CharField(max_length=60, blank=True, null=True)
    serial_number   = models.CharField(max_length=20, blank=True, null=True, default='-')
    quality         = models.IntegerField(null=True, blank=True)
    set_description = models.TextField(max_length=200, blank=True, null=True, default=DEFAULT_SET_DESCRIPTION)
    description     = models.TextField(default=CAMERA_DEFAULT_DESCRIPTION)
    spec_table      = models.TextField(max_length=300, blank=True, null=True, default=DEFAULT_SPEC_TABLE)
    production_date = models.CharField(max_length=20, blank=True, null=True, default=' - ')
    info_links      = models.TextField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return f"{self.brand} : {self.model}"

    def __init__(self, *args, **kwargs):
        super(Camera, self).__init__(*args, **kwargs)

    def make_title(self):
        self.title = self.title_en = f'{self.brand} {self.model}'
        self.save()

    def order_title(self):
        camera = _("Aparat")
        return f'{camera} {self.brand} {self.model} (no.{self.serial_number})'

    def tuple_spec_table(self):
        # creates table of tuples of product technical details, ex. input: lens @ 10mm &
        table = []
        pair = []
        curr = ''
        for word in self.spec_table.split():
            if word == '@':
                pair.append(curr)
                curr = ''
            elif word == '&':
                pair.append(curr)
                curr = ''
                table.append(pair)
                pair = []
            else:
                curr += word + ' '
        return table

    def set_items(self):
        # creates table of product attributes, ex input: camera &
        table = []
        curr = ''
        for word in self.set_description.split():
            if word == '&':
                table.append(curr)
                curr = ''
            else:
                curr += word + ' '
        return table

    def all_info_links(self):
        return [link for link in self.info_links.split()] if self.info_links else False

    def all_samples(self):
        # return self.samples.all()[0].sample.url
        return [obj for obj in self.samples.all()]

    def print_attr(self):
        return [
            (_("Numer seryjny"), self.serial_number),
            (_("Stan"), self.quality),
            (_("Lata produkcji"), self.production_date)
            ]


class CameraSample(models.Model):
    product = models.ForeignKey(Camera, related_name='samples', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_image_path, null=True, blank=True, default='default_min.jpg')
    thumbnail = models.ImageField(upload_to=upload_image_path, max_length=500, default='default_min.jpg')

    def save(self, *args, **kwargs):
        _create_thumbnail(self)
        force_update = False
        if self.id:
            force_update = True
        super(CameraSample, self).save(force_update=force_update)


class Strap(Product):
    type        = models.CharField(max_length=120, null=True, blank=True, choices=STRAP_TYPE_CHOICES)
    model       = models.CharField(max_length=120, null=True, blank=True, choices=STRAP_MODEL_CHOICES)
    description = models.TextField(max_length=500,  null=True, blank=True)

    def __str__(self):
        return f"{self.get_type_display()} : {self.get_model_display()}"

    def make_title(self):
        self.title = f'Pasek {self.get_type_display()}'
        self.title_en = f'Strap'
        self.save()

    def make_description(self):
        self.description = STRAP_DESCRIPTION_PL
        self.description_en = STRAP_DESCRIPTION_EN
        self.save()

    def set_category(self):
        self.category = 'straps'
        self.save()

    def print_attr(self):
        return [("Model", f"{self.get_model_display()}")]

    def order_title(self):
        return f'{self.title} : {self.get_model_display()}'


class Button(Product):
    model       = models.CharField(max_length=120, null=True, blank=True, choices=BUTTON_MODEL_CHOICES)
    description = models.TextField(max_length=500,  null=True, blank=True)

    def __str__(self):
        return f"{self.get_model_display()}"

    def set_category(self):
        self.category = 'buttons'
        self.save()

    def make_title(self):
        self.title = 'Przycisk spustu'
        self.title_en = 'Trigger button'
        self.save()

    def make_description(self):
        self.description = BUTTON_DESCRIPTION_PL
        self.description_en = BUTTON_DESCRIPTION_EN
        self.save()

    def print_attr(self):
        return [(_("Kolor"), f"{self.get_model_display()}")]

    def order_title(self):
        return f'{self.title} : {self.get_model_display()}'


def product_post_save_receiver(sender, instance, created, *args, **kwargs):
    if (created and not kwargs.get('raw', False)):

        if not instance.title:
            instance.make_title()

        if not instance.description:
            try:
                instance.make_description()
            except AttributeError:
                pass

        if not instance.category:
            try:
                instance.set_category()
            except AttributeError:
                pass

        if not instance.slug:
            instance.slug = unique_slug_generator(instance)
            instance.save()

for subclass in Product.__subclasses__():
    post_save.connect(product_post_save_receiver, sender=subclass)

