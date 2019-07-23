from django.contrib import admin

from .models import Cart


class CartAdmin(admin.ModelAdmin):
    list_display = ['__str__','user', 'total', 'currency', 'products_list', 'timestamp']
    ordering = ['-timestamp']

    def products_list(self, object):
        return [str(prod) for prod in object.products.all()]


admin.site.register(Cart, CartAdmin)
