from django.core.paginator import Paginator
from django.db.models import QuerySet, Q
from django.views.generic import TemplateView

from dashboard.models import Message, GroupProfile

def get_user_filters(request) -> Q:

    user_filter: Q = GroupProfile.get_user_filters(request.user)
    message_type_filters: list = request.GET.getlist("msg-filters")
    text_search: str = request.GET.get("general-search", "")
    errored_only: bool = request.GET.get("errored-only", "off") == "on"
    payload_types: list = request.GET.getlist("payload-type")

    if message_type_filters:
        user_filter &= Q(message_type__in=message_type_filters)
    if text_search:
        user_filter &= Q(object_identifiers__icontains=text_search)
    if errored_only:
        user_filter &= Q(errored=True)
    if payload_types:
        user_filter &= Q(payload_format__in=(i.lower() for i in payload_types))
    return user_filter


class MessagesView(TemplateView):
    template_name: str = "msg_results.html"
    max_msg_page: int = 20

    def get_context_data(self, **kwargs) -> dict:
        context: dict = super().get_context_data(**kwargs)
        page_number: int = int(self.request.GET.get("page", 1))

        msgs_queryset: QuerySet = self.get_queryset()
        messages = Paginator(msgs_queryset.order_by("-id"), self.max_msg_page)
        context["msg_page_obj"] = messages.get_page(page_number)
        return context

    def get_queryset(self) -> QuerySet:
        user_filters: Q = get_user_filters(self.request)
        return Message.objects.filter(user_filters)


class TemplateGetById(TemplateView):
    template_name: str = "new_message.html"

    def get_context_data(self, **kwargs) -> dict:
        context: dict = super().get_context_data(**kwargs)
        msg_id: int = self.kwargs.get("msg_id", None)
        msg: Message | None = self.get_object(msg_id)
        if msg is not None:
            context["msg"] = msg
        return context

    def get_object(self, msg_id: int) -> QuerySet:
        user_filters: Q = get_user_filters(self.request)
        user_filters &= Q(id=msg_id)

        return Message.objects.filter(user_filters).first()

