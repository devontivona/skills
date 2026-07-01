#!/usr/bin/env python3
"""Minimal Home Assistant MCP client (Streamable HTTP).

Talks to the ha-mcp server on Devon's home network. Only reachable on the LAN
(riker.local). The secret is in the URL path — keep it here, not in logs.

Usage as a library:
    import ha_mcp
    ha_mcp.call("ha_get_state", {"entity_id": "..."})   # returns parsed dict
Or CLI:
    python3 ha_mcp.py tools
    python3 ha_mcp.py call ha_get_state '{"entity_id":"light.x"}'
"""
import sys, json, urllib.request, os

BASE = os.environ.get("HA_MCP_URL",
    "http://riker.local:9583/private_GZ6N_rx5KhKmBn-_nqKCWg")

_sid = None

def _rpc(method, params, sid=None, mid=1):
    body = json.dumps({"jsonrpc":"2.0","id":mid,"method":method,"params":params}).encode()
    req = urllib.request.Request(BASE, data=body, headers={
        "Content-Type":"application/json",
        "Accept":"application/json, text/event-stream"})
    if sid: req.add_header("Mcp-Session-Id", sid)
    r = urllib.request.urlopen(req, timeout=25)
    sid2 = r.headers.get("Mcp-Session-Id")
    raw = r.read().decode()
    out = None
    for line in raw.splitlines():
        if line.startswith("data:"):
            try: out = json.loads(line[5:].strip())
            except: pass
    if out is None:
        try: out = json.loads(raw)
        except: out = raw
    return out, sid2

def _init():
    global _sid
    if _sid: return _sid
    _, _sid = _rpc("initialize", {"protocolVersion":"2024-11-05","capabilities":{},
        "clientInfo":{"name":"sunny-inovelli","version":"1"}})
    try:
        body = json.dumps({"jsonrpc":"2.0","method":"notifications/initialized","params":{}}).encode()
        req = urllib.request.Request(BASE, data=body, headers={
            "Content-Type":"application/json",
            "Accept":"application/json, text/event-stream",
            "Mcp-Session-Id":_sid})
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass
    return _sid

def call(tool, args):
    """Call an MCP tool. Returns the parsed inner JSON (structuredContent or text)."""
    _init()
    out, _ = _rpc("tools/call", {"name":tool,"arguments":args}, sid=_sid, mid=2)
    res = out.get("result", {}) if isinstance(out, dict) else {}
    # prefer structuredContent, fall back to first text block
    if isinstance(res, dict) and res.get("structuredContent") is not None:
        return {"_ok": not res.get("isError", False), "data": res["structuredContent"]}
    try:
        txt = res["content"][0]["text"]
        try: return {"_ok": not res.get("isError", False), "data": json.loads(txt)}
        except: return {"_ok": not res.get("isError", False), "data": txt}
    except Exception:
        return {"_ok": False, "data": out}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "tools"
    if cmd == "tools":
        _init()
        out, _ = _rpc("tools/list", {}, sid=_sid, mid=2)
        for t in out["result"]["tools"]:
            print(t["name"])
    elif cmd == "call":
        tool = sys.argv[2]
        args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        print(json.dumps(call(tool, args), indent=2)[:8000])
