from django.core.paginator import Paginator
from django.db.models import QuerySet, Q
from django.views.generic import TemplateView

from dashboard.models import Message, GroupProfile


class MessagesView(TemplateView):
    template_name: str = "msg_results.html"
    max_msg_page: int = 20

    def get_context_data(self, **kwargs) -> dict:
        active_filters: list = self.request.GET.getlist("msg-filters")
        text_search: str = self.request.GET.get("general-search", "")

        context: dict = super().get_context_data(**kwargs)
        page_number: int = int(self.request.GET.get("page", 1))
        msgs_queryset: QuerySet = self.get_queryset(msg_type_filters=active_filters, search=text_search)
        messages = Paginator(msgs_queryset.order_by("-id"), self.max_msg_page)
        context["msg_page_obj"] = messages.get_page(page_number)
        return context



    def get_queryset(self, msg_type_filters: list = [], search: str = "") -> QuerySet:
        user_filter: Q = GroupProfile.get_user_filters(self.request.user)
        ret = Message.objects.filter(user_filter)
        if msg_type_filters:
            ret = ret.filter(message_type__in=msg_type_filters)
        if search:
            ret = ret.filter(object_identifiers__icontains=search)
        return ret

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
