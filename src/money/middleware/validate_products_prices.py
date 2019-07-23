from django.utils.deprecation import MiddlewareMixin
from products.models import Product
from money.models import ShippingPrice

class ValidateProductsPrices(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/admin/'):
            return None
        products = Product.objects.all_active()
        for product in products:
            try:
                if product.promo_active:
                    if not product.prices.promo or product.prices.promo == 0.0:
                        raise Exception(f"Null promo price in active product: {product}")
                else:
                    if not product.prices.regular or product.prices.regular == 0.0:
                        raise Exception(f"Null regular price in active product: {product}")
            except:
                raise Exception(f"NO PRICES in active product: {product}")


class ValidateShippingPrices(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/admin/'):
            return None
        shipping = ShippingPrice.objects.all()
        if not shipping:
            raise Exception(f"NO SHIPPING PRICE MODEL INSTANCE IN DATABASE!")
        else:
            shipping = shipping.first()
            if shipping.local.amount == 0.0 or shipping.international.amount == 0.0:
                raise Exception(f"SHIPPING PRICES NOT DEFINED IN MODEL INSTANCE!")
