---
name: inovelli-switches
description: Manage Kate/Devon's Inovelli VZW32-SN Blue/Red Series mmWave presence dimmer switches over Home Assistant (Z-Wave JS via the HA MCP): read/copy/set config parameters, un-disable the integration-disabled config entities, write automations, and tune mmWave presence. Use whenever working with Inovelli switches, mmWave dimmers, mmwave presence lighting, or copying switch config across many switches.
---

# Inovelli VZW32-SN mmWave dimmer management

Devon's house has a growing fleet of **Inovelli VZW32-SN** 2-in-1 dimmer + mmWave
presence switches (Blue/Red Series, same Z-Wave param model), on **Z-Wave JS** in
Home Assistant. Goal is to configure, tune, and automate them at scale (20+ planned).

Everything here goes through the **HA MCP** (`home-assistant` server, `riker.local:9583`)
— only reachable on Devon's home LAN. See `topic:home-assistant` for the MCP itself and
`topic:inovelli-switches` for the live per-switch inventory/state (that memory doc is the
source of truth for which switches exist; this skill is the *how*).

## Tooling

Two scripts ship with this skill (run with `python3` from the skill dir):

- `scripts/ha_mcp.py` — minimal MCP client. `call(tool, args)` returns `{"_ok":bool,"data":...}`.
- `scripts/inovelli.py` — the switch commands. Always start here:

```
cd ~/.sunny/skills/authored/skills/inovelli-switches
python3 scripts/inovelli.py list                                  # all switches: node, name, area, light entity, device_id
python3 scripts/inovelli.py readparam <light_entity> <suffix>     # read a config value (entity must be ENABLED)
python3 scripts/inovelli.py setparam <light_entity> <param#> <v>  # write one param by NUMBER (works even if entity disabled)
python3 scripts/inovelli.py copy   <source_light_entity> [p#,p#]  # copy params from one switch to ALL others
python3 scripts/inovelli.py enable <device_id> [suffix,suffix]    # un-disable config entities so they show in the HA UI
```

`HA_MCP_URL` env var overrides the server URL if it ever changes.

## The two hard-won gotchas (read before doing anything)

1. **Most config entities ship DISABLED by the integration.** Inovelli exposes ~131
   entities per switch; HA disables the advanced/config ones (`disabled_by: "integration"`),
   so they read `None`/`unknown` and don't appear in the UI. Two consequences:
   - To **write** a value, don't wait to enable it — `zwave_js.set_config_parameter` writes
     **by parameter number** and works regardless of entity enabled-state. This is the
     reliable path; `setparam` / `copy` use it.
   - To let Kate/Devon **see and hand-edit** a setting in the HA UI (and so you can read it
     back), the entity must be **enabled** first: `inovelli.py enable <device_id>`.
   - You **cannot read a value back until its entity is enabled** — a disabled entity's
     state is `None`. So the read-verify step only works post-enable.

2. **`zwave_js.set_config_parameter` call shape** (via `ha_call_service`): put
   `parameter` and `value` inside **`data`**, and `entity_id` at the **top level** (NOT in
   service_data). `inovelli.py setparam` already does this. Returns success synchronously
   but you still can't read the value back over MCP unless the entity is enabled.

3. **Duplicate switches get `_2` entity suffixes.** When two switches share a base name
   (e.g. two `light.kitchen_mmwave_dimmer`), the second one's config entities are
   `..._default_level_local_2` etc. The scripts match `<suffix>(_\d+)?` so this is handled —
   but eyeball `list` output to confirm you're hitting the right device_id.

## Common jobs

### Copy one switch's config to all the others
This is the headline use case (what Kate asked for: match the kitchen counter switch).
```
python3 scripts/inovelli.py copy light.kitchen_kitchen_counter_lights
```
Copies the DEFAULT set (114 mmWave detection timeout, 13 default level local, 95 LED
color-when-on, 96 LED color-when-off) from the source to every other Inovelli switch.
Pass a custom CSV of param numbers as a 2nd arg to copy a different set. NOTE: the source's
entities for those params must be **enabled** so their values can be read; if `copy` prints
`source param X reads None`, run `enable` on the source device first.

Then make them visible/editable in the UI on the targets:
```
python3 scripts/inovelli.py enable <device_id>   # for each target device_id from `list`
```

### Set a single parameter on one switch
```
python3 scripts/inovelli.py setparam light.garage_mmwave_dimmer 114 600   # detection timeout 600s
```

### Verify a write stuck
Enable the entity, then read:
```
python3 scripts/inovelli.py enable <device_id> mmwave_detection_timeout
python3 scripts/inovelli.py readparam <light_entity> mmwave_detection_timeout
```

## Parameters

Quick map of the ones we use most (full table + descriptions in
`references/parameters.md` — read it before tuning geometry/sensitivity):

| # | Name | Range / units | Notes |
|---|------|---------------|-------|
| 12 | Auto Off Timer | seconds, 0=off | turns load off N s after on |
| 13 | Default Level (Local) | 0–99, 0=restore prev | brightness on local press |
| 14 | Default Level (Remote) | 0–99 | brightness on hub/remote on |
| 95 | Default All-LED Color When On | 0–255 hue | LED bar color, load on |
| 96 | Default All-LED Color When Off | 0–255 hue | LED bar color, load off |
| 97 | Default All-LED Brightness When On | 0–100 | |
| 98 | Default All-LED Brightness When Off | 0–100 | |
| 108 | mmWave Stay Life | 50ms units (÷20 = sec) | how long presence "holds" after last detect |
| 110 | Light On Presence Behavior | 0=manual … 1=auto on+off | **sensor→load mode**; 0 = sensor does NOT drive the load |
| 114 | mmWave Detection Timeout | seconds | detection window |

**Param 110 is the big one for behavior:** set it to **0 (manual)** if you want the switch's
built-in mmWave to *not* auto-control the load (e.g. you're driving lighting from an HA
automation instead, or the built-in short timeout keeps killing the light). Default is 1
(auto on+off). This bit Kate — see `topic:inovelli-switches`.

Param 26 (Dimming Mode) is **read-only / locked by Inovelli** — do not attempt to write it
(hardware-damage risk).

## Automations

Presence lighting via HA automation (more flexible than the switch's built-in timeout):
each switch has `binary_sensor.<name>_motion_detection`. Pattern that works well:
trigger on motion sensor → `off` for the desired duration, condition light is on, action
`light.turn_off`. With param 110=0 the switch won't fight the automation. Example live in
Devon's HA: automation id `living_room_off_after_1h_no_motion` (see topic doc).

Use `ha_config_set_automation` via the MCP to create these; confirm the YAML with
Devon/Kate before writing (per the confirm-before-write rule in topic:home-assistant).

## When a new switch is added
1. `python3 scripts/inovelli.py list` — confirm it appears (model VZW32-SN, alive).
   If it's not alive/interviewed, that's a physical/mesh problem — see the Node 16 saga in
   `topic:inovelli-switches`; re-interview must be done in the HA Z-Wave UI.
2. `copy light.kitchen_kitchen_counter_lights` (or whichever is the reference switch) to
   push the standard config to it.
3. `enable <device_id>` so the settings are visible/editable in the UI.
4. Update the inventory in `topic:inovelli-switches` (node id, name, entity, area).
