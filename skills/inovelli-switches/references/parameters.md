# Inovelli VZW32-SN mmWave Presence Dimmer — Z-Wave parameter reference

Verbatim from Inovelli's help center (Red Series mmWave Presence Dimmer "Parameters"
article, last updated 2026-06-19), cross-checked against the zwave-js device config and
hands-on with Devon's fleet. Blue and Red mmWave dimmers share this parameter model.
Write by NUMBER via `zwave_js.set_config_parameter` (works even when the HA entity is
disabled). Inovelli notes the table can lag firmware — verify anything unusual on-device.

## Full parameter table

| # | Name | Range | Default | Bytes |
|---|------|-------|---------|-------|
| 1 | Dimming Speed Up (Remote) | 0–254 | 25 | 1 |
| 2 | Dimming Speed Up (Local) | 0–255 | 255 | 1 |
| 3 | Ramp Rate Off→On (Remote) | 0–255 | 255 | 1 |
| 4 | Ramp Rate Off→On (Local) | 0–255 | 255 | 1 |
| 5 | Dimming Speed Down (Remote) | 0–255 | 255 | 1 |
| 6 | Dimming Speed Down (Local) | 0–255 | 255 | 1 |
| 7 | Ramp Rate On→Off (Remote) | 0–254 | 255 | 1 |
| 8 | Ramp Rate On→Off (Local) | 0–255 | 255 | 1 |
| 9 | Minimum Dim Level | 1–54 | 1 | 1 |
| 10 | Maximum Dim Level | 55–99 | 99 | 1 |
| 11 | Invert Switch | 0–1 | 0 | 1 |
| 12 | Auto-Off Timer | 0–32767 s (0=off) | 0 | 2 |
| 13 | Default Level (Local) | 0–99 (0=last state) | 0 | 1 |
| 14 | Default Level (Remote) | 0–99 (0=last state) | 0 | 1 |
| 15 | Level After Power Restored | 0–100 (0=off,100=last) | 100 | 1 |
| 17 | LED Indicator Timeout | 0–11 (0=always off,11=always on,1–10=sec) | 11 | 1 |
| 18 | Active Power Reports | 0–100 (unit 0.1 W) | 10 | 1 |
| 19 | Periodic Power & Energy Reports | 0, 30–32767 s | 3600 | 2 |
| 20 | Active Energy Reports | 0–32767 (unit 0.01 kWh) | 10 | 2 |
| 21 | AC Power Type (READ ONLY) | 0=neutral,1=non-neutral | 0 | 1 |
| 22 | Switch Type | 0=single-pole,1=multi-way dumb,2=aux,3=full sine | 0* | 1 |
| 23 | Quick Start Time | 0–60 (60ths of a sec) | 0 | 1 |
| 24 | Quick Start Level | 0–254 | 254 | 1 |
| 25 | Non-Neutral Output | 0=throttled,1=full | 0 | 1 |
| 26 | Leading/Trailing Edge | 0–1 | 0 | 1 |
| 32 | Internal Temperature Monitor (READ ONLY) | 0–127 | — | 1 |
| 33 | Overheat Protection (READ ONLY) | 0–1 | 0 | 1 |
| 50 | Button Press Delay | 0–9 (0=instant,5=500ms) | 5 | 1 |
| 52 | Smart Bulb Mode | 0=off,1=on | 0* | 1 |
| 53 | 2x Tap Up to Max | 0–1 | 0 | 1 |
| 54 | 2x Tap Down to Min | 0–1 | 0 | 1 |
| 55 | 2x Tap Up Level | 1–99 % | 99 | 1 |
| 56 | 2x Tap Down Level | 1–99 % | 1 | 1 |
| 58 | Exclusion Behavior | 0=LED off,1=pulse blue,2=disabled | 1 | 1 |
| 59 | Association Behavior | 0=off,1=local,2=hub,3=both | 1 | 1 |
| 64/69/74/79/84/89/94 | LED #1–#7 Notification (32-bit encoded) | 0–4294967295 | 0 | 4 |
| 95 | **Default All-LED Color When On** (hue) | 0–255 | **170 (Blue)** | 1 |
| 96 | **Default All-LED Color When Off** (hue) | 0–255 | **170 (Blue)** | 1 |
| 97 | **Default All-LED Brightness When On** | 0–100 % | **33** | 1 |
| 98 | **Default All-LED Brightness When Off** | 0–100 % | **1** | 1 |
| 99 | All-LED Notification (32-bit, all 7) | 0–4294967295 | 0 | 4 |
| 100 | LED Bar Scaling | 0=Gen3,1=Gen2 | 0 | 1 |
| 101 | Detection Area Min Z (floor/height) | −600…600 cm | −600 | 2 |
| 102 | Detection Area Max Z (ceiling/height) | −600…600 cm | 600 | 2 |
| 103 | Detection Area Min X (left/width) | −600…600 cm | −600 | 2 |
| 104 | Detection Area Max X (right/width) | −600…600 cm | 600 | 2 |
| 105 | Detection Area Min Y (near/depth) | −600…600 cm | 0 | 2 |
| 106 | Detection Area Max Y (far/depth) | −600…600 cm | 600 | 2 |
| 107 | mmWave Target Info Report | 0–1 | 0 | 1 |
| 108 | **mmWave Stay Life** | **0–3600 s** | **300** | 2 |
| 109 | UTC Time Range | — | — | 4 |
| 110 | **mmWave Load Behavior** | 0–6 | **1** | 1 |
| 111 | mmWave Control Command (dispatcher) | 0–255 | — | 1 |
| 112 | **mmWave Detection Sensitivity** | 0=low,1=med,2=high | **2** | 1 |
| 113 | **mmWave Trigger Speed** | 0=low(5s),1=med(1s),2=fast(0.2s) | **2** | 1 |
| 114 | **mmWave Hold Time** (off-delay) | 0–4294967295 s | **10** | 4 |
| 115 | mmWave Module FW Version (READ ONLY) | — | — | 4 |
| 116 | mmWave Reporting Area Status | 0–0x01010101 | 0 | 4 |
| 117 | Room Size Preset | 0=custom,1=XS…5=XL | 0 | — |
| 118 | Illuminance Reporting Threshold | 0–32767 | 20 | 2 |
| 119 | Illuminance Reporting Interval | 0–32767 s | 600 | 2 |
| 120 | Single Tap Handling | 0–1 | 0 | 1 |
| 123 | Aux Switch Unique Scenes | 0–1 | 0 | 1 |
| 130 | Z-Wave Assoc Device Control Enable | 0–1 | 0 | 1 |
| 131–133 | Assoc Preset Values #1/#2/#3 | 2–254 | 63/128/254 | 1 |
| 134 | Assoc Control LED Bar Color | 0–255 | 255 | 1 |
| 158 | Switch Mode | 0=dimmer,1=simulated on/off | 1 | 1 |
| 159 | One LED Mode | 0=all 7,1=bottom only | 0 | 1 |
| 160 | Firmware Update Indicator | 0–1 | 1 | 1 |
| 161 | Relay Click Sound | 0=on,1=off | 0 | 1 |
| 162 | Clear Notification via 2x Tap Config | 0–1 | 0 | 1 |

