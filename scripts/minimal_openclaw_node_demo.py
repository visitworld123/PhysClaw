from __future__ import annotations

import re
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, Tuple

from node_server.server import PhysClawNodeServer
from nodes.robot_node.robot_node import RobotNode
from shared.config import load_node_server_config
from shared.message import Message


def _start_server_in_thread() -> Tuple[PhysClawNodeServer, threading.Thread]:
    server = PhysClawNodeServer()
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server, t


def _call_openclaw_agent(user_text: str) -> str:
    cmd = ["openclaw", "agent", "--message", user_text]
    try:
        proc = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=20)
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        if out:
            return out
        if err:
            return f"[openclaw stderr] {err}"
        return "[openclaw] no output"
    except FileNotFoundError:
        return "[openclaw] command not found, skip gateway response"
    except subprocess.TimeoutExpired:
        return "[openclaw] request timeout, continue local routing"
    except Exception as exc:  # pragma: no cover
        return f"[openclaw] failed: {exc}"


def _parse_robot_intent(text: str) -> Dict[str, object]:
    lowered = text.lower()
    if "pick" in lowered or "抓" in lowered:
        obj = "object"
        m = re.search(r"pick\s+([a-zA-Z0-9_-]+)", lowered)
        if m:
            obj = m.group(1)
        return {"command": "pick", "params": {"object": obj}}

    if "place" in lowered or "放" in lowered:
        return {"command": "place", "params": {"object": "object", "location": "target"}}

    nums = re.findall(r"-?\d+(?:\.\d+)?", lowered)
    if "move" in lowered or "移动" in lowered:
        pose = [float(x) for x in nums[:3]] if nums else [0.0, 0.0, 0.0]
        while len(pose) < 3:
            pose.append(0.0)
        return {"command": "move", "params": {"pose": pose[:3]}}

    return {"command": "move", "params": {"pose": [0.1, 0.2, 0.3]}}


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    cfg = load_node_server_config()
    server_url = cfg.base_url

    print(f"[demo] project root: {project_root}")
    print("[demo] starting PhysClaw Node Server ...")
    _server, _thread = _start_server_in_thread()
    time.sleep(0.4)

    robot = RobotNode(node_id="robot-demo-1", server_url=server_url)
    robot.run()
    print("[demo] robot node registered: robot-demo-1")
    print("[demo] input text (type 'exit' to quit)")

    try:
        while True:
            text = input("you> ").strip()
            if not text:
                continue
            if text.lower() in {"exit", "quit"}:
                break

            openclaw_resp = _call_openclaw_agent(text)
            print(f"openclaw> {openclaw_resp}")

            intent = _parse_robot_intent(text)
            gateway_message = Message(
                action="robot.command",
                source="openclaw-gateway",
                target="robot-demo-1",
                payload=intent,
            )

            dispatch = robot.send_message(gateway_message, mode="direct")
            print(f"router> {dispatch}")

            node_result = robot.handle_message(gateway_message)
            print(f"robot-node> {node_result}")
    finally:
        robot.stop()
        print("[demo] robot node stopped")


if __name__ == "__main__":
    main()
