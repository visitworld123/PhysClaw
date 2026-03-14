from __future__ import annotations

from typing import Any, Dict

from nodes.base_node.base_node import BaseNode
from shared.message import Message


class ValueModelNode(BaseNode):
    """价值模型节点：对候选动作进行打分。"""

    def __init__(self, node_id: str, server_url: str) -> None:
        super().__init__(
            node_id=node_id,
            node_type="value_model",
            server_url=server_url,
            endpoint=f"value-model://{node_id}",
            metadata={"capabilities": ["score_action"]},
        )

    def score_action(self, action_plan: str, context: Dict[str, Any]) -> Dict[str, Any]:
        base_score = 0.75
        if "grasp" in action_plan:
            base_score += 0.1
        if context.get("safety") == "strict":
            base_score -= 0.05
        return {"ok": True, "score": round(max(0.0, min(1.0, base_score)), 3)}

    def handle_message(self, message: Message) -> Dict[str, Any]:
        if message.action == "value.score":
            action_plan = str(message.payload.get("action_plan") or "")
            context = dict(message.payload.get("context") or {})
            return self.score_action(action_plan=action_plan, context=context)
        return super().handle_message(message)
