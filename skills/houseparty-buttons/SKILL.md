---
name: houseparty-buttons
description: Bridge Inovelli scene/config button presses in Home Assistant to houseparty CLI actions (NTS mixtapes on Sonos) via an always-on websocket listener on janeway. Use whenever changing what a switch's config button does, adding a new button-to-music mapping, editing the favorites cycle, changing speakers/volume, or debugging the houseparty-buttons service.
---

# houseparty-buttons — Inovelli config buttons → Sonos music

Turns the programmable config button on Inovelli VZW32-SN switches into music
controls. Home Assistant (on **riker**) sees the button press; this service (on
**janeway**) reacts and runs the `houseparty` CLI locally to play/stop NTS mixtapes
on Sonos.

## Why a janeway-side listener (not HA automations)
HA can't call an HTTP/CLI endpoint on janeway without a `rest_command:`/`shell_command:`
block in `configuration.yaml` — YAML-only, needs a riker edit + HA restart, not doable via
the MCP. So instead a small always-on Python service on janeway holds a **websocket** to HA,
subscribes to `state_changed`, and shells out to `houseparty`. Zero HA-side config; all logic
lives in code here. (See topic:home-assistant for the general cross-machine note, and
skill:inovelli-switches for the scene-button mapping: scene_001=off paddle, 002=on paddle,
**003=config button**.)

## Runtime design (v2 — non-blocking + warm group)
The receive loop must NEVER block on houseparty. Button presses are pushed to an
asyncio.Queue; a single worker runs one houseparty action at a time. (v1 ran the CLI
inline and froze the websocket for the ~25s a cold 7-speaker group-form takes, so it
missed the next press and could stall.) Two more tricks:
- **Warm group:** toggle uses pause/resume (never stop), so repeat presses are ~1s
  instead of re-forming the group (~25s cold). `stop` is avoided while in use.
- **Two-stage play:** start on `primary_speaker` (~1.5s, instant feedback) then fan out
  to all speakers in the background. state.json tracks mode = idle/playing/paused so
  toggle knows whether to play / resume / pause.

## Where everything lives (janeway)
- Code + config: `~/projects/houseparty-buttons/`
  - `listener.py` — the websocket listener + button dispatch
  - `config.json` — **the file you edit** to change behavior (buttons, speakers, volume)
  - `state.json` — runtime state (playing flag, per-button cycle index); auto-managed
  - `listener.log` — rolling log
- HA token: `~/.config/houseparty-buttons/ha_token` (chmod 600; long-lived token named
  "houseparty-buttons"). Never print it.
- Service: **user systemd unit** `houseparty-buttons.service` (Restart=always, lingering
  enabled so it runs across logout/reboot).

## config.json shape
```json
{
  "ha_url": "ws://riker.local:8123/api/websocket",
  "token_file": "~/.config/houseparty-buttons/ha_token",
  "houseparty_bin": "/home/tivona/.local/bin/houseparty",
  "all_speakers": ["Bathroom Speaker","Bedroom Speaker","Kitchen Speaker","Living Room","Office","Rec Room","Sonos Move"],
  "volume": 10,
  "primary_speaker": "Kitchen Speaker",
  "frame_url": "http://CHANGE_ME:8080",
  "toast_duration_ms": 20000,
  "buttons": {
    "event.kitchen_mmwave_dimmer_scene_003":   {"label":"Kitchen Pendant config button","gesture":"KeyPressed","action":"toggle","mixtape":"poolside"},
    "event.kitchen_mmwave_dimmer_scene_003_2": {"label":"Kitchen Cabinet config button","gesture":"KeyPressed","action":"cycle","mixtapes":["poolside","slow-focus","4-to-the-floor","island-time","feelings","memory-lane","100-percent-hip-hop"]}
  }
}
```
- Key = the HA **event entity** for a switch's config button (`..._scene_003`; a duplicate
  base-name switch gets `..._scene_003_2`).
- `gesture` = which press fires it: `KeyPressed` (1x), `KeyPressed2x`..`5x`, `KeyHeldDown`.
  One physical button → up to ~6 distinct actions if you add more entries per gesture.
- `action`:
  - `toggle` — play `mixtape` on all speakers at `volume`; press again while playing → pause all.
  - `cycle` — advance through `mixtapes` one step per press, play on all speakers.
