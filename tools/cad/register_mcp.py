"""Register the pinned bridge for this repository only; preserve unrelated config."""
import json
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[2]
target = ROOT / ".codex/config.toml"
existing = target.read_text(encoding="utf-8-sig") if target.exists() else ""
config = tomllib.loads(existing)
name = "skellycad_freecad"
entry = {"command": "powershell.exe", "args": ["-NoProfile", "-File", str(ROOT / "tools/cad/cad.ps1"), "mcp"], "cwd": str(ROOT), "startup_timeout_sec": 30, "tool_timeout_sec": 180}
old = config.get("mcp_servers", {}).get(name)
if old is not None and old != entry:
    raise RuntimeError("An existing skellycad_freecad configuration differs; review before changing it")
if old is None:
    block = f"\n[mcp_servers.{name}]\n" + "\n".join(f"{k} = {json.dumps(v)}" for k, v in entry.items()) + "\n"
    tomllib.loads(existing + block)
    target.parent.mkdir(exist_ok=True)
    target.write_text(existing + block, encoding="utf-8")
print(f"Registered {name} in {target}. Reload MCP servers in Codex to load it.")
