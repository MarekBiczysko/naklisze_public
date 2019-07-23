from django.contrib import admin
from django.core.urlresolvers import resolve
from modeltranslation.admin import TranslationAdmin

from .models import Product, Camera, Strap, Button, ProductImage, CameraSample
from money.models import ProductPrice

from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
)


def make_all_available(modeladmin, request, queryset):
    queryset.update(selled=False)
    queryset.update(active=True)

make_all_available.short_description = "Mark selected products as active and available"


def resave_thumbnails(modeladmin, request, queryset):
    for obj in queryset:
        samples = CameraSample.objects.filter(product=obj)
        images = obj.images.all()
        if images:
            for image in images:
                image.save()
        if samples:
            for sample in samples:
                sample.save()


resave_thumbnails.short_description = "Make new thumbnails from original images"

class ProductPriceInline(admin.StackedInline):
    model = ProductPrice
    extra = 1
    max_num = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 5

class CameraSampleInline(admin.TabularInline):
    model = CameraSample


class ProductChildAdmin(PolymorphicChildModelAdmin):
    """ Base admin class for all child models """
    base_model = Product  # Optional, explicitly set here.
    readonly_fields = [
        'slug',
    ]

    # By using these `base_...` attributes instead of the regular ModelAdmin `form` and `fieldsets`,
    # the additional fields of the child models are automatically added to the admin form.
    """
    base_form = ...
    base_fieldsets = (
        ...
    )
    """

    inlines = (ProductImageInline, ProductPriceInline)
    save_as = True
    # Copy ProductImage inlines to new object when using 'save as' button
    # double save() method to avoid error : 'save() prohibited to prevent data loss due to unsaved related object'
    def save_model(self, request, obj, form, change):
        # Django always sends this when "Save as new is clicked"
        obj.save()
        if '_saveasnew' in request.POST:
            # Get the ID from the admin URL
            original_pk = resolve(request.path).args[0]
            # Get the original object
            original_obj = obj._meta.concrete_model.objects.get(id=original_pk)

            # Create ProductImage objects with foreign key to new copied Product object
            original_images = ProductImage.objects.filter(product=original_obj)
            for image in original_images:
                ProductImage.objects.create(product=obj, image=image.image)
        obj.save()


class CameraAdmin(ProductChildAdmin):
    base_model = Camera  # Explicitly set here!
    # show_in_index = True  # makes child model admin visible in main admin site
    # define custom features here
    fields = (
        'title',
        'category',
        'brand',
        'model',
        'active',
        'selled',
        'promo_active',
        'featured',
        'serial_number',
        'quality',
        'production_date',
        'description',
        'spec_table',
        'set_description',
        'info_links',
        'tags',
        'slug',
    )

    inlines = ProductChildAdmin.inlines + (CameraSampleInline,)


class StrapAdmin(ProductChildAdmin):
    base_model = Strap
    fields = (
        'title',
        'type',
        'model',
        'active',
        'selled',
        'promo_active',
        'featured',
        'description',
        'tags',
        'slug',
        'category',
    )


class ButtonAdmin(ProductChildAdmin):
    base_model = Button
    fields = (
        'title',
        'model',
        'active',
        'selled',
        'promo_active',
        'featured',
        'description',
        'tags',
        'category',
        'slug',
    )


class ProductParentAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    base_model = Product  # Optional, explicitly set here.
    child_models = (
        Camera,
        Strap,
        Button,
    )

    list_filter = (PolymorphicChildModelFilter,)
    list_display = (
        'title',
        'category',
        'get_info',
        'active',
        'selled',
        'featured',
        'get_regular_price',
        'get_promo_price',
        'promo_active',
    )
    actions = [make_all_available, resave_thumbnails]

    def price_reg(self, object):
        return object.price.reg

    def price_promo(self, object):
        return object.price.promo

    def get_info(self, obj):
        id = obj.id
        try:
            return Camera.objects.all().filter(id=id).first().serial_number
        except:
            pass
        try:
            return Strap.objects.all().filter(id=id).first().model
        except:
            pass
        try:
            return Button.objects.all().filter(id=id).first().model
        except:
            pass

    get_info.short_description = 'Model/Serial No'  # Renames column head

    def get_regular_price(self, obj):
        return obj.prices.regular

    get_regular_price.short_description = 'Price'  # Renames column head
    
    def get_promo_price(self, obj):
        return obj.prices.promo

    get_promo_price.short_description = 'Promo price'  # Renames column head


@admin.register(Product)
class MyTranslatedProductAdmin(ProductParentAdmin, TranslationAdmin):
    pass

@admin.register(Camera)
class MyTranslatedCameraAdmin(CameraAdmin, TranslationAdmin):
    pass

@admin.register(Strap)
class MyTranslatedStrapAdmin(StrapAdmin, TranslationAdmin):
    pass

@admin.register(Button)
class MyTranslatedButtonAdmin(ButtonAdmin, TranslationAdmin):
    pass
