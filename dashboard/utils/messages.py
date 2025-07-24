import json
import xml.etree.ElementTree as ET


def get_payload_format(payload: bytes | str) -> str:
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8", errors="ignore").strip()
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
