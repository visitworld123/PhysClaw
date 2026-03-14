from __future__ import annotations

from typing import Any, Dict

from node_server.registry import NodeRegistry


class MessageRouter:
    def __init__(self, registry: NodeRegistry) -> None:
        self.registry = registry

    def route(self, message: Dict[str, Any]) -> Dict[str, Any]:
        target_id = str(message.get("target") or "")
        if not target_id:
            return {"ok": False, "error": "target is required"}
        node = self.registry.get_node(target_id)
        if node is None:
            return {"ok": False, "error": f"target node not found: {target_id}"}
        return {
            "ok": True,
            "dispatch": {
                "mode": "direct",
                "target": node.to_dict(),
                "message": message,
            },
        }

    def broadcast(self, message: Dict[str, Any]) -> Dict[str, Any]:
        nodes = list(self.registry.list_nodes().values())
        return {
            "ok": True,
            "dispatch": {
                "mode": "broadcast",
                "targets": nodes,
                "message": message,
            },
        }

    def route_to_type(self, node_type: str, message: Dict[str, Any]) -> Dict[str, Any]:
        nodes = list(self.registry.list_nodes(node_type=node_type).values())
        if not nodes:
            return {"ok": False, "error": f"no nodes of type: {node_type}"}
        return {
            "ok": True,
            "dispatch": {
                "mode": "type",
                "node_type": node_type,
                "targets": nodes,
                "message": message,
            },
        }