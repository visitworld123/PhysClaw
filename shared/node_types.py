from __future__ import annotations

from enum import Enum


class NodeType(str, Enum):
	"""支持的 PhysClaw 节点类型。"""

	ROBOT = "robot"
	VLA = "vla"
	VALUE_MODEL = "value_model"
	WORLD_MODEL = "world_model"

