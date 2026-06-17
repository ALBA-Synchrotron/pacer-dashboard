from django.urls import path

from dashboard.views.statistics import StatisticsView, StatisticsTemplateView

urlpatterns: list = [
    path("stats", StatisticsView.as_view(), name="statistics"),
    path("tmpl/stats", StatisticsTemplateView.as_view(), name="statistics_templ"),

]
