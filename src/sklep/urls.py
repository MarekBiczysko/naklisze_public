from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.views.i18n import javascript_catalog

from django.conf import settings
from django.conf.urls.static import static

from .views import home_page, AboutPageView, cookies_policy, regulations_page, ChangeLanguageView
from money.views import ChangeCurrencyView

from sklep.sitemaps import StaticViewSitemap, ProductsViewSitemap, ProductCategoriesViewSitemap
from django.contrib.sitemaps.views import sitemap


sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductsViewSitemap,
    'categories': ProductCategoriesViewSitemap
}


urlpatterns = [
    url(r'^$', home_page, name='home_page'),
    url(r'^about/$', AboutPageView.as_view(), name='about'),
    url(r'^analytics/', include("analytics.urls", namespace='analytics')),
    url(r'^orders/', include("orders.urls", namespace='orders')),
    url(r'^regulations/$', regulations_page, name='regulations'),
    url(r'^cookies/$', cookies_policy, name='cookies'),
    url(r'^accounts/', include("accounts.urls", namespace='accounts')),
    url(r'^accounts/', include("accounts.passwords.urls")),
    url(r'^products/', include("products.urls", namespace='products')),
    url(r'^search/', include("search.urls", namespace='search')),
    url(r'^marketing/', include("marketing.urls", namespace='marketing')),
    url(r'^geo/', include("geolocation.urls", namespace='geolocation')),
    url(r'^cart/', include("carts.urls", namespace='carts')),
    url(r'^admin/', admin.site.urls),
    url(r'^lang/(?P<lang>[\w-]+)', ChangeLanguageView.as_view(), name='lang'),
    url(r'^currency/(?P<currency>[\w-]+)', ChangeCurrencyView.as_view(), name='currency'),
]

urlpatterns += [
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}),
    url(r'^robots\.txt$', TemplateView.as_view(template_name="sklep/robots.txt", content_type='text/plain')),
]

js_info_dict = {
    'domain': 'djangojs',
    'packages': ('sklep',),
}

urlpatterns += [
    url(r'^jsi18n/$', javascript_catalog, js_info_dict, name='jscatalog'),
]

urlpatterns += [url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico', permanent=True))]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# # Redirect thrash urls to home page:
# urlpatterns += [
#     url(r'^well-known/assetlinks\.json$', RedirectView.as_view(url='/', permanent=True)),
#     url(r'^\.git/HEAD$', RedirectView.as_view(url='/', permanent=True)),
# ]
