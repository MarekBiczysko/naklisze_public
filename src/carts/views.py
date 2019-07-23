import os

from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.db.models import Q
from django.db import transaction
from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext as _

from sklep.log import loger
from .models import Cart
from products.models import Product
from orders.models import Order
from accounts.forms import LoginForm, GuestForm
from billing.models import BillingProfile
from addresses.forms import AddressForm
from addresses.models import Address
from sklep.utils import send_mail

import logging
log = logging.getLogger(__name__)


def cart_home(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    products = cart_obj.products.all()

    context = {
        'total_price': cart_obj.total,
        'basket_products': products,
        'cart': cart_obj,
    }

    return render(request, "carts/home.html", context)

@transaction.atomic()
def cart_update(request):
    product_id = request.POST.get('product')
    add_another_multiple = request.POST.get('add_another_multiple')

    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)

        except Product.DoesNotExist:

            messages.warning(request, _('Wystąpił błąd, produkt nie istnieje w bazie'))
            loger.error(f'Product {product_id} was not added to cart because it not exist in DB')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        cart_obj, new_obj = Cart.objects.new_or_get(request)

        # try add to cart another instance of same type multiple product
        if add_another_multiple:
            qs = get_another_multiple_product(product_obj, cart_obj)

            # if there is available another product -> add to cart
            if qs:
                new_product = qs[0]
                cart_obj.products.add(new_product)
                cart_obj.recalculate_values()
            else:
                loger.warning(f'Failed to add another multiple product {product_obj} to cart, no more products of this kind')
                messages.warning(request, _('Brak dostępnych kolejnych produktów tego typu'))

        else:
            if product_obj in cart_obj.products.all():
                cart_obj.products.remove(product_obj)
                loger.info(f'Removed product {product_obj} from cart {cart_obj}')
            else:
                cart_obj.products.add(product_obj)  # cart_obj.products.add(product_id)
                loger.info(f'Added product {product_obj} to cart {cart_obj}')
                messages.success(request, _('Produkt został dodany do koszyka'))

        request.session['cart_items_count'] = cart_obj.products.count()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def checkout_home(request):

    cart_obj, cart_created = Cart.objects.new_or_get(request) # create or get cart
    products = cart_obj.products.all()

    order_obj = None
    address_qs = None

    login_form = LoginForm()
    guest_form = GuestForm()
    address_form = AddressForm()

    billing_address_id = request.session.get("billing_address_id", None)
    shipping_address_id = request.session.get("shipping_address_id", None)

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)

    if request.session.get('success_order_id'):
        del request.session['success_order_id']

    if cart_created or cart_obj.products.count() == 0: # new empty cart or no products in cart so no checkout
        loger.info(f'cart_created={cart_created} or products_count={cart_obj.products.count()} so redirecting to carts:home ')
        return redirect("carts:home")

    if billing_profile is not None: # Billing profile is available so we can create or update order

        # make_checkout flag is received via GET trough check_availability
        make_checkout = request.GET.get('make_checkout')

        del_shipping_address = request.POST.get('del_shipping_address')
        del_billing_address = request.POST.get('del_billing_address')
        newShippingType = request.POST.get('shippingType')

        address_qs = Address.objects.filter(billing_profile=billing_profile, current=True)

        with transaction.atomic():

            order_obj, order_obj_created = Order.objects.new_or_get(
                cart_obj=cart_obj, billing_profile=billing_profile, select_for_update=True
            )

            if shipping_address_id:
                order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
                order_obj.save()
                del request.session["shipping_address_id"]
                loger.info(f'Added shipping address {shipping_address_id} to order {order_obj}')

            if billing_address_id:
                order_obj.billing_address = Address.objects.get(id=billing_address_id)
                order_obj.save()
                del request.session["billing_address_id"]
                loger.info(f'Added billing address {billing_address_id} to order {order_obj}')

            if newShippingType:
                order_obj.update_all(new_shipping_type=newShippingType)
                loger.info(f'Updated order {order_obj} with new shipping type {newShippingType}')

            if make_checkout:
                loger.info(f'Starting checkout for order {order_obj}')
                order_is_done = order_obj.check_if_done()
                if order_is_done:
                    order_obj.mark_as_done()
                    order_obj.add_comment(request.session.get('order_comment', ''))
                    request.session['success_order_id'] = order_obj.order_id
                    loger.info(f'Order {order_obj} is done, redirecting to carts:checkout_success')
                    return redirect("carts:checkout_success")

            # delete current address from order and go back to choose another one
            if del_shipping_address or del_billing_address:
                if del_shipping_address:
                    order_obj.shipping_address = None
                    order_obj.save()
                    loger.info(f'Deleted shipping address from order {order_obj}')
                elif del_billing_address:
                    order_obj.billing_address = None
                    order_obj.save()
                    loger.info(f'Deleted billing address from order {order_obj}')

                return redirect("carts:checkout")

    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form,
        "address_form": address_form,
        "basket_products": products,
        "address_qs": address_qs,
    }

    return render(request, "carts/checkout.html", context)