\* P22 and P52: Inovelli's table shows default 1 but the article body says 0 — treat as 0
(single-pole / smart-bulb-off) until verified on a freshly included switch.

**P26 (Leading/Trailing Edge / "Dimming Mode") is effectively locked — do not experiment;
Inovelli flags hardware-damage risk on some models.**

## mmWave: the parameters that actually matter for presence lighting

- **110 mmWave Load Behavior (default 1)** — how presence drives the load. This is the
  headline: **1 = Auto On/Off when Occupied gives you presence on AND off natively, no
  automation needed.** Full map:
  - 0 = disabled (presence does not control load)
  - 1 = Auto On/Off when Occupied  ← default, normal presence lighting
  - 2 = Auto Off when Vacant
  - 3 = Auto On when Occupied
  - 4 = Auto On/Off when Vacant
  - 5 = Auto On when Vacant
  - 6 = Auto Off when Occupied
- **114 mmWave Hold Time (seconds, default 10)** — how long the load stays on after presence
  is lost. This is the primary off-delay. (We set Devon's fleet to 600 = 10 min.)
- **108 mmWave Stay Life (seconds, 0–3600, default 300)** — how long a *motionless* person
  still counts as present. Raise this for sit-still rooms (couch, desk, bath) so the light
  doesn't drop while someone is barely moving.
- **112 Sensitivity (0/1/2, default 2=high)** and **113 Trigger Speed (0/1/2, default
  2=fast, 0.2s)** — detection tuning. See references/sensitivity.md.
- **101–106 Detection Area (cm, X/Y/Z bounding box)** — shrink these to exclude reflective
  surfaces / adjacent rooms. Most powerful tool against false triggers.
- **117 Room Size Preset** — coarse starting geometry (0 custom, 1 XS … 5 XL), then fine-tune
  101–106.

### P111 mmWave Control Command (a command dispatcher, not a stored setting)
Write a value to *do* a thing:
- 0 = Factory-reset mmWave module (clears area/timeout/speed; LED flashes red 3s)
- 1 = Generate & store Interference Area — run with the fan/HVAC ON and the room empty; maps
  static noise so it's ignored (LED pulses orange ~20–30s). Best fix for fan/HVAC false-ons.
- 2 = request interference report (reserved)
- 3 = clear stored interference area
- 4 = reset detection area (P101–P106) to defaults — must reconfigure geometry after

## Non-mmWave essentials
- **12 Auto-Off Timer** (s, 0=off), **13/14 Default Level Local/Remote** (0–99, 0=restore
  last), **15 Level After Power Restored**.
- **95/96 LED bar color when on/off** (0–255 hue: default 170=blue; use Inovelli Toolbox for
  exact hues), **97/98 LED brightness on/off** (0–100; defaults 33/1).
- Dimming/ramp speeds (1–8) encode: 1–100 → ×100ms; 101–160 → seconds; 161–254 → minutes;
  255 → mirror parent param; 0 → instant.

## HA integration reality
- Most config entities ship **disabled by the integration** (read `None`/`unknown`, hidden in
  UI). Writing by number works anyway; `inovelli.py enable <device_id>` un-hides them for
  UI editing / read-back.
