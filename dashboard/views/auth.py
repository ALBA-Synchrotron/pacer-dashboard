from urllib import parse

from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse


def logout_redirect_to_sso(request):
    redirect_url: str = f"{request.scheme}://{request.get_host()}{settings.LOGOUT_REDIRECT_URL}"
    if request.user and request.user.is_authenticated:
        logout(request)
    return redirect(settings.SSO_LOGOUT_REDIRECT_URL.format(redirect_url))


def login_redirect_to_sso(request):
    login = reverse("social:begin", kwargs={"backend": "oidc"})
    next_page = request.GET.get("next", settings.LOGIN_REDIRECT_URL)
    url_params = {
        "process": "login",
        "next": next_page
    }
    suffix = parse.urlencode(url_params)
    return redirect(f"{login}?{suffix}")
