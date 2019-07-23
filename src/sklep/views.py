from django.shortcuts import render
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.views.generic import FormView
from django.shortcuts import redirect
from django.views.generic import RedirectView
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.conf import settings
from django.shortcuts import HttpResponseRedirect
from django.utils.translation import ugettext as _

from random import shuffle

from .forms import ContactForm
from infobox.models import Infobox
from carts.models import Cart
from products.models import Product, Camera
from marketing.models import MarketingPref

from sklep.log import loger


def regulations_page(request):
    context = {
    }
    return render(request, 'regulations.html', context)


def home_page(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    promo_products = Product.objects.all_promo().order_by('?')

    featured_products = Product.make_qs_unique(Product.objects.featured())
    shuffle(featured_products)

    new_products = Camera.objects.latest()
    infobox = Infobox.objects.all().filter(active=True)

    newsletter_visible = True


    if request.user.is_authenticated:
        qs = MarketingPref.objects.filter(user=request.user)
        if qs:
            marketing_obj = qs.first()
            if marketing_obj.subscribed:
                newsletter_visible = False
                loger.debug(f'Newsletter jumbotron is hidden for {request.user}')

    context = {
        'cart': cart_obj,
        'promo_products': promo_products,
        'featured_products': featured_products,
        'new_products': new_products,
        'newsletter_visible': newsletter_visible,
        'infobox' : infobox,
    }

    if request.user.is_authenticated():
        context['username'] = request.user.username

    return render(request, 'home_page.html', context)


class AboutPageView(FormView):
    template_name = 'about.html'
    form_class = ContactForm

    def form_valid(self, form):
        request = self.request
        fullname = form.cleaned_data['fullname']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']
        subject = "Wiadomość od {}".format(fullname)

        try:
            send_mail(subject, message, email, ['naklisze@gmail.com'])
            messages.success(request, _('Pomyślnie wysłano wiadomość'))
            loger.info(f'Successfuly sent email from {email} using /contacts form')
            form = ContactForm(None)

        except BadHeaderError:
            messages.warning(request, _('Nastąpił błąd przy wysyłaniu wiadomości'))
            loger.exception(f'Error while sending mail from /contacts')

        return redirect('about')

    def form_invalid(self, form):
        request = self.request
        messages.warning(request, _('Formularz został wypełniony niepoprawnie!'))
        return redirect('about')


def cookies_policy(request):
    context = {
    }
    return render(request, 'base/cookies_policy.html', context)


class ChangeLanguageView(RedirectView):
    def get(self, request, *args, **kwargs):
        lang = self.kwargs.get('lang')
        if lang:
            if any(lang in l for l in settings.LANGUAGES):
                request.session[LANGUAGE_SESSION_KEY] = lang
                loger.info(f'User {request.user} changed language to: {lang}')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

