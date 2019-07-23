from datetime import timedelta

from django.db.models import Q
from django.shortcuts import render, HttpResponse
from django.utils.datetime_safe import datetime
from django.views.generic import DetailView, ListView
from .models import Geolocation, get_geo_by_ip, validate_ipv4
from django.contrib.auth.mixins import LoginRequiredMixin


GOOGLE_CRAWLER_IP_PREFIX = '66.249'

def ip_geo_view(request, ip):
    context = {}
    if validate_ipv4(ip):
        geodata = get_geo_by_ip(ip)
        if geodata:
            for param in geodata:
                context[param] = geodata[param]

    return render(request, 'geolocation/view.html', context)


class GeoListView(LoginRequiredMixin, ListView):
    template_name = 'geolocation/view.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_staff:
            return HttpResponse(' NOT AUTHORIZED ')
        return super(GeoListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        last_month = datetime.today() - timedelta(days=30)
        qs = Geolocation.objects.all().filter(date__gte=last_month).exclude(
            Q(ip__startswith=GOOGLE_CRAWLER_IP_PREFIX) | Q(user__username='admin')
            ).order_by('-date')
        return qs