def checkout_success(request):

    success_order_id = request.session.get('success_order_id')

    if not success_order_id:
        loger.warning(f'success_order_id not found in checkout_success view, redirecting to home page')
        return redirect("home_page")

    with transaction.atomic():

        order_obj = Order.objects.select_for_update().get(order_id=success_order_id)
        order_obj.update_date()
        success_user_email = order_obj.billing_profile.email
        success_order_total = order_obj.total
        context = {
            'success_order_id': success_order_id,
            'success_user_email': success_user_email,
            'success_order_total': success_order_total
        }


        bought_products = order_obj.cart.products.all().select_for_update()
        for product in bought_products:
            product.make_selled()
            loger.info(f'All products in order {order_obj} were marked as bought')

    if request.session.get('cart_id'):
        del request.session['cart_id']
    if request.session.get('cart_items_count'):
        del request.session['cart_items_count']
    if request.session.get('guest_email_id'):
        del request.session['guest_email_id']

    # Send order success mail
    send_order_success_mail(request, success_order_id, success_user_email, str(success_order_total), bought_products,
                            order_obj)

    if request.session.get('success_order_id'):
        del request.session['success_order_id']
    if request.session.get('order_comment'):
        del request.session['order_comment']

    return render(request, "carts/checkout_success.html", context)


def get_another_multiple_product(product, cart_obj):
    # if possible return qs of available instances of same model of 'multiple type' product

    product_category = product.category
    product_model = product.model  # model is unique type field

    # constructing Q query :)
    queryClass = product.__class__.__name__
    queryField = 'model'
    queryFilter = queryClass + '___' + queryField

    # unpacking dict to kwargs hack
    qs = Product.objects.all_available().filter(category=product_category).filter(
        Q(**{queryFilter: product_model}))

    # filter out products which are already in cart
    qs = [prod for prod in qs if not prod in cart_obj.products.all()]

    return qs

@transaction.atomic()
def check_availability(request):
    next_get_url = request.GET.get('next_url')
    next_post_url = request.POST.get('next_url')
    make_checkout = request.POST.get('make_checkout')
    order_comment = request.POST.get('comment')

    redirect_path = (next_post_url or next_get_url) or None

    cart_obj, cart_created = Cart.objects.new_or_get(request, select_for_update=True)  # create or get cart
    cart_obj.recalculate_values()
    products = cart_obj.products.all().select_for_update()
    all_available = True

    loger.info(f'Checking availability of products in cart {cart_obj}')

    for product in products:
        if product.selled == True:
            loger.info(f'Product {product} is unavailable')

            # try replace 'multiple' product with available one
            if product.category in product.MULTIPLE_PRODUCTS_CATEGORIES:
                loger.info(f'Product {product} is multiple product, trying to get another available')

                available_prod_list = get_another_multiple_product(product, cart_obj)

                # if there is available another product -> replace
                if available_prod_list:
                    loger.info(f'Another multiple products type {product} are available')
                    cart_obj.products.remove(product)
                    new_product = available_prod_list[0]
                    cart_obj.products.add(new_product)
                    loger.info(f'Switched {product} to {new_product}')
                    continue

            # remove not available product from cart
            all_available = False
            cart_obj.products.remove(product)
            request.session['cart_items_count'] = cart_obj.products.count()

            deleted_product_msg_text = _("Produkt ") + str(product) + _(" został usunięty z karty")

            messages.warning(request, deleted_product_msg_text)
            loger.info(f'Removed unavailable product from cart: {product}')

    if all_available is True:
        loger.info(f'All products in cart {cart_obj} are available')
        if make_checkout:
            loger.info(f'Redirecting to checkout view with make_checkout flag')
            redirect_path += "?make_checkout=True"
        if order_comment:
            request.session['order_comment'] = order_comment

        return redirect(redirect_path)

    else:
        messages.warning(request, _("Ktoś Cię ubiegł, jeden z wybranych przez Ciebie produktów jest już niedostępny :("))
        loger.info(f'Some products from cart {cart_obj} were unavailable, redirecting to carts:home ')
        return redirect("carts:home")


def send_order_success_mail(request, success_order_id, success_user_email, success_order_total, bought_products, order_obj):
    mail_subject = "naklisze.pl - " + _("Potwierdzenie zamówienia nr ") + str(success_order_id)

    message = render_to_string(
        'carts/checkout_success_email.html',
        {
            'success_order_id': success_order_id,
            'success_user_email': success_user_email,
            'success_order_total': success_order_total,
            'bought_products': bought_products,
            'order': order_obj,
            'settings_url': request.build_absolute_uri(reverse('accounts:settings')),
            'register_url': request.build_absolute_uri(reverse('accounts:register'))
        },
        request=request
    )

    return_file_path = os.path.join(settings.STATIC_ROOT, 'formularz_reklamacji.pdf')
    regulations_file_path = os.path.join(settings.STATIC_ROOT, 'Regulamin.pdf')
    attachments = [return_file_path, regulations_file_path]

    recipient_list = [success_user_email, "naklisze@gmail.com"]

    send_mail(mail_subject, message, recipient_list, attachments)
    loger.info(f'Success order {success_order_id} email was scheduled to send to {recipient_list}')
