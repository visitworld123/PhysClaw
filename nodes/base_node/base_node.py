from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict

from shared.message import Message
from shared.utils import http_json_request


@dataclass
class BaseNode:
    node_id: str
    node_type: str
    server_url: str
    endpoint: str = "local://node"
    metadata: Dict[str, Any] = field(default_factory=dict)
    heartbeat_interval_sec: int = 5

    _running: bool = field(default=False, init=False, repr=False)
    _heartbeat_thread: threading.Thread | None = field(default=None, init=False, repr=False)

    def register(self) -> Dict[str, Any]:
        return http_json_request(
            url=f"{self.server_url}/register",
            method="POST",
            body={
                "node_id": self.node_id,
                "node_type": self.node_type,
                "endpoint": self.endpoint,
                "metadata": self.metadata,
            },
        )

    def unregister(self) -> Dict[str, Any]:
        return http_json_request(
            url=f"{self.server_url}/unregister",
            method="POST",
            body={"node_id": self.node_id},
        )

    def heartbeat(self) -> Dict[str, Any]:
        return http_json_request(
            url=f"{self.server_url}/heartbeat",
            method="POST",
            body={"node_id": self.node_id},
        )

    def send_message(self, message: Message, mode: str = "direct", node_type: str = "") -> Dict[str, Any]:
        payload = message.to_dict()
        payload["mode"] = mode
        if node_type:
            payload["node_type"] = node_type
        return http_json_request(url=f"{self.server_url}/message", method="POST", body=payload)

    def handle_message(self, message: Message) -> Dict[str, Any]:
        return {
            "ok": True,
            "node_id": self.node_id,
            "handled_action": message.action,
            "echo": message.payload,
        }

    def _heartbeat_loop(self) -> None:
        while self._running:
            self.heartbeat()
            time.sleep(self.heartbeat_interval_sec)

    def run(self) -> None:
        reg = self.register()
        if not reg.get("ok"):
            raise RuntimeError(f"register failed: {reg}")
        self._running = True
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

    def stop(self) -> None:
        self._running = False
        self.unregister()
