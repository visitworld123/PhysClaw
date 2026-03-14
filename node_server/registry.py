from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class NodeRecord:
    node_id: str
    node_type: str
    endpoint: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_heartbeat: str = field(default_factory=_now_iso)
    registered_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "endpoint": self.endpoint,
            "metadata": self.metadata,
            "last_heartbeat": self.last_heartbeat,
            "registered_at": self.registered_at,
        }


class NodeRegistry:
    def __init__(self) -> None:
        self._nodes: Dict[str, NodeRecord] = {}
        self._lock = Lock()

    def register(self, node_id: str, node_type: str, endpoint: str, metadata: Optional[Dict[str, Any]] = None) -> NodeRecord:
        record = NodeRecord(
            node_id=node_id,
            node_type=node_type,
            endpoint=endpoint,
            metadata=dict(metadata or {}),
        )
        with self._lock:
            self._nodes[node_id] = record
        return record

    def unregister(self, node_id: str) -> bool:
        with self._lock:
            return self._nodes.pop(node_id, None) is not None

    def heartbeat(self, node_id: str) -> bool:
        with self._lock:
            node = self._nodes.get(node_id)
            if node is None:
                return False
            node.last_heartbeat = _now_iso()
            return True

    def get_node(self, node_id: str) -> Optional[NodeRecord]:
        with self._lock:
            return self._nodes.get(node_id)

    def list_nodes(self, node_type: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            if node_type is None:
                return {node_id: node.to_dict() for node_id, node in self._nodes.items()}
            return {
                node_id: node.to_dict()
                for node_id, node in self._nodes.items()
                if node.node_type == node_type
            }