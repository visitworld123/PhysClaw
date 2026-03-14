from __future__ import annotations

from dataclasses import dataclass

from shared.config import load_node_server_config


@dataclass(frozen=True)
class ServerRuntimeConfig:
	host: str
	port: int


def get_server_runtime_config() -> ServerRuntimeConfig:
	cfg = load_node_server_config()
	return ServerRuntimeConfig(host=cfg.host, port=cfg.port)

