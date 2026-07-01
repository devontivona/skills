#!/usr/bin/env python3
"""Inovelli VZW32-SN switch management over the HA MCP.

High-level helpers built on ha_mcp.py. Commands:

  list
      List all Inovelli VZW32-SN devices (node, name, area, light entity, device_id).

  setparam <light_entity> <param#> <value>
      Write one Z-Wave config parameter by number (works even when the matching
      config entity is disabled — this is the reliable path).

  readparam <device_id_or_light_entity> <suffix>
      Read a config value back via its number.* entity state (only works if the
      entity is ENABLED). suffix e.g. mmwave_detection_timeout, default_level_local.

  copy <source_light_entity> [<param#>,<param#>,...]
      Read the given params from the source switch's ENABLED config entities and
      write them to every OTHER Inovelli switch. If no param list given, uses the
      DEFAULT_COPY_SET below. Prints a per-switch result grid.

  enable <device_id> [<suffix>,...]
      Un-disable (enable) the integration-disabled config entities matching the
      given suffixes on a device, so they show up + are editable in the HA UI.

Param numbers live in PARАМS below; full reference in references/parameters.md.
"""
import sys, json, time, re
sys.path.insert(0, __file__.rsplit("/",1)[0])
import ha_mcp

MODEL = "VZW32-SN"

# --- Parameter number map (see references/parameters.md for the full table) ---
PARAMS = {
    "auto_off_timer": 12,          # seconds, 0=disabled
    "default_level_local": 13,     # 0-99, 0=restore previous
    "default_level_remote": 14,    # 0-99
    "led_color_on": 95,            # Default All LED Strip Color When On (0-255 hue)
    "led_color_off": 96,           # Default All LED Strip Color When Off
    "led_bright_on": 97,           # Default All LED Strip Brightness When On (0-100)
    "led_bright_off": 98,          # Default All LED Strip Brightness When Off
    "mmwave_stay_life": 108,       # 50ms units (÷20 = seconds)
    "light_on_presence_behavior": 110,  # sensor->load mode: 0 manual .. 1 auto on+off
    "mmwave_detection_timeout": 114,    # seconds
}

# Suffix (HA entity name tail) -> param number, for reading enabled entities.
SUFFIX_PARAM = {
    "mmwave_detection_timeout": 114,
    "default_level_local": 13,
    "default_level_remote": 14,
    "default_all_led_strip_color_when_on": 95,
    "default_all_led_strip_color_when_off": 96,
    "auto_off_timer": 12,
    "mmwave_stay_life": 108,
}

# What `copy` grabs by default (param# -> friendly).
DEFAULT_COPY_SET = [114, 13, 95, 96]

def _devices():
    r = ha_mcp.call("ha_get_device", {"manufacturer":"Inovelli","detail_level":"summary","limit":50})
    d = r["data"]
    devs = d.get("devices") or d.get("device") or []
    if isinstance(devs, dict): devs = [devs]
    return [x for x in devs if x.get("model")==MODEL]

def _device_full(device_id):
    r = ha_mcp.call("ha_get_device", {"device_id":device_id,"detail_level":"full"})
    return r["data"]["device"]

def _light_entity(dev_full):
    for e in dev_full["entities"]:
        if e["entity_id"].startswith("light."):
            return e["entity_id"]
    return None

def _find_config_entity(dev_full, suffix):
    """Return the number.* entity whose name tail matches suffix (+optional _N)."""
    pat = re.compile(r"_"+re.escape(suffix)+r"(_\d+)?$")
    for e in dev_full["entities"]:
        eid = e["entity_id"]
        if eid.startswith("number.") and pat.search(eid):
            return eid
    return None

def _state(entity_id):
    r = ha_mcp.call("ha_get_state", {"entity_id":entity_id})
    try:
        return r["data"]["data"]["state"]
    except Exception:
        return None

def setparam(light_entity, param, value):
    r = ha_mcp.call("ha_call_service", {
        "domain":"zwave_js","service":"set_config_parameter",
        "entity_id":light_entity,
        "data":{"parameter":int(param),"value":int(value)}})
    return "ok" if r["_ok"] else "ERR"

def cmd_list():
    for x in sorted(_devices(), key=lambda d: str(d.get("area_id"))):
        full = _device_full(x["device_id"])
        le = _light_entity(full)
        print(f"node {x.get('node_id'):>4}  {x.get('name'):40}  area={x.get('area_id'):12}  {le}  [{x['device_id']}]")

def cmd_setparam(light_entity, param, value):
    print(setparam(light_entity, param, value), light_entity, f"p{param}={value}")

def cmd_readparam(dev, suffix):
    if dev.startswith("light."):
        # resolve device from light entity
        r = ha_mcp.call("ha_get_device", {"entity_id":dev,"detail_level":"full"})
        full = r["data"]["device"]
    else:
        full = _device_full(dev)
    eid = _find_config_entity(full, suffix)
    print(eid, "=>", _state(eid) if eid else "NOT FOUND")

def cmd_copy(source_light, param_csv=None):
    params = [int(p) for p in param_csv.split(",")] if param_csv else DEFAULT_COPY_SET
    # read source values from its enabled config entities
    r = ha_mcp.call("ha_get_device", {"entity_id":source_light,"detail_level":"full"})
    src_full = r["data"]["device"]
    num_to_suffix = {v:k for k,v in SUFFIX_PARAM.items()}
    src_vals = {}
    for p in params:
        suf = num_to_suffix.get(p)
        eid = _find_config_entity(src_full, suf) if suf else None
        st = _state(eid) if eid else None
        if st in (None, "unknown", "unavailable"):
            print(f"!! source param {p} ({suf}) reads {st} — enable it on the source first, or pass values manually")
        src_vals[p] = st
    print("Source values:", {p:src_vals[p] for p in params})
    src_id = src_full["device_id"]
    for x in _devices():
        if x["device_id"] == src_id:
            continue
        full = _device_full(x["device_id"])
        le = _light_entity(full)
        line = [f"{x.get('name'):32}"]
        for p in params:
            v = src_vals[p]
            if v in (None,"unknown","unavailable"):
                line.append(f"p{p}:skip"); continue
            st = setparam(le, p, int(float(v)))
            line.append(f"p{p}={int(float(v))}:{st}")
            time.sleep(0.4)
        print("  ".join(line))

def cmd_enable(device_id, suffix_csv=None):
    full = _device_full(device_id)
    suffixes = suffix_csv.split(",") if suffix_csv else list(SUFFIX_PARAM.keys())
    for suf in suffixes:
        eid = _find_config_entity(full, suf)
        if not eid:
            print("skip (no entity):", suf); continue
        r = ha_mcp.call("ha_set_entity", {"entity_id":eid,"enabled":True})
        ok = r["_ok"] and (r["data"].get("success") if isinstance(r["data"],dict) else True)
        print(("ok " if ok else "ERR"), eid)
        time.sleep(0.3)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv)>1 else "list"
    a = sys.argv[2:]
    if cmd=="list": cmd_list()
    elif cmd=="setparam": cmd_setparam(a[0], a[1], a[2])
    elif cmd=="readparam": cmd_readparam(a[0], a[1])
    elif cmd=="copy": cmd_copy(a[0], a[1] if len(a)>1 else None)
    elif cmd=="enable": cmd_enable(a[0], a[1] if len(a)>1 else None)
    else: print("unknown command:", cmd)
