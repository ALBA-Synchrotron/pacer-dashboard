from django.core.paginator import Paginator
from django.db.models import QuerySet, Q
from django.views.generic import TemplateView

from dashboard.models import Message, GroupProfile


class MessagesView(TemplateView):
    template_name: str = "msg_results.html"

    def get_context_data(self, **kwargs) -> dict:
        context: dict = super().get_context_data(**kwargs)
        page_number: int = self.request.GET.get("page", 1)
        msgs_queryset: QuerySet = self.get_queryset()
        messages = Paginator(msgs_queryset.order_by("-id"), 20)
        context["msg_page_obj"] = messages.get_page(page_number)
        context["msg_types"] = msgs_queryset.values_list("message_type", flat=True).distinct()
        return context



    def get_queryset(self) -> QuerySet:
        user_filter: Q = GroupProfile.get_user_filters(self.request.user)
        return Message.objects.filter(user_filter)

class TemplateGetById(TemplateView):
    template_name: str = "new_message.html"

    def get_context_data(self, **kwargs) -> dict:
        context: dict = super().get_context_data(**kwargs)

        msg: Message | None = self.get_object()
        if msg is not None:
            context["msg"] = msg
        return context

    def get_object(self) -> Message | None:
        msg_id: int = self.kwargs.get("msg_id", None)
        user_filter: Q = GroupProfile.get_user_filters(self.request.user)
        try:
            return Message.objects.get(Q(pk=msg_id) & user_filter)
        except Message.DoesNotExist:
            return None
