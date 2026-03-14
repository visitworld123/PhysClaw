from __future__ import annotations

from typing import Any, Dict

from nodes.base_node.base_node import BaseNode
from shared.message import Message


class VLANode(BaseNode):
    """VLA 节点：输入视觉/文本观测，输出动作建议。"""

    def __init__(self, node_id: str, server_url: str) -> None:
        super().__init__(
            node_id=node_id,
            node_type="vla",
            server_url=server_url,
            endpoint=f"vla://{node_id}",
            metadata={"capabilities": ["plan_action"]},
        )

    def plan_action(self, observation: str, goal: str) -> Dict[str, Any]:
        action = f"Based on observation='{observation[:60]}', execute approach->grasp->lift toward goal='{goal}'"
        return {"ok": True, "action_plan": action}

    def handle_message(self, message: Message) -> Dict[str, Any]:
        if message.action == "vla.plan":
            observation = str(message.payload.get("observation") or "")
            goal = str(message.payload.get("goal") or "")
            return self.plan_action(observation=observation, goal=goal)
        return super().handle_message(message)
