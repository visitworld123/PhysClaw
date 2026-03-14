from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional


def http_json_request(
	url: str,
	method: str = "GET",
	body: Optional[Dict[str, Any]] = None,
	timeout: int = 10,
) -> Dict[str, Any]:
	data = None
	headers = {"Content-Type": "application/json"}
	if body is not None:
		data = json.dumps(body).encode("utf-8")
	req = urllib.request.Request(url=url, data=data, method=method.upper(), headers=headers)

	try:
		with urllib.request.urlopen(req, timeout=timeout) as resp:
			raw = resp.read().decode("utf-8")
			return json.loads(raw) if raw else {}
	except urllib.error.HTTPError as exc:
		payload = exc.read().decode("utf-8") if exc.fp else ""
		try:
			return json.loads(payload)
		except Exception:
			return {"ok": False, "error": f"HTTPError {exc.code}", "raw": payload}
	except Exception as exc:  # pragma: no cover - 兜底异常
		return {"ok": False, "error": str(exc)}

