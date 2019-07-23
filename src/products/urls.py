from django.conf.urls import url
from .models import Product

from products.views import (
    ProductCategoriesView,
    ProductListView,
    ProductDetailSlugView,
    MultipleProductListView
)


camera_category_regex = "^offer/(?P<category>" + '|'.join(Product.CAMERA_CATEGORIES) + ")/$"
multiple_products_category_regex = "^offer/(?P<category>" + '|'.join(Product.MULTIPLE_PRODUCTS_CATEGORIES) + ")/$"


urlpatterns = [
    url(r'^offer/$', ProductCategoriesView, name='offer'),
    url(r'{}'.format(camera_category_regex), ProductListView.as_view(), name='list'),
    url(r'{}'.format(multiple_products_category_regex), MultipleProductListView.as_view(), name='multiple_list'),
    url(r'^(?P<slug>[\w-]+)/$', ProductDetailSlugView.as_view(), name='detail'),
]
