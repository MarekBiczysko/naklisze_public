from django.contrib import admin

# Register your models here.
from .models import ProductPrice, ShippingPrice

class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ['product', 'category', 'regular', 'promo']

    def category(self, obj):
        return obj.product.category

class ShippingPriceAdmin(admin.ModelAdmin):
    list_display = ['local', 'international', 'self']

admin.site.register(ProductPrice, ProductPriceAdmin)
admin.site.register(ShippingPrice, ShippingPriceAdmin)