from django.db.models import QuerySet
from django.views.generic import TemplateView

from dashboard.models import Message


class MessagesView(TemplateView):
    template_name: str = "msg_results.html"

    def get_context_data(self, **kwargs) -> dict:
        context: dict = super().get_context_data(**kwargs)
        context['messages'] = self.get_queryset()
        return context

    def get_queryset(self) -> QuerySet:
        return Message.objects.order_by('-id')[:20]
