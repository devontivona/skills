# Flight-research — report template & schema

Every completed search publishes ONE report to `flights.waywardlane.com`. Keep the shape FIXED
across searches — that consistency is exactly what Devon asked for (skim any report the same way,
compare searches over time). This file is the SINGLE SOURCE OF TRUTH for the report shape.

- Write one JSON file per search to `~/.sunny/data/sites/flights/data/reports/<slug>.json`
  (slug = short kebab-case of route + month, e.g. `sfo-tokyo-nov2026`).
- The site server reads the directory fresh per request — no rebuild/restart after writing a
  report (only `devbox restart flights` if you edit `server.js`).
- Confirm live: `curl -sI https://flights.waywardlane.com/report/<slug>`, check the index lists
  it, then send Devon the direct report URL.
- A full worked example ships at `assets/example-report.json` (also live on the site as
  `sfo-tokyo-nov2026`). Read it for the exact expected shape.

## What the report page renders

1. **Header / hero** — title + route summary + status.
2. **Recommendation first** — the final call and its reasoning, up top (lead with the
   conclusion).
3. **Search parameters** — routes, dates/window searched, travelers, cabins, markets tried.
4. **Source comparison table** — Google Flights / Ignav / Seats.aero side by side; cheapest CASH
   per cabin highlighted; the Seats.aero row clearly marked AWARD (points), not cash.
5. **Market-arbitrage summary** — only if run (which markets, whether it moved price).
6. **Date-matrix summary** — only if run (best date-pair + the swept grid).
7. **Open-jaw comparison** — only when relevant (open-jaw vs the round-trip baseline, both shown).
8. **Hub-hacking section** — only when relevant; the $1,000 business-class threshold note and the
   risk caveats are ALWAYS visible, never collapsed/hidden.
9. **Hidden-city note** — a short line (usually "not applicable / not recommended" with the risk).

Missing/optional sections render as omitted, not blank placeholders — a partial report is fine.

## On-disk JSON schema (one file per report)

```json
{
  "id": "kebab-slug",
  "created": "ISO date",
  "updated": "ISO date",
  "status": "complete | in_progress",
  "title": "string — human title shown in the hero",
  "route_summary": "string — e.g. 'SFO ⇄ NRT · round-trip'",
  "example_notice": "string or omit — a banner flag; used only by the baked-in example",

  "search_params": [ { "label": "string", "value": "string" } ],

  "recommendation": "string — the final call. Multi-paragraph (blank line between paragraphs).",
  "recommendation_reasoning": "string — why. Multi-paragraph.",

  "source_comparison": [
    { "source": "Google Flights | Ignav | Seats.aero",
      "kind": "cash | award",
      "cabin": "string — e.g. 'Business (per seat)'",
      "headline": "string — price or 'NNN,NNN mi + $tax' for award",
      "carrier": "string",
      "detail": "string — market, nonstop/stops, fare status, etc.",
      "cheapest": true }
  ],
  "cheapest_note": "string — clarifies that highlight = cheapest CASH, award row is not like-for-like",

  "market_arbitrage": {
    "ran": true,
    "summary": "string",
    "rows": [ { "market": "US", "cabin": "Business", "source": "Ignav", "price": "$4,180", "note": "USD" } ]
  },

  "date_matrix": {
    "ran": true,
    "summary": "string",
    "best_pair": "string",
    "rows": [ { "depart": "Nov 21 (Sat)", "return": "Dec 1 (Tue)", "price": "$690 econ", "note": "cheapest" } ]
  },

  "open_jaw": {
    "relevant": true,
    "summary": "string",
    "roundtrip_baseline": "string",
    "openjaw_option": "string"
  },

  "hub_hacking": {
    "relevant": true,
    "recommended": false,
    "summary": "string",
    "threshold_note": "string — restate the $1,000 business-class rule and whether it's met",
    "risk_caveats": [ "string", "string" ]
  },

  "hidden_city_note": "string — usually 'not applicable / not recommended' + the risk, or omit",

  "sources_used": [ "string" ],
  "footer_note": "string — 'prices point-in-time, re-verify before booking'"
}
```

### Rendering notes (mirrors the decisions site)

- Long-form fields (`recommendation`, `recommendation_reasoning`, section `summary`s) should be
  written as 2–4 SHORT paragraphs separated by a blank line (`\n\n` in the JSON string). The
  server splits on blank lines and renders each as its own `<p>` — one unbroken block renders as
  a wall of text.
- `market_arbitrage`, `date_matrix`, `open_jaw`, `hub_hacking` are each rendered ONLY when
  present and (where applicable) `ran`/`relevant` is truthy. Omit the whole key when a step
  wasn't run — the section disappears cleanly.
- In `source_comparison`, set `cheapest: true` on the cheapest CASH row per cabin; award rows
  (`kind: "award"`) get an "Award / points" tag and are never marked cheapest (not like-for-like).
