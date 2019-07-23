from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import DetailView, FormView, UpdateView
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from sklep.log import loger
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from .forms import LoginForm, RegisterForm, GuestForm, UserDataUpdateForm
from .models import GuestEmail
from orders.models import Order
from marketing.models import MarketingPref
from addresses.models import Address
from mixins import NextUrlMixin
from analytics.models import ObjectViewed

User = get_user_model()


class SettingsPageView(LoginRequiredMixin, DetailView, UpdateView):
    template_name = "accounts/settings.html"
    redirect_field_name = "next_url"
    form_class = UserDataUpdateForm
    success_url = '#'

    def get_object(self, queryset=None):
        """User object for account settings change tab"""
        qs = User.objects.get(username=self.request.user.username)
        return qs

    def get_context_data(self, *args, **kwargs):
        """Context data for Bills/Recently viewed products tabs"""
        request = self.request
        user = request.user
        context = super(SettingsPageView, self).get_context_data(*args, **kwargs)

        user_orders = Order.objects.user_orders_history(user)
        addresses_qs = Address.objects.filter(billing_profile__email=user.email, current=True)
        billing_addresses = addresses_qs.filter(address_type="billing")
        shipping_addresses = addresses_qs.filter(address_type="shipping")
        unique_viewed_products = ObjectViewed.objects.viewed_products_for_user(user)

        context['orders'] = user_orders
        context['billing_addresses'] = billing_addresses
        context['shipping_addresses'] = shipping_addresses
        context['viewed_products'] = unique_viewed_products

        return context

    def post(self, request, *args, **kwargs):
        """ POST action handler for making 'unused' address stale in addresses tab"""
        if request.POST.get('del_address'):
            address_id = request.POST.get('address_id')
            if not address_id:
                loger.error(f'No address to delete specified in POST request: {request.POST}')
            else:
                qs = Address.objects.filter(id=address_id)
                if qs:
                    address_to_del = qs.first()
                    address_to_del.make_stale()
            return redirect('accounts:settings')

        return super(SettingsPageView, self).post(request, *args, **kwargs)


class GuestRegisterView(NextUrlMixin, FormView):
    form_class = GuestForm
    template_name = "accounts/auth.html"

    def get_context_data(self, **kwargs):
        context = super(GuestRegisterView, self).get_context_data(**kwargs)
        context['title'] =  _("Kontynuuj jako gość")
        context['button'] = _("Dalej")
        return context

    def form_invalid(self, form):
        request = self.request
        messages.warning(request, _('Formularz został wypełniony niepoprawnie!'))
        return super(GuestRegisterView, self).form_invalid(form)

    def form_valid(self, form):
        request = self.request

        email = form.cleaned_data.get("email")
        new_guest_email = GuestEmail.objects.create(email=email)
        request.session['guest_email_id'] = new_guest_email.id
        loger.info(f'New guest user was created: {new_guest_email} with id {new_guest_email.id}')
        messages.success(request,  _('Utworzono konto gościa z adresem e-mail ') + str(new_guest_email))

        # Subscribe to newsletter
        newsletter_sub = form.cleaned_data.get('subscribe')
        if newsletter_sub:
            newsletter_subscribe(request, form, guest_email=new_guest_email.email)

        next_path = self.get_next_url()
        return redirect(next_path)


class LoginView(NextUrlMixin, FormView):
    form_class = LoginForm
    template_name = "accounts/auth.html"

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context['title'] = _("Zaloguj się na konto")
        context['button'] = _("Zaloguj")
        context['login'] = "True"
        return context

    def form_invalid(self, form):
        request = self.request
        messages.warning(request, _('Formularz został wypełniony niepoprawnie!'))
        return super(LoginView, self).form_invalid(form)

    def form_valid(self, form):
        request = self.request
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user_auth = authenticate(request, username=username, password=password)
        user_obj = User.objects.get(username=username)

        if user_obj.is_active == True:

            if user_auth is not None:
                login(request, user_auth)
                messages.success(request, _('Pomyślnie zalogowano użytkownika ') + str(username))
                loger.info(f'User {str(username)} was logged in')
                request.session['username'] = username

                if request.session.get('guest_email_id'):
                    del request.session['guest_email_id']

                next_path = self.get_next_url()
                return redirect(next_path)

            else:
                messages.warning(request, _('Niepoprawne hasło!'))
                return self.form_invalid(form)

        else:
            messages.warning(
                request,
                _('Konto nieaktywne, czy dokonałeś aktywacji? Sprawdź instrukcję wysłaną na adres e-mail:') + str(user_obj.email)
            )

            loger.info(f'User tries to log on inactive account {user_obj.username} {user_obj.email}')

            reactivate_url = f'/accounts/reactivate/{user_obj.username}/{user_obj.email}/'

            reactivate_msg_text = _("Kliknij w ") + f"<a href='{reactivate_url}'>LINK</a>" + _(" aby ponownie przesłać link aktywacyjny.")

            messages.warning(request, mark_safe(reactivate_msg_text))

            return self.form_invalid(form)


