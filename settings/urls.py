"""
URL configuration for settings project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path

from dashboard.views.auth import logout_redirect_to_sso, login_redirect_to_sso

urlpatterns: list = [
    path("", include("social_django.urls", namespace="social")),
    path("admin/login/", login_redirect_to_sso, name="admin_sso_login"),
    path("admin/logout/", logout_redirect_to_sso, name="admin_sso_logout"),
    path("oidc-logout", logout_redirect_to_sso, name="oidc-logout"),
    path("", include("dashboard.urls.generic")),
    path("admin/", admin.site.urls),
]
