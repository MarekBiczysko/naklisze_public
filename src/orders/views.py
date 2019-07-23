from django.contrib.auth.models import User
from orders.models import Order
from easy_pdf.views import PDFTemplateView, PDFTemplateResponseMixin
from django.conf import settings


# Create your views here.
class GeneratePdfOrderView(PDFTemplateView):
    template_name = 'orders/pdf_order_data.html'

    def get_context_data(self, **kwargs):

        if 'view' not in kwargs:
            kwargs['view'] = self
        context = kwargs

        context['ENV'] = settings.CURRENT_SETTINGS
        context['request'] = self.request

        order_id = self.kwargs.get('order_id')
        order_qs = Order.objects.filter(id=order_id)
        if order_qs:
            order_obj = order_qs.first()

            self.pdf_filename = f"order_{order_id}"
            context['order'] = order_obj

        return context
