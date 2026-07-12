---
name: home-assistant
description: Scripted/bulk access to Devon's Home Assistant via its MCP server. Use when a task needs many HA calls in a loop (history analysis, batch entity checks, bulk automation edits) or runs on a surface without the native home-assistant__ha_* tools. For a handful of one-off calls in a normal turn, just use the injected tools instead.
---

# home-assistant — scripted MCP access

Devon's Home Assistant runs on riker.local (his home server; LAN-only). Its MCP
server exposes ~77 `ha_*` tools which are injected natively into owner turns as
`home-assistant__ha_*` — **prefer those for one-off calls**. This skill is for the
cases native tools handle badly:

- Bulk/looped work: crunching entity history, checking dozens of entities,
  batch-editing automations — one Python loop instead of 50 tool calls.
- Run surfaces that don't get MCP tools injected.

## The helper

`scripts/ha.py` (next to this file). It reads the server URL — whose secret path
segment is the only auth — from `~/.sunny/state/mcp.json` at runtime. NEVER copy
that URL into code, notes, or memory; the registry is the single source of truth.

```python
import sys
sys.path.insert(0, "/expanded/path/to/~/.sunny/skills/authored/skills/home-assistant/scripts")
import ha
ha.tools()                                              # list tool names
ha.call("ha_get_state", entity_id="lock.b129v915_lock_mechanism")
ha.call("ha_search", query="living room", domain_filter="light")
```

CLI for quick checks:

```
python3 ~/.sunny/skills/authored/skills/home-assistant/scripts/ha.py list
python3 ~/.sunny/skills/authored/skills/home-assistant/scripts/ha.py call ha_get_overview '{}'
```

Protocol details (session-id handshake, SSE responses) are handled inside the
script and documented in its docstring — don't re-implement this client in
scratch; import it.

## Cautions

- Write/control tools act on REAL devices (locks, climate, automations).
  Confirm with the owner before any non-trivial change (restarts, deletes,
  automation edits) — same rule as the native tools.
- LAN-only: riker.local is unreachable off Devon's home network; expect
  connection errors elsewhere.
- Facts about the home itself (entity quirks, Sonos layout, lock states) live
  in memory `topic:home-assistant` — this skill is only the access procedure.
