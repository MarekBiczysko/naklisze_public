from django.views.generic import ListView

from analytics.models import SearchQueries
from products.models import Product
from carts.models import Cart
from sklep.log import loger


class SearchProductView(ListView):
    template_name = 'search/view.html'

    def get_context_data(self, *args, **kwargs):
        request = self.request
        context = super(SearchProductView, self).get_context_data()
        context['query'] = self.request.GET.get('q')
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        query = request.GET.get('q')
        if query is not None:
            SearchQueries.objects.new(request, query)

            results = Product.objects.search(query).order_by('-timestamp')
            if results is not None:
                qs = Product.make_qs_unique(results)
                return qs
        loger.info(f'No search results for query {query}, rendering featured products instead')
        return Product.objects.featured()
