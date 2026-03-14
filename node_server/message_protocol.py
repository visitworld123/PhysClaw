from __future__ import annotations

from typing import Any, Dict, Tuple

REQUIRED_MESSAGE_FIELDS = ("action", "source", "target", "payload")


def validate_message(data: Dict[str, Any]) -> Tuple[bool, str]:
	if not isinstance(data, dict):
		return False, "message must be a JSON object"
	for field in REQUIRED_MESSAGE_FIELDS:
		if field not in data:
			return False, f"missing field: {field}"
	if not isinstance(data.get("payload"), dict):
		return False, "payload must be object"
	return True, "ok"

