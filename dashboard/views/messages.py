from django.core.paginator import Paginator
from django.db.models import QuerySet, Q
from django.views.generic import TemplateView

from dashboard.models import Message, GroupProfile

MAX_MSG_PER_PAGE: int = 10


def get_user_filters(request) -> Q:
    user_filter: Q = GroupProfile.get_user_filters(request.user)
    message_type_filters: list = request.GET.getlist("msg-filters")
    text_search: str = request.GET.get("general-search", "").strip()
    errored_only: bool = request.GET.get("errored-only", "off") == "on"
    payload_types: list = request.GET.getlist("payload-type")

    if message_type_filters:
        user_filter &= Q(message_type__in=message_type_filters)
    if text_search:
        user_filter &= Q(object_identifiers__icontains=text_search) | Q(hash__icontains=text_search)
    if errored_only:
        user_filter &= Q(errored=True)
    if payload_types:
        user_filter &= Q(payload_format__in=(i.lower() for i in payload_types))
    return user_filter


class MessagesView(TemplateView):
    template_name: str = "msg_results.html"

    def get_context_data(self, **kwargs) -> dict:
        context: dict = super().get_context_data(**kwargs)
        page_number: int = int(self.request.GET.get("page", 1))

        msgs_queryset: QuerySet = self.get_queryset()
        messages = Paginator(msgs_queryset.order_by("-id"), MAX_MSG_PER_PAGE)
        context["current_page"] = page_number
        context["msg_page_obj"] = messages.get_page(page_number)
        context["total_msgs"] = msgs_queryset.count()
        context["current_msgs"] = min(MAX_MSG_PER_PAGE * page_number, msgs_queryset.count())
        return context

    def get_queryset(self) -> QuerySet:
        user_filters: Q = get_user_filters(self.request)
        return Message.objects.filter(user_filters)


class TemplateGetById(TemplateView):
    template_name: str = "new_message.html"

    def get_context_data(self, **kwargs) -> dict:
        context: dict = super().get_context_data(**kwargs)

        msg_id: int = self.kwargs.get("msg_id", None)
        current_page: int = int(self.request.GET.get("current-page", 1))
        total_msgs: int = int(self.request.GET.get("total-msgs", 0))

        context["current_msgs"] = min(MAX_MSG_PER_PAGE * current_page, total_msgs)
        context["total_msgs"] = total_msgs

        msg: Message | None = self.get_object(msg_id)
        if msg is not None:
            context["msg"] = msg
            context["current_msgs"] += 1
            context["total_msgs"] += 1
        return context

    def get_object(self, msg_id: int) -> QuerySet:
        user_filters: Q = get_user_filters(self.request)
        user_filters &= Q(id=msg_id)

        return Message.objects.filter(user_filters).first()
