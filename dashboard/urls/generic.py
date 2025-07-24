from django.urls import path

from dashboard.views.status import StatusView

urlpatterns: list = [
    path("", StatusView.as_view(), name="status"),
]
