from django.shortcuts import render

# Create your views here.
from sklep.log import loger


def wix_page(request):
    context = {
    }
    loger.info(f'Redirecting to wix subdomain')
    return render(request, 'wix/wix.html', context)
