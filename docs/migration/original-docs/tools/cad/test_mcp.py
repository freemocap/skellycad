"""End-to-end MCP handshake and live FreeCAD query (no source edits)."""
import asyncio
import json
import os
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


async def main():
    params = StdioServerParameters(command=str(HERE / ".venv/Scripts/freecad-mcp.exe"), args=["--host", "127.0.0.1"], env=dict(os.environ))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            status = await session.call_tool("get_rpc_status", {})
            documents = await session.call_tool("list_documents", {})
            report = {"tools": [t.name for t in tools.tools], "status": status.model_dump(mode="json"), "documents": documents.model_dump(mode="json")}
            text = "\n".join(getattr(c, "text", "") for c in status.content)
            if getattr(status, "is_error", getattr(status, "isError", False)) or '"success": true' not in text.lower():
                raise RuntimeError(f"FreeCAD live status failed: {text}")
            if getattr(documents, "is_error", getattr(documents, "isError", False)):
                raise RuntimeError("FreeCAD document query failed")
            path = ROOT / "generated/mcp-check.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print("CAD_MCP_OK", len(tools.tools), "tools; live FreeCAD status checked")


if __name__ == "__main__":
    asyncio.run(asyncio.wait_for(main(), timeout=60))
