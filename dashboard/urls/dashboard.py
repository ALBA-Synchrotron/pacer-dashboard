from django.urls import path

from dashboard.views.dashboard import DashboardView

urlpatterns: list = [
    path("", DashboardView.as_view(), name="dashboard_home"),

]
