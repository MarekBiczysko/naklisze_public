from django.shortcuts import render, Http404
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import ugettext as _

from itertools import chain

from sklep.log import loger
from .models import Product, Camera, DICT_CATEGORIES_CHOICES
from carts.models import Cart
from analytics.mixins import ObjectViewedMixin


PAGINATION_PRODUCTS_NUMBER = 12


def ProductCategoriesView(request):
    context = {
    }
    return render(request, 'products/offer.html', context)


class ProductListView(ListView):
    template_name = 'products/list.html'

    def get_context_data(self, *args, **kwargs):
        request = self.request
        category = self.kwargs.get('category')
        category_name = DICT_CATEGORIES_CHOICES.get(category)

        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(request)

        context['cart'] = cart_obj
        context['category'] = category_name

        if category in Product.CAMERA_CATEGORIES:
            brands = list(set(Camera.objects.all_active().filter(category=category).values_list('brand', flat=True)))
            context['brands'] = sorted(brands)

        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        category = self.kwargs.get('category')

        brand = request.GET.get('brand')

        qs_available = Product.objects.all_available().filter(category=category).order_by('-timestamp')
        qs_visible_sold = Product.objects.visible_sold().filter(category=category)

        if brand:
            qs_available = qs_available.filter(camera__brand=brand)
            qs_visible_sold = qs_visible_sold.filter(camera__brand=brand)

        qs = list(chain(qs_available, qs_visible_sold))

        return paginator(request, qs)


class MultipleProductListView(ProductListView):
    template_name = 'products/list.html'

    def get_queryset(self, *args, **kwargs):
        request = self.request
        category = self.kwargs.get('category')
        cart_obj, new_obj = Cart.objects.new_or_get(request)

        qs              = Product.objects.all_active().filter(category=category).order_by('-timestamp')
        qs_available    = qs.available()
        qs_notinbasket  = qs_available.exclude(id__in=cart_obj.product_list())

        # if there are products still not available and not in basket
        if qs_notinbasket:
            qs = qs_notinbasket
        # elif all products are in basket (thumb up visible in prod cart:))
        elif qs_available:
            qs = qs_available
        # else show that all unique products are sold

        unique_items = Product.make_qs_unique(qs)

        return paginator(request, unique_items)


class ProductDetailSlugView(ObjectViewedMixin, DetailView):
    template_name = 'products/detail.html'

    def get_context_data(self, *args, **kwargs):
        request = self.request
        context = super(ProductDetailSlugView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        context['cart'] = cart_obj
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')

        try:
            instance = Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            raise Http404(_("Brak produktu w bazie"))
        except Product.MultipleObjectsReturned:
            qs = Product.objects.filter(slug=slug)
            instance = qs.first()
            loger.warning(f'MultipleObjectsReturned in ProductDetailSlugView, returning {instance} from {qs}')

        return instance


def paginator(request, qs):
    paginator = Paginator(qs, PAGINATION_PRODUCTS_NUMBER)
    page = request.GET.get('page')
    try:
        paginated_qs = paginator.page(page)
    except PageNotAnInteger:
        paginated_qs = paginator.page(1)
    except EmptyPage:
        paginated_qs = paginator.page(paginator.num_pages)
    return paginated_qs
