from django.urls import path, include

from dashboard.views.status import StatusView

urlpatterns: list = [
    path("", include("dashboard.urls.dashboard")),
    path("", include("dashboard.urls.messages")),
    path("", include("dashboard.urls.statistics")),
    path("status", StatusView.as_view(), name="status"),

]
