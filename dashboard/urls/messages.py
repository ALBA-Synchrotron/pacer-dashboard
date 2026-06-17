from django.urls import path

from dashboard.views.messages import MessagesView, TemplateGetById, MessageAcknowledgeView, \
    MessageReingestionTemplateView, MessageReingestionAPIView, RelatedMessageTemplateView

reference_name: str = "messages"

urlpatterns: list = [
    path("tmpl/messages", MessagesView.as_view(), name=f"{reference_name}_tmpl_list"),
    path("tmpl/messages/<int:msg_id>", TemplateGetById.as_view(), name=f"{reference_name}_tmpl_detail"),
    path("tmpl/messages/<int:msg_id>/ack", MessageAcknowledgeView.as_view(), name=f"{reference_name}_tmpl_ack"),
    path("tmpl/messages/<int:msg_id>/reingest", MessageReingestionTemplateView.as_view(),
         name=f"{reference_name}_tmpl_reingest"),
    path("tmpl/messages/reingest", MessageReingestionAPIView.as_view(), name=f"{reference_name}_api_reingest"),
path("tmpl/messages/<int:msg_id>/related", RelatedMessageTemplateView.as_view(), name=f"{reference_name}_api_related"),
]
