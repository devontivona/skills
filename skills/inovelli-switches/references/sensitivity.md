# mmWave sensitivity vs reflection — tuning guidance

(From the Inovelli "Understanding the tradeoff between mmWave sensitivity and reflection"
article; enrich verbatim once the docs digest lands.)

Core idea: mmWave radar bounces off surfaces. **Higher sensitivity** lets the switch detect
smaller/slower/farther motion (good: reliable presence while sitting still) but also picks up
**reflections and spurious motion** (bad: false "occupied" from HVAC airflow, ceiling fans,
reflective surfaces, motion in an adjacent room / hallway).

Symptoms:
- **Too HIGH sensitivity:** light stays on when the room is empty; triggers from a fan, a
  passing person in the hall, curtains, or reflective countertops/appliances.
- **Too LOW sensitivity:** light turns off while someone is sitting still (reading, watching
  TV) because subtle motion isn't detected.

Tuning approach:
1. Start mid-range, then adjust in small steps, testing the actual failure mode.
2. Prefer to **shrink the detection geometry** (height/width/depth params 101–106, or the
   room-size preset 117) to exclude reflective/adjacent-room sources rather than cranking
   sensitivity down globally.
3. Reflective/metallic surfaces and airflow are the usual culprits for false triggers —
   aim the zone away from them.
4. Combine with `mmWave Stay Life` (108) / detection timeout (114) so brief dropouts don't
   flip the light.

<!-- TODO(sunny): replace with the article's exact wording/recommended step values. -->
