from django.urls import path

from dashboard.views.messages import MessagesView

reference_name: str = "messages"

urlpatterns: list = [
    path("tmpl/messages", MessagesView.as_view(), name=f"{reference_name}_tmpl_list"),

]
