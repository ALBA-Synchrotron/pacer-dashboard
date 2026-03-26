from django.urls import path

from dashboard.views.status import StatusView

urlpatterns: list = [
    path("status", StatusView.as_view(), name="status"),
]
