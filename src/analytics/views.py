from django.contrib.auth.decorators import user_passes_test
from django.views.generic import TemplateView, DetailView
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.conf import settings

from orders.models import Order
from analytics.objects import AccountsInfo, UserHistoryData
from analytics.models import SearchQueries

from easy_pdf.views import PDFTemplateView, PDFTemplateResponseMixin

from sklep.log import loger


class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/view.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_staff:
            loger.warning(f'{user} wanted to access admin panel!')
            return HttpResponse(' ( . )( . ) ')
        return super(AnalyticsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(AnalyticsView, self).get_context_data(*args, **kwargs)
        orders_qs = Order.objects.all_confirmed()
        incomes = {
            'PLN': [],
            'USD': [],
            'EUR': []
        }
        for order in orders_qs:
            incomes[order.currency].append(order.total)

        for currency, totals in incomes.items():
            incomes[currency] = sum(totals)

        accounts_info = AccountsInfo()
        users_list = accounts_info.all_users
        active_sessions = accounts_info.active_sessions
        active_users = accounts_info.active_users

        search_queries = SearchQueries.objects.clients_queries()

        context['orders'] = orders_qs
        context['incomes'] = incomes
        context['users_list'] = users_list
        context['no_active_sessions'] = len(active_sessions)
        context['active_users'] = active_users
        context['search_queries'] = search_queries

        return context


class GeneratePdfUserDataView(PDFTemplateView):
    template_name = 'analytics/pdf_user_data.html'

    def get(self, request, *args, **kwargs):
        """
        Handles GET request and returns HTTP response.
        """
        user_email = request.user.email
        context = self.get_context_data(user_email, **kwargs)

        return self.render_to_response(context)


    def post(self, request, *args, **kwargs):
        """
        Handles POST request and returns HTTP response.
        """
        user_email = request.POST.get('user_email')
        context = self.get_context_data(user_email, **kwargs)

        return self.render_to_response(context)

    def get_context_data(self, user_email, **kwargs):

        if 'view' not in kwargs:
            kwargs['view'] = self
        context = kwargs

        context['ENV'] = settings.CURRENT_SETTINGS
        context['request'] = self.request

        user_qs = User.objects.filter(email=user_email)
        if user_qs:
            user = UserHistoryData(user_qs.first())

            self.pdf_filename = user.pdf_filename
            context['user'] = user

        return context


from django.views.static import serve
import os


@user_passes_test(lambda u: u.is_superuser)
def sklep_log_view(request):
    filepath = '/var/log/sklep.log'
    return serve(request, os.path.basename(filepath), os.path.dirname(filepath))


@user_passes_test(lambda u: u.is_superuser)
def sklep_django_log_view(request):
    filepath = '/var/log/sklep_django.log'
    return serve(request, os.path.basename(filepath), os.path.dirname(filepath))
