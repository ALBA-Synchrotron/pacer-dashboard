import json
import re
from collections import Counter

from django.db.models import QuerySet, Q, Count
from django.views.generic import TemplateView

from dashboard.models import GroupProfile, Message
from dashboard.utils.messages import get_user_filters


def normalize_error_message(error_message: str) -> str:
    try:
        parsed_error = json.loads(error_message)
        if isinstance(parsed_error, dict):
            error_message = " | ".join(str(value) for value in parsed_error.values())
    except json.JSONDecodeError:
        pass

    error_message = re.sub(r"\b\d{5,}\b", "<number>", error_message)
    error_message = re.sub(r"\b[0-9a-f]{8,}\b", "<hex>", error_message, flags=re.IGNORECASE)
    error_message = re.sub(r"\b[A-Z]{1,10}-\d+\b", "<identifier>", error_message)

    return error_message.strip()

class StatisticsView(TemplateView):
    template_name: str = "stats/statistics.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super(StatisticsView, self).get_context_data(**kwargs)
        context["message_types"] = GroupProfile.get_allowed_message_types(self.request.user)

        return context


class StatisticsTemplateView(TemplateView):
    template_name: str = "stats/stats_content.html"

    def get_queryset(self) -> QuerySet:
        user_filters: Q = get_user_filters(self.request)
        return Message.objects.filter(user_filters)

    def get_queryset_unrestricted(self) -> QuerySet:
        return Message.objects.filter()

    def get_context_data(self, **kwargs) -> dict:
        context = super(StatisticsTemplateView, self).get_context_data(**kwargs)
        objects = self.get_queryset()
        all_objects = self.get_queryset_unrestricted()

        context["total_messages_general"] = {
            "title": "Messages",
            "subtitle": "Total messages processed",
            "icon": "fa-solid fa-envelope",
            "value": objects.count(),
            "text_class": "text-primary"
        }

        context["total_errors_general"] = {
            "title": "Errors",
            "subtitle": "Total errors captured",
            "icon": "fa-solid fa-triangle-exclamation",
            "value": objects.filter(errored=True).count(),
            "text_class": "text-warning"
        }

        context["total_users_general"] = {
            "title": "Users",
            "subtitle": "Total users synced",
            "icon": "fa-solid fa-user",
            "value": all_objects.filter(message_type="user-sync").distinct("object_identifiers").count(),
            "text_class": "text-success"
        }

        context["total_investigations_general"] = {
            "title": "Investigations",
            "subtitle": "Total investigations synced",
            "icon": "fa-solid fa-flask",
            "value": all_objects.filter(message_type="proposal-sync").distinct("object_identifiers").count(),
            "text_class": "text-success"
        }

        context["msg_types_table_stats"] = []

        msg_types = GroupProfile.get_allowed_message_types(self.request.user)

        for msg_type in msg_types:
            msg_count = objects.filter(message_type=msg_type).count()
            errored_msg_count = objects.filter(message_type=msg_type, errored=True).count()

            error_messages = (
                objects
                .filter(message_type=msg_type, errored=True)
                .exclude(error_message__isnull=True)
                .exclude(error_message="")
                .values_list("error_message", flat=True)
            )

            normalized_errors = [
                normalize_error_message(error_message)
                for error_message in error_messages
            ]

            most_repeated_error = Counter(normalized_errors).most_common(1)

            context["msg_types_table_stats"].append({
                "type": msg_type,
                "msg_count": msg_count,
                "error_msg_count": errored_msg_count,
                "error_rate": round((errored_msg_count / msg_count) * 100 if msg_count > 0 else 0, 2),
                "most_repeated_error": most_repeated_error[0][0] if most_repeated_error else "",
                "most_repeated_error_count": most_repeated_error[0][1] if most_repeated_error else 0,
            })
            context["msg_types_table_stats"].sort(key=lambda x: x["error_rate"])
        return context
