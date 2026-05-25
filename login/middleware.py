from django.shortcuts import redirect
from django.conf import settings


# Prefijos de URL que no requieren autenticación
PUBLIC_PREFIXES = (
    '/login/',
    '/admin/',
    '/__debug__/',
)


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        is_public = any(request.path.startswith(prefix) for prefix in PUBLIC_PREFIXES)

        if not is_public and not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        is_login_page = request.path.rstrip('/') in ('/login', '/login/') or request.path in ('/login/', '/login/login')
        if is_login_page and request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)

        return self.get_response(request)
