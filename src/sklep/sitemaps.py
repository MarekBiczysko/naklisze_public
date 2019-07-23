from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

from products.models import Product


class StaticViewSitemap(Sitemap):

    def items(self):
        return ['home_page', 'about', 'search:query', 'products:offer']

    def location(self, obj):
        return reverse(obj)


class ProductsViewSitemap(Sitemap):

    def items(self):
        return Product.objects.all_active()


class ProductCategoriesViewSitemap(Sitemap):

    def items(self):
        return Product.CAMERA_CATEGORIES + Product.MULTIPLE_PRODUCTS_CATEGORIES

    def location(self, obj):
        url = 'products:list' if obj in Product.CAMERA_CATEGORIES else 'products:multiple_list'
        return reverse(url, kwargs={'category': obj})
