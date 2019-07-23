from django.utils.http import is_safe_url


class NextUrlMixin(object):
    default_next = '/'
    def get_next_url(self):
        request = self.request
        next_get_url = request.GET.get('next_url')
        next_post_url = request.POST.get('next_url')
        redirect_path = (next_post_url or next_get_url) or None

        if is_safe_url(redirect_path, request.get_host()):
            return redirect_path
        else:
            return self.default_next
