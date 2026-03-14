from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Tuple
from urllib.parse import parse_qs, urlparse

from node_server.config import get_server_runtime_config
from node_server.message_protocol import validate_message
from node_server.registry import NodeRegistry
from node_server.router import MessageRouter


class PhysClawNodeServer:
	def __init__(self) -> None:
		self.registry = NodeRegistry()
		self.router = MessageRouter(self.registry)
		self.config = get_server_runtime_config()

	def create_handler(self):
		server = self

		class Handler(BaseHTTPRequestHandler):
			def _read_json(self) -> Dict[str, Any]:
				length = int(self.headers.get("Content-Length", "0"))
				raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
				try:
					return json.loads(raw)
				except Exception:
					return {}

			def _write_json(self, code: int, payload: Dict[str, Any]) -> None:
				body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
				self.send_response(code)
				self.send_header("Content-Type", "application/json; charset=utf-8")
				self.send_header("Content-Length", str(len(body)))
				self.end_headers()
				self.wfile.write(body)

			def log_message(self, format: str, *args: Any) -> None:
				return

			def do_GET(self):  # noqa: N802
				parsed = urlparse(self.path)
				if parsed.path == "/health":
					self._write_json(200, {"ok": True, "service": "physclaw-node-server"})
					return
				if parsed.path == "/nodes":
					qs = parse_qs(parsed.query)
					node_type = qs.get("type", [None])[0]
					data = server.registry.list_nodes(node_type=node_type)
					self._write_json(200, {"ok": True, "nodes": data})
					return
				self._write_json(404, {"ok": False, "error": "not found"})

			def do_POST(self):  # noqa: N802
				if self.path == "/register":
					body = self._read_json()
					required = ("node_id", "node_type", "endpoint")
					missing = [k for k in required if not body.get(k)]
					if missing:
						self._write_json(400, {"ok": False, "error": f"missing fields: {missing}"})
						return
					record = server.registry.register(
						node_id=str(body["node_id"]),
						node_type=str(body["node_type"]),
						endpoint=str(body["endpoint"]),
						metadata=dict(body.get("metadata") or {}),
					)
					self._write_json(200, {"ok": True, "node": record.to_dict()})
					return

				if self.path == "/unregister":
					body = self._read_json()
					node_id = str(body.get("node_id") or "")
					if not node_id:
						self._write_json(400, {"ok": False, "error": "node_id is required"})
						return
					ok = server.registry.unregister(node_id)
					self._write_json(200, {"ok": ok})
					return

				if self.path == "/heartbeat":
					body = self._read_json()
					node_id = str(body.get("node_id") or "")
					ok = server.registry.heartbeat(node_id)
					self._write_json(200, {"ok": ok})
					return

				if self.path == "/message":
					body = self._read_json()
					valid, reason = validate_message(body)
					if not valid:
						self._write_json(400, {"ok": False, "error": reason})
						return
					mode = str(body.get("mode") or "direct")
					if mode == "broadcast":
						result = server.router.broadcast(body)
					elif mode == "type":
						node_type = str(body.get("node_type") or "")
						result = server.router.route_to_type(node_type=node_type, message=body)
					else:
						result = server.router.route(body)
					self._write_json(200, result)
					return

				self._write_json(404, {"ok": False, "error": "not found"})

		return Handler

	def serve_forever(self) -> None:
		httpd = ThreadingHTTPServer((self.config.host, self.config.port), self.create_handler())
		print(f"[physclaw-node-server] listening at http://{self.config.host}:{self.config.port}")
		httpd.serve_forever()


def main() -> None:
	server = PhysClawNodeServer()
	server.serve_forever()


if __name__ == "__main__":
	main()

