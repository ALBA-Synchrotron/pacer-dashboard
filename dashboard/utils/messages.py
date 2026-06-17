import json
import xml.etree.ElementTree as ET

from django.db.models import Q

from dashboard.models import GroupProfile


def get_payload_format(payload: bytes | str) -> str:
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8", errors="ignore").strip()
    if isinstance(payload, dict):
        return "json"
    try:
        json.loads(payload)
        return "json"
    except (ValueError, json.JSONDecodeError):
        pass
    try:
        ET.fromstring(payload)
        return "xml"
    except ET.ParseError:
        pass
    return "unknown"


def get_user_filters(request) -> Q:
    user_filter: Q = GroupProfile.get_user_filters(request.user)
    message_type_filters: list = request.GET.getlist("msg-filters")
    text_search: str = request.GET.get("general-search", "").strip()
    errored_only: bool = request.GET.get("errored-only", "off") == "on"
    payload_types: list = request.GET.getlist("payload-type")
    start_date: str = request.GET.get("startDate", "")
    end_date: str = request.GET.get("endDate", "")
    include_acknowledged: bool = request.GET.get("include-acknowledged", "off") == "on"

    if message_type_filters:
        user_filter &= Q(message_type__in=message_type_filters)
    if text_search:
        user_filter &= Q(object_identifiers__icontains=text_search) | Q(hash__icontains=text_search)
    if errored_only:
        user_filter &= Q(errored=True)
    if payload_types:
        user_filter &= Q(payload_format__in=(i.lower() for i in payload_types))
    if start_date:
        user_filter &= Q(processing_start__gte=start_date)
    if end_date:
        user_filter &= Q(processing_start__lte=end_date)
    if not include_acknowledged:
        user_filter &= Q(acknowledged=False)
    return user_filter