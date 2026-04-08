from django.urls import path

from dashboard.views.messages import MessagesView, GetById

reference_name: str = "messages"

urlpatterns: list = [
    path("tmpl/messages", MessagesView.as_view(), name=f"{reference_name}_tmpl_list"),
    path("tmpl/messages/<int:msg_id>", GetById.as_view(), name=f"{reference_name}_tmpl_detail"),
]
