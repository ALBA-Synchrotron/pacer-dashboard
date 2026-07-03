import ast
import hashlib
import itertools
import json
import xml

from django import template
from django.conf import settings

from dashboard.models import GroupProfile

register = template.Library()


@register.simple_tag
def error_str_parsing(s: str) -> dict:
    try:
        return json.loads(s)
    except Exception:
        return {"error": s}

@register.filter
def shorten_hash(value: str) -> str:
    if len(value) > 16:
        return f"{value[:16]}..."
    return value

@register.filter
def pretty_json(value) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2, ensure_ascii=False)

    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            pass

        try:
            parsed = ast.literal_eval(value)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except (ValueError, SyntaxError):
            return value

    return str(value)


@register.simple_tag
def app_subpath() -> str:
    if not settings.FORCE_SCRIPT_NAME:
        return ""
    return settings.FORCE_SCRIPT_NAME

@register.simple_tag
def sockets_subpath() -> str:
    if not settings.SOCKETS_CONTEXT_PATH:
        return ""
    return settings.SOCKETS_CONTEXT_PATH

@register.filter
def pretty_xml(value) -> str:
    try:
        dom = xml.dom.minidom.parseString(value)
        pretty = dom.toprettyxml(indent="  ")
        pretty = "\n".join(line for line in pretty.split("\n") if line.strip())
        return pretty
    except Exception:
        return value

def stable_hash(s: str) -> int:
    return int(hashlib.md5(s.encode("utf-8")).hexdigest(), 16)

@register.filter
def badge_bg(name: str) -> str:
    h = stable_hash(name)
    hue = h % 360
    return f"hsl({hue} 55% 88%)"

@register.filter
def badge_text(name: str) -> str:
    h = stable_hash(name)
    hue = h % 360
    return f"hsl({hue} 70% 35%)"

@register.simple_tag(takes_context=True)
def message_actions_allowed(context) -> bool:
    if settings.ADMIN_ROLE_GROUP_NAME in [i.name for i in context["request"].user.groups.all()]:
        return True
    return GroupProfile.message_actions_allowed(context["request"].user)

@register.simple_tag
def can_reingest_message(user, msg):
    if settings.ADMIN_ROLE_GROUP_NAME in [g.name for g in user.groups.all()]:
        return True

    allowed_reingestions = [
        message_type
        for g in user.groups.all()
        for message_type in (g.groupprofile.allowed_message_types_reingest or "").split(",")
        if message_type
    ]
    return msg.message_type in allowed_reingestions