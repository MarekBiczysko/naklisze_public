from django.contrib import admin

from .models import Order

class OrderAdmin(admin.ModelAdmin):
    list_display = ['timestamp', '__str__', 'billing_profile', 'logged_user_promo', 'total', 'status']
    ordering = ['-timestamp']

    readonly_fields = [
        'cart',
        'order_cart_products',
    ]

    class Meta:
        model = Order

    def order_cart_products(self, object):
        return [str(prod) for prod in object.cart.products.all()]


admin.site.register(Order, OrderAdmin)
