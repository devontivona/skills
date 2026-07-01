# Inovelli VZW32-SN — Z-Wave configuration parameter reference

Source of truth: Inovelli help center (Red Series mmWave Presence Dimmer parameters
article) + the zwave-js device config JSON + hands-on with Devon's fleet (2026-07).
The VZW32-SN Blue and Red mmWave dimmers share this parameter model.

> Verify a specific value/range against the live device config before relying on it for
> anything unusual — firmware revisions occasionally shift ranges. Write by NUMBER via
> `zwave_js.set_config_parameter` (works even when the HA entity is disabled).

## Core dimmer behavior
| # | Name | Range / units | Default | What it does |
|---|------|---------------|---------|--------------|
| 12 | Auto Off Timer | 0–32767 s (0 = disabled) | 0 | Turns the load off N seconds after it turns on. |
| 13 | Default Level (Local) | 0–99 (0 = restore previous) | 99 | Brightness the load goes to on a **local** paddle press. |
| 14 | Default Level (Remote) | 0–99 (0 = restore previous) | 99 | Brightness on a **hub/remote/Z-Wave** on command. |
| 15 | Level After Power Restored | 0–99 | 99 | Level after power loss. |
| 9  | Ramp Rate / Dimming speed group | see per-entity | — | Up/down local+remote ramp/dim speeds are separate params (exposed as number.* dimming/ramp entities). |
| 26 | Dimming Mode | READ-ONLY | — | **Locked by Inovelli — never write (HW damage risk).** |

## LED bar (notification / status LED)
| # | Name | Range / units | Notes |
|---|------|---------------|-------|
| 95 | Default All-LED Strip **Color When On** | 0–255 (hue) | Color of the LED bar while the load is ON. 0=red, ~85=green, ~170=blue, 255=white-ish per Inovelli hue scale. |
| 96 | Default All-LED Strip **Color When Off** | 0–255 (hue) | LED bar color while load is OFF. |
| 97 | Default All-LED Strip **Brightness When On** | 0–100 | LED bar brightness, load ON. |
| 98 | Default All-LED Strip **Brightness When Off** | 0–100 | LED bar brightness, load OFF. |
| — | Per-LED (LED1..LED7) Strip Effect color/level/duration/effect | per entity | Individual segment effects; exposed as number.*/select.* entities per LED. |

## mmWave presence
| # | Name | Range / units | Default | What it does |
|---|------|---------------|---------|--------------|
| 108 | mmWave Stay Life | 50 ms units (÷20 → seconds) | 300 (=15 s) | How long presence is "held" after the last detection before clearing. |
| 110 | **Light On Presence Behavior** (sensor→load mode) | 0–… | 1 | 0 = **manual** (sensor does NOT control the load); 1 = auto on + off; other values = auto-on-only / auto-off-only variants. Set 0 to drive lighting from HA automations instead. |
| 112 | mmWave Sensitivity | (see sensitivity article) | — | Higher = detects smaller/farther motion but more prone to reflections/false triggers. See references/sensitivity.md. |
| 113 | mmWave Target Speed | — | — | Min motion speed to register. |
| 114 | mmWave Detection Timeout | seconds | 30 | Detection window / how long before it re-evaluates presence. |
| 101 | mmWave Height Minimum (Floor) | cm | — | Detection zone geometry. |
| 102 | mmWave Height Maximum (Ceiling) | cm | — | |
| 103 | mmWave Width Minimum (Left) | cm | — | |
| 104 | mmWave Width Maximum (Right) | cm | — | |
| 105 | mmWave Depth Minimum (Near) | cm | — | |
| 106 | mmWave Depth Maximum (Far) | cm | — | |
| 117 | mmWave Room Size preset | preset | — | Coarse geometry preset. |

## Notes
- Reading a value back over MCP requires the matching `number.*` entity to be **enabled**
  (integration disables most by default). Enable via `inovelli.py enable <device_id>`.
- Config number entities read `unknown`/`None` while disabled — that's expected, not a fault.
- For presence-lighting, the reliable pattern is: param 110 = 0 (manual) + an HA automation
  on `binary_sensor.<name>_motion_detection` for on/off timing. This avoids the switch's
  built-in timeout fighting your automation.

<!-- TODO(sunny): enrich exact defaults/ranges from the Inovelli parameters article once the
     docs digest lands; some defaults above are from the zwave-js config + observed behavior. -->
