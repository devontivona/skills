#!/usr/bin/env python3
"""Minimal Home Assistant MCP client — raw JSON-RPC over Streamable HTTP.

The HA MCP server (ha-mcp on riker.local, Devon's home server) exposes ~77 ha_*
tools. This client is for SCRIPTED/BULK work (loops, history crunching, batch
entity updates) and for run surfaces that don't get the native MCP tools
injected. For one-off calls in a normal owner turn, prefer the injected
home-assistant__ha_* tools.

The base URL — including its secret path segment, the server's only auth — is
READ from ~/.sunny/state/mcp.json (entry "home-assistant") at runtime. Never
hardcode or copy that URL anywhere.

Usage (as a library):
    import ha
    ha.call("ha_get_state", entity_id="climate.thermostat")
    ha.call("ha_search", query="living room", domain_filter="light")
    for e in ids: print(ha.call("ha_get_state", entity_id=e))   # bulk loop

Usage (CLI, for quick manual checks):
    python3 ha.py list                                   # tool names
    python3 ha.py call ha_get_overview '{}'
    python3 ha.py call ha_get_state '{"entity_id": "lock.b129v915_lock_mechanism"}'

Protocol notes (why this file exists): POST JSON-RPC to the BASE url (not /mcp),
send Accept: application/json, text/event-stream, capture Mcp-Session-Id from
the initialize response headers and replay it on every later call. Responses
may arrive as SSE `data:` lines or plain JSON — both are handled.

Only reachable on Devon's home network (riker.local). Write/control tools are
live on real devices — confirm with the owner before non-trivial changes.
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

MCP_REGISTRY = Path.home() / ".sunny/state/mcp.json"
SERVER = "home-assistant"


def _base_url():
    entry = json.loads(MCP_REGISTRY.read_text())[SERVER]
    if not entry.get("enabled", False):
        raise RuntimeError(f"{SERVER} is disabled in {MCP_REGISTRY}")
    return entry["url"]


class _Session:
    def __init__(self):
        self.url = _base_url()
        self.sid = None
        self._initialized = False

    def _rpc(self, method, params, mid=1):
        body = json.dumps({"jsonrpc": "2.0", "id": mid, "method": method, "params": params}).encode()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.sid:
            headers["Mcp-Session-Id"] = self.sid
        req = urllib.request.Request(self.url, data=body, headers=headers)
        try:
            r = urllib.request.urlopen(req, timeout=30)
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.read().decode()[:500]}"}
        if r.headers.get("Mcp-Session-Id"):
            self.sid = r.headers.get("Mcp-Session-Id")
        raw = r.read().decode()
        out = None
        for line in raw.splitlines():
            if line.startswith("data:"):
                try:
                    out = json.loads(line[5:].strip())
                except Exception:
                    pass
        if out is None:
            try:
                out = json.loads(raw)
            except Exception:
                out = {"raw": raw}
        return out

    def _ensure_init(self):
        if self._initialized:
            return
        self._rpc("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "sunny-ha", "version": "1"},
        }, mid=0)
        self._initialized = True

    def list_tools(self):
        self._ensure_init()
        result = self._rpc("tools/list", {})
        try:
            return [t["name"] for t in result["result"]["tools"]]
        except (KeyError, TypeError):
            return result

    def call_tool(self, tool, arguments, mid=1):
        self._ensure_init()
        result = self._rpc("tools/call", {"name": tool, "arguments": arguments}, mid=mid)
        try:
            return result["result"]["content"][0]["text"]
        except (KeyError, IndexError, TypeError):
            return json.dumps(result)


_session = None


def _get_session():
    global _session
    if _session is None:
        _session = _Session()
    return _session


def call(tool, **arguments):
    """Call an ha_* tool with keyword arguments. Returns the tool's text output."""
    return _get_session().call_tool(tool, arguments)


def tools():
    """List available tool names."""
    return _get_session().list_tools()


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "list":
        print("\n".join(tools()))
    elif len(sys.argv) >= 3 and sys.argv[1] == "call":
        args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        print(_get_session().call_tool(sys.argv[2], args))
    else:
        print(__doc__)
        sys.exit(1)
