import hashlib
import json
import xml

from django import template
from django.conf import settings

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
    try:
        parsed = json.loads(value)
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    except Exception:
        return value


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
