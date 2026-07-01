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
| 108 | mmWave Stay Life | seconds, 0-3600 (default 300) | how long a MOTIONLESS person still counts as present |
| 110 | mmWave Load Behavior | 0-6 (default 1) | **1 = auto on+off = native presence lighting, no automation**; 0 = disabled |
| 114 | mmWave Hold Time | seconds (default 10) | off-delay after presence lost; fleet=600 |

**Param 110 is the big one for behavior.** Default 1 (Auto On/Off when Occupied) = full
native presence lighting, on and off, no automation needed. Set it to **0** only to fully
disable presence control of the load. Values 2–6 are one-way / inverted variants (see
references/parameters.md). If presence "off" feels wrong, tune 114/108/112 rather than
switching to manual+automation.

Param 26 (Dimming Mode) is **read-only / locked by Inovelli** — do not attempt to write it
(hardware-damage risk).

## Presence lighting: use the NATIVE behavior, not an automation

**Default `param 110 = 1` (Auto On/Off when Occupied) already gives presence-driven ON and
OFF for free — you do NOT need an HA automation for basic presence lighting.** The off-timing
is controlled by parameters, not an automation:
- `114` mmWave Hold Time — how long the load stays on after presence is lost (Devon's fleet
  = 600s / 10 min; default is only 10s).
- `108` mmWave Stay Life — how long a *motionless* person still counts as present (default
  300s). Raise for sit-still rooms so the light doesn't drop while someone is barely moving.
- `112` Sensitivity / `113` Trigger Speed / `101–106` geometry — detection tuning.

If a light "keeps turning off while someone sits still," that's a **tuning problem** (raise
108/112, shape geometry), NOT a reason to build an automation. See references/sensitivity.md.

### Working example: time-based hold-time (day/night)
A good use of an automation is flipping a *parameter* on a schedule while leaving presence
native. Devon's "Main Floor mmWave Hold Time — day/night" (entity
`automation.main_floor_mmwave_hold_time_day_night`): two `time` triggers (22:00 id=night,
07:00 id=day) → `choose` by trigger id → `zwave_js.set_config_parameter` param 114 to 300
(night, 5 min) or 7200 (day, 2 hr) on the 5 main-floor light entities. Presence stays 110=1;
only the hold time changes, so a still-present person keeps the light on and the timer only
starts once they leave. This is the preferred shape: automate the *tuning*, not the on/off.

Historical note: an automation `living_room_off_after_1h_no_motion` was built for Kate's
first switch as a workaround before we had the real docs. With param tuning it's unnecessary —
prefer native 110=1. Only build an HA automation (`ha_config_set_automation`) when you need
logic the switch genuinely can't do, e.g. time-of-day behavior or cross-device scenes. Confirm
YAML with Devon/Kate before writing (confirm-before-write rule, topic:home-assistant).

## When a new switch is added
1. `python3 scripts/inovelli.py list` — confirm it appears (model VZW32-SN, alive).
   If it's not alive/interviewed, that's a physical/mesh problem — see the Node 16 saga in
   `topic:inovelli-switches`; re-interview must be done in the HA Z-Wave UI.
2. `copy light.kitchen_kitchen_counter_lights` (or whichever is the reference switch) to
   push the standard config to it.
3. `enable <device_id>` so the settings are visible/editable in the UI.
4. Update the inventory in `topic:inovelli-switches` (node id, name, entity, area).
