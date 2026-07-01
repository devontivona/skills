# mmWave sensitivity vs. reflection — tuning guidance

From Inovelli's "Understanding the tradeoff between mmWave sensitivity and reflection"
article, plus the basic configuration guide. This is the conceptual playbook for tuning
presence so lights don't false-trigger or drop while someone sits still.

## Core tradeoff
mmWave emits radio waves and reads reflections; it can detect micro-motion (breathing) but
also bounces off walls, glass, tile, mirrors, metal. Raising **sensitivity (P112)** does two
things at once: increases detection range AND raises the noise floor (reflections start
registering as presence). Higher sensitivity = more detection + more false positives.

## Symptoms
- **Too HIGH (P112=2):** room stays "occupied" after everyone leaves; detects people through
  walls/glass or walking past a doorway; random intermittent triggers. Worse in reflective
  rooms (mirrors, glass showers, stainless appliances, tile, narrow hallways/alcoves).
- **Too LOW (P112=0):** light drops while someone is sitting still (reading, TV, shower)
  because subtle motion isn't caught.

## Recommended tuning order
1. **Start at Medium sensitivity (P112=1)** — best balance for most rooms. Inovelli's own
   default is High (2); drop to Medium first if you see false-ons.
2. **Use High (P112=2)** for: large/open rooms, users often seated/motionless, or sensor
   mounted far from the action.
3. **Use Low/Medium** in highly reflective spaces (mirrors, glass, stainless, tile, alcoves).
4. **Shape the detection area (P101–P106)** to match real room geometry — this is the single
   most powerful tool for killing false triggers from adjacent rooms/hallways. Or start from a
   Room Size Preset (P117) and fine-tune.
5. **Calibrate interference first (P111=1)** with fans/HVAC running and the room empty — maps
   repetitive motion so it's ignored. Do this before cranking sensitivity down.
6. **Iterate** against the actual failure mode you observe.

## Physical placement
- Don't aim directly at mirrors or windows (biggest bounce-back source).
- Don't aim through doorways (raises odds of catching someone outside the room).

## For a "sit-still" room (couch / desk / TV — Kate's living-room case)
The failure mode there is the light dropping while motionless. Fixes, in order:
1. Raise **P108 mmWave Stay Life** (how long a still person counts as present; default 300s /
   5 min, up to 3600s).
2. Ensure **P112 Sensitivity** high enough to catch micro-motion (2=high for a big room).
3. Set **P114 Hold Time** to a comfortable off-delay (Devon's fleet = 600s).
4. Keep **P110 = 1** (native auto on/off) — no HA automation required. Only reach for an
   automation if you need logic the switch can't do (e.g. time-of-day behavior).