def logout_page(request):
    if request.session.get('guest_email_id'):
        loger.info(f'Logged out guest user {request.session.get("guest_email_id")}')
        del request.session['guest_email_id']
        messages.success(request, _('Zakończono sesję gościa'))
    else:
        loger.info(f'Logged out user {request.user}')
        logout(request)
        messages.success(request, _('Pomyślnie wylogowano użytkownika'))

    if request.session.get('cart_id'):
        del request.session['cart_id']
    if request.session.get('cart_items_count'):
        del request.session['cart_items_count']

    return redirect('/')


class RegisterView(NextUrlMixin, FormView):
    form_class = RegisterForm
    template_name = "accounts/auth.html"
    default_next = 'accounts:login'

    def get_context_data(self, **kwargs):
        context = super(RegisterView, self).get_context_data(**kwargs)
        context['title'] = _("Utwórz nowe konto")
        context['button'] = _("Zarejestruj")
        return context

    def form_invalid(self, form):
        request = self.request
        messages.warning(request, _('Formularz został wypełniony niepoprawnie!'))
        return super(RegisterView, self).form_invalid(form)

    def form_valid(self, form):
        request = self.request
        user = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        new_user = User.objects.create_user(user, email, password)
        new_user.is_active = False
        new_user.save()

        loger.info(f'Created new user account: {new_user.username} with id: {new_user.id}')
        create_user_msg_text = _("Utworzono konto dla użytkownika ") + str(user) + _(", aktywuj swoje konto postępując zgodnie z instrukcjami wysłanymi na adres e-mail ") + str(email)

        messages.info(request, create_user_msg_text)

        # Subscribe to newsletter
        newsletter_sub = form.cleaned_data.get('subscribe')
        if newsletter_sub:
            newsletter_subscribe(request, form, new_user=new_user)

        # Send activation mail
        send_activation_mail(request, user, email)

        next_path = self.get_next_url()
        return redirect(next_path)


def newsletter_subscribe(request, form, new_user=None, guest_email=None):
    if guest_email:
        MarketingPref.objects.get_or_create(user=None, guest_user_email=guest_email)

    elif new_user:
        MarketingPref.objects.get_or_create(user=new_user)

    messages.success(request, _('Zostałeś dodany do naszego Newslettera!'))
    loger.info(f'User {new_user} with email {guest_email} was added to newsletter')


def send_activation_mail(request, user, email):
    new_user = User.objects.get(username=user)

    mail_subject = _("Aktywuj swoje konto w naklisze.pl")
    current_site = get_current_site(request)
    message = render_to_string('accounts/acc_active_email.html', {
        'user': new_user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
        'token': account_activation_token.make_token(new_user),
    })
    email_msg = EmailMessage(
        mail_subject, message, to=[email]
    )
    try:
        email_msg.send()
        loger.info(f'Account activation email was send to {email}')
    except:
        messages.warning(request, _('Nastąpił błąd przy wysyłaniu wiadomości aktywacyjnej'))
        loger.exception(f'Error while sending account activation email to {email}')

    return redirect("accounts:login")


def activation_view(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user_obj = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user_obj = None

    if user_obj and account_activation_token.check_token(user_obj, token):
        user_obj.is_active = True
        user_obj.save()

        success_msg_text = _("Aktywowano konto użytkownika ") + str(user_obj.username) + _(", możesz się już zalogować")
        messages.success(request, success_msg_text)
        loger.info(f'User {str(user_obj.username)} account was activated')
        return redirect('accounts:login')

    else:
        messages.warning(request, _('Niepoprawny link aktywacji konta!'))
        loger.warning(f'Wrong account activation link for User ID {uid}')
        return redirect('accounts:register')
