import json

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import QuerySet, Q
from django.http import Http404
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from dashboard.models import Message, GroupProfile
from django.conf import settings

from dashboard.utils.messages import get_user_filters
from dashboard.utils.rabbitmq import GenericPublisher

MAX_MSG_PER_PAGE: int = 10





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


class MessageAcknowledgeView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name: str = "msg_card/msg_card.html"

    def has_permission(self):
        if settings.ADMIN_ROLE_GROUP_NAME in [i.name for i in self.request.user.groups.all()]:
            return True
        return GroupProfile.message_actions_allowed(self.request.user)

    def get_object(self, msg_id: int) -> QuerySet:
        user_filters = Q(id=msg_id)
        return Message.objects.filter(user_filters).first()

    def post(self, request, *args, **kwargs):
        msg_id = self.kwargs.get("msg_id")
        msg = self.get_object(msg_id)

        if msg is None:
            raise Http404("Message not found")

        msg.acknowledged = not msg.acknowledged
        msg.save(update_fields=["acknowledged"])

        self.object = msg
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        context: dict = super().get_context_data(**kwargs)

        msg_id: int = self.kwargs.get("msg_id", None)
        msg: Message | None = self.get_object(msg_id)
        if msg is not None:
            context["msg"] = msg
        return context


class MessageReingestionTemplateView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name: str = "msg_reingestion/msg_reingest_content.html"

    def has_permission(self):
        if settings.ADMIN_ROLE_GROUP_NAME in [i.name for i in self.request.user.groups.all()]:
            return True
        return GroupProfile.message_actions_allowed(self.request.user)

    def __get_available_routing_keys(self, msg: Message) -> list:
        opts = list(
            Message.objects.filter(exchange_name=msg.exchange_name).values_list("routing_key", flat=True).distinct())
        opts.remove(msg.routing_key)
        return opts

    def get_context_data(self, **kwargs) -> dict:
        context: dict = super().get_context_data(**kwargs)

        msg_id: int = self.kwargs.get("msg_id", None)
        msg: Message | None = self.get_object(msg_id)
        if msg is not None:
            context["msg"] = msg
            context["routing_keys"] = self.__get_available_routing_keys(msg)
        return context

    def get_object(self, msg_id: int) -> QuerySet:
        user_filters = Q(id=msg_id)
        return Message.objects.filter(user_filters).first()


class MessageReingestionAPIView(LoginRequiredMixin, PermissionRequiredMixin, GenericAPIView):
    def has_permission(self):
        if settings.ADMIN_ROLE_GROUP_NAME in [i.name for i in self.request.user.groups.all()]:
            return True
        msg_id: int = int(self.request.POST.get("msg-id", 0))
        msg: Message | None = self.get_object(msg_id)

        allowed_reingestions = [
            message_type
            for g in self.request.user.groups.all()
            for message_type in (g.groupprofile.allowed_message_types_reingest or "").split(",")
            if message_type
        ]
        return GroupProfile.message_actions_allowed(self.request.user) and msg.message_type in allowed_reingestions

    def post(self, request, *args, **kwargs):
        msg_id: int = int(request.POST.get("msg-id", 0))
        msg_payload = request.POST.get("msg-payload", "")

        if not msg_payload:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        msg: Message | None = self.get_object(msg_id)

        if not msg:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            match msg.payload_format:
                case "json":
                    msg_payload = json.loads(msg_payload)
                case "xml":
                    msg_payload = msg_payload.strip()

            GenericPublisher.send_messages_to_broker([msg_payload], msg.exchange_name,
                                                     msg.routing_key, dump_json_body=msg.payload_format == "json")
            return Response(status=status.HTTP_200_OK)
        except Exception:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_object(self, msg_id: int) -> QuerySet:
        user_filters = Q(id=msg_id)
        return Message.objects.filter(user_filters).first()


class RelatedMessageTemplateView(TemplateView):
    template_name: str = "msg_related/msg_related_content.html"

    def get_context_data(self, **kwargs) -> dict:
        context: dict = super().get_context_data(**kwargs)

        msg_id: int = self.kwargs.get("msg_id", None)
        msg: Message | None = self.get_object(msg_id)
        if msg is not None:
            context["related_messages"] = msg.get_related_messages()
            context["original_message"] = msg
        return context

    def get_object(self, msg_id: int) -> QuerySet:
        user_filters = Q(id=msg_id)
        return Message.objects.filter(user_filters).first()
