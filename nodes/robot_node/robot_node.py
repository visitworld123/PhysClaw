from __future__ import annotations

from typing import Any, Dict

from nodes.base_node.base_node import BaseNode
from shared.message import Message


class RobotNode(BaseNode):
    """机器人执行节点：模拟运动与抓取动作。"""

    def __init__(self, node_id: str, server_url: str) -> None:
        super().__init__(
            node_id=node_id,
            node_type="robot",
            server_url=server_url,
            endpoint=f"robot://{node_id}",
            metadata={"capabilities": ["move", "pick", "place"]},
        )

    def execute_robot_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if command == "move":
            pose = params.get("pose", [0, 0, 0])
            return {"ok": True, "result": f"robot moved to pose {pose}"}
        if command == "pick":
            obj = params.get("object", "unknown")
            return {"ok": True, "result": f"robot picked {obj}"}
        if command == "place":
            obj = params.get("object", "unknown")
            loc = params.get("location", "default")
            return {"ok": True, "result": f"robot placed {obj} at {loc}"}
        return {"ok": False, "error": f"unsupported robot command: {command}"}

    def handle_message(self, message: Message) -> Dict[str, Any]:
        if message.action == "robot.command":
            command = str(message.payload.get("command") or "")
            params = dict(message.payload.get("params") or {})
            return self.execute_robot_command(command=command, params=params)
        return super().handle_message(message)
