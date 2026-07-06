#!/usr/bin/env python3
"""Minimal Craft MCP client — handles OAuth token refresh + raw JSON-RPC calls.

Usage (as a library):
    import craft_mcp
    craft_mcp.read("documents list --location unsorted --offset 0")
    craft_mcp.read("search resources/")
    craft_mcp.write('blocks add --id <rootBlockId> --markdown "#resources/repos" --position end')

Usage (CLI, for quick manual checks):
    python3 craft_mcp.py read "folders list"
    python3 craft_mcp.py write "blocks add --id ABC --markdown \"#resources/repos\" --position end"

Token file: ~/.sunny/mcp-oauth/craft.json (shared with Sunny's main mcp.json config —
do not hand-edit the client_id/token_endpoint, only tokens get rewritten here).

Gotcha (2026-07-06): Craft's Cloudflare-fronted endpoints reject requests without a
browser-like User-Agent (403 "browser_signature_banned"). Always send a real UA.
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TOKEN_FILE = Path.home() / ".sunny/mcp-oauth/craft.json"
BASE_URL = "https://mcp.craft.do/links/DSVtQGux9Yz/mcp"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


def _load_cfg():
    return json.loads(TOKEN_FILE.read_text())


def _save_cfg(cfg):
    TOKEN_FILE.write_text(json.dumps(cfg, indent=2))


def _refresh_token(cfg):
    client = cfg["clientInformation"]
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": cfg["tokens"]["refresh_token"],
        "client_id": client["client_id"],
    }).encode()
    req = urllib.request.Request(
        client["token_endpoint"], data=data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": UA,
        })
    r = urllib.request.urlopen(req, timeout=15)
    new_tokens = json.loads(r.read().decode())
    cfg["tokens"]["access_token"] = new_tokens["access_token"]
    cfg["tokens"]["refresh_token"] = new_tokens.get("refresh_token", cfg["tokens"]["refresh_token"])
    _save_cfg(cfg)
    return cfg


class _Session:
    def __init__(self):
        self.cfg = _load_cfg()
        self.sid = None
        self._initialized = False

    def _rpc(self, method, params, mid=1, _retried=False):
        body = json.dumps({"jsonrpc": "2.0", "id": mid, "method": method, "params": params}).encode()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {self.cfg['tokens']['access_token']}",
            "User-Agent": UA,
        }
        if self.sid:
            headers["Mcp-Session-Id"] = self.sid
        req = urllib.request.Request(BASE_URL, data=body, headers=headers)
        try:
            r = urllib.request.urlopen(req, timeout=30)
            if r.headers.get("Mcp-Session-Id"):
                self.sid = r.headers.get("Mcp-Session-Id")
            raw = r.read().decode()
        except urllib.error.HTTPError as e:
            if e.code in (401, 403) and not _retried:
                # Access token likely expired — refresh once and retry.
                self.cfg = _refresh_token(self.cfg)
                return self._rpc(method, params, mid=mid, _retried=True)
            return {"error": f"HTTP {e.code}: {e.read().decode()[:500]}"}
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
            "clientInfo": {"name": "sunny", "version": "1"},
        }, mid=0)
        self._initialized = True

    def call_tool(self, tool, command, mid=1):
        self._ensure_init()
        result = self._rpc("tools/call", {"name": tool, "arguments": {"command": command}}, mid=mid)
        try:
            text = result["result"]["content"][0]["text"]
        except (KeyError, IndexError, TypeError):
            return json.dumps(result)
        return text


_session = None


def _get_session():
    global _session
    if _session is None:
        _session = _Session()
    return _session


def read(command):
    """Call craft_read with a command string. Returns the tool's text output."""
    return _get_session().call_tool("craft_read", command)


def write(command):
    """Call craft_write with a command string. Returns the tool's text output."""
    return _get_session().call_tool("craft_write", command)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: craft_mcp.py <read|write> '<command>'", file=sys.stderr)
        sys.exit(1)
    verb, cmd = sys.argv[1], sys.argv[2]
    fn = read if verb == "read" else write
    print(fn(cmd))
