from django.db.models import QuerySet, Q
from django.db.models.sql import Query
from django.views.generic import TemplateView

from dashboard.models import Message, GroupProfile


class MessagesView(TemplateView):
    template_name: str = "msg_results.html"

    def get_context_data(self, **kwargs) -> dict:
        context: dict = super().get_context_data(**kwargs)
        context['messages'] = self.get_queryset()
        return context

    def get_queryset(self) -> QuerySet:
        user_filter: Q = GroupProfile.get_user_filters(self.request.user)
        return Message.objects.filter(user_filter).order_by('id')[:20]
