from __future__ import annotations

from typing import Any, Dict

from nodes.base_node.base_node import BaseNode
from shared.message import Message


class WorldModelNode(BaseNode):
    """世界模型节点：进行简化状态预测。"""

    def __init__(self, node_id: str, server_url: str) -> None:
        super().__init__(
            node_id=node_id,
            node_type="world_model",
            server_url=server_url,
            endpoint=f"world-model://{node_id}",
            metadata={"capabilities": ["predict_next_state"]},
        )

    def predict_next_state(self, state: Dict[str, Any], action: str) -> Dict[str, Any]:
        next_state = dict(state)
        next_state["last_action"] = action
        next_state["predicted"] = True
        return {"ok": True, "next_state": next_state}

    def handle_message(self, message: Message) -> Dict[str, Any]:
        if message.action == "world.predict":
            state = dict(message.payload.get("state") or {})
            action = str(message.payload.get("action") or "")
            return self.predict_next_state(state=state, action=action)
        return super().handle_message(message)
