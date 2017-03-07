import re

from django.conf import settings
from django.shortcuts import redirect


EXEMPT_URLS = [re.compile(settings.WELCOME_URL.lstrip('/'))]
if hasattr(settings, 'AUTHORIZATION_EXEMPT_URLS'):
    EXEMPT_URLS += [re.compile(url) for url in settings.AUTHORIZATION_EXEMPT_URLS]


class AuthorizationRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        assert hasattr(request, 'user')

        path = request.path_info.lstrip('/')
        # print(path)

        url_is_exempt = any(url.match(path) for url in EXEMPT_URLS)

        if False and url_is_exempt:
            return redirect(settings.WELCOME_REDIRECT_URL)
        elif False or url_is_exempt:
            return None
        else:
            return redirect(settings.WELCOME_URL)
