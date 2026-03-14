from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4


def utc_now_iso() -> str:
	return datetime.now(timezone.utc).isoformat()


@dataclass
class Message:
	"""Node Server 与 Node 之间统一消息结构。"""

	action: str
	source: str
	target: str
	payload: Dict[str, Any] = field(default_factory=dict)
	message_id: str = field(default_factory=lambda: str(uuid4()))
	ts: str = field(default_factory=utc_now_iso)

	def to_dict(self) -> Dict[str, Any]:
		return {
			"message_id": self.message_id,
			"action": self.action,
			"source": self.source,
			"target": self.target,
			"payload": self.payload,
			"ts": self.ts,
		}

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> "Message":
		return cls(
			message_id=str(data.get("message_id") or str(uuid4())),
			action=str(data.get("action") or "unknown"),
			source=str(data.get("source") or "unknown"),
			target=str(data.get("target") or "unknown"),
			payload=dict(data.get("payload") or {}),
			ts=str(data.get("ts") or utc_now_iso()),
		)