- Current setup: **all 7 speakers @ 10% ("party mode")**. Pendant = toggle `poolside`.
  Cabinet = cycle poolside → slow-focus → 4-to-the-floor → island-time → feelings →
  memory-lane → Low Key (`100-percent-hip-hop`) → loop.

- `frame_url` — base URL of the EO digital picture frame on the LAN (e.g.
  `http://10.0.0.x:8080`). When set, each new play publishes an ephemeral **toast**
  ("Now playing: <Title>") to the frame via `POST /api/toast` (see the eo repo's
  `docs/eo-api.md`). **Optional and fully fire-and-forget:** if it's missing or left at
  the placeholder `http://CHANGE_ME:8080`, or if the frame is offline/unreachable, the
  toast is skipped/logged and **music playback is never affected** (the POST runs in a
  thread with a ~3s timeout and swallows all exceptions). Must be filled in with the real
  frame address before toasts will appear.
- `toast_duration_ms` — optional override for how long the toast stays on the frame
  (ms). If absent, `listener.py` omits `durationMs` and the frame applies its own default
  (20000ms / 20s).

### How the toast works (`post_toast`)
`do_play()` runs the two-stage play (primary speaker, then fan-out) and then calls
`post_toast(cfg, "Now playing: <Title>")` **once** (not once per speaker). The title is
scraped from the primary `houseparty play` stdout (`"▶ Playing <Title> on ..."`) via
regex, falling back to the alias title-cased (hyphens → spaces) if that doesn't match.
`post_toast` uses stdlib `urllib.request` wrapped in `asyncio.to_thread` (no extra venv
dependency) so it never blocks the event loop.

## Common edits
Always: edit `config.json`, then restart the service.
```
nano ~/projects/houseparty-buttons/config.json
systemctl --user restart houseparty-buttons.service
```
- **Change the pendant's default mixtape:** edit its `mixtape`.
- **Change/reorder the cabinet cycle:** edit the `mixtapes` array (use aliases from
  `houseparty list --json`).
- **Change speakers or volume:** edit `all_speakers` / `volume`.
- **Point toasts at the frame:** set `frame_url` to the frame's real `http://<ip>:8080`
  (reserve a DHCP IP or use its mDNS `_eo._tcp` name). Optionally set `toast_duration_ms`.
- **Map a new switch's button:** add a `"event.<switch>_scene_003": {...}` entry. Find the
  entity via skill:inovelli-switches (`inovelli.py list` for the switch, then its
  `event.*_scene_003`).
- **Add a second gesture on the same button:** the listener matches on exact `gesture`, so
  add another config entry keyed to the same entity but you'll need distinct behavior — extend
  `handle_button` if you want e.g. 2x-press = different mixtape (currently one entry per entity;
  a small change to key on (entity, gesture) enables multi-gesture).

## Operate / debug the service
```
systemctl --user status houseparty-buttons.service
systemctl --user restart houseparty-buttons.service
journalctl --user -u houseparty-buttons.service -f          # live
tail -f ~/projects/houseparty-buttons/listener.log          # or the file log
```
Each press logs a line like `[Kitchen Pendant config button] toggle -> PLAY poolside`.

## Gotchas
- **Firing logic:** the listener triggers on a *new* `state` timestamp with the matching
  `event_type` gesture. It de-dupes by remembering the last timestamp per entity, so a state
  refresh with an unchanged timestamp won't double-fire.
- **`toggle` playing-state** is tracked in `state.json`, not read from Sonos. If music is
  stopped some other way (app, another button), the flag can drift — a press will just correct
  it on the next toggle. `cycle` presses always (re)start playback.
- **`pause` vs `stop`:** toggle uses `houseparty pause` (keeps the group intact for a clean
  resume). It passes all speakers so the whole group pauses.
- **websockets dep** lives in the project venv (`.venv`, uv-managed, python 3.10). Reinstall:
  `uv pip install --python ~/projects/houseparty-buttons/.venv/bin/python websockets`.
- **Token** is a long-lived HA token; if it's ever revoked, auth fails in the log — mint a new
  one (HA → profile → Security → Long-lived access tokens) and overwrite the token file.
