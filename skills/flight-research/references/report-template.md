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
2. **Recommendation first** — the final call + reasoning, up top. "Recommendation" now means
   **the highlighted top row of the ranked field, restated** — not a separately-derived verdict.
3. **Ranked field (PRIMARY artifact)** — the full ranked table of every real contender, cheapest
   adjusted price first, #1 row highlighted. Above the table: a "how this field was built" panel
   (hard constraints applied + how many were filtered out) and a visible points→cash conversion
   note. "Consider instead" callouts render near the TOP of the table (not buried at the bottom).
   This is the centerpiece; everything below is supporting context. See "The ranked field" below.
4. **Search parameters** — routes, dates/window, travelers, cabins, **max stops per leg**, markets.
5. **Source comparison table** — Google Flights / Ignav / Seats.aero side by side; cheapest CASH
   per cabin highlighted; the Seats.aero row clearly marked AWARD (points), not cash. Now a
   SUPPORTING view under the ranked field (the ranked field is what merges the three sources).
6. **Market-arbitrage summary** — only if run (which markets, whether it moved price).
7. **Date-matrix summary** — only if run (best date-pair + the swept grid).
8. **Open-jaw comparison** — only when relevant (open-jaw vs the round-trip baseline, both shown).
9. **Hub-hacking section** — only when relevant; the $1,000 business-class threshold note and the
   risk caveats are ALWAYS visible, never collapsed/hidden.
10. **Hidden-city note** — a short line (usually "not applicable / not recommended" with the risk).

Missing/optional sections render as omitted, not blank placeholders — a partial report is fine.

## The ranked field (the centerpiece)

The full ranking algorithm — hard-constraint filter → adjusted price (with the ~1.4¢/point
award conversion) → ascending sort → per-row tags → loyalty flag → top 15–20 rows → "consider
instead" callouts — is specified in SKILL.md's Output section. This file is the SINGLE SOURCE OF
TRUTH for the *shape* those steps write to (the `ranking`, `ranked_itineraries`,
`consider_instead` keys in the schema below). Two things that live only here:

**Points→cash conversion (must be VISIBLE, never hidden):** award rows are converted to an
adjusted cash-equivalent at a stated per-point rate — default **~1.4¢/point for business** (a
rule of thumb; cite The Points Guy monthly valuations,
thepointsguy.com/guide/monthly-valuations/). Put the rate in `ranking.points_cents_per_point`
AND spell the math out per award row in `ranked_itineraries[].points_conversion` (e.g.
`"88,000 mi × 1.4¢ = $1,232 + $240 tax"`). The renderer shows both. Never compute this as an
internal-only number.

**Loyalty-flag lookup (baked in so it's not re-discovered every search).** Derived from the
"Kate & Devon" 1Password vault (via `credential_manage action="discover"`). These are the
airline programs Devon/Kate hold accounts with — a row's carrier matching one of these gets
`loyalty_tier: "direct"` (filled badge); a row reachable only via that program's ALLIANCE
partner gets `loyalty_tier: "alliance"` (outline badge). Re-confirm against the vault only if
the account set looks like it changed; otherwise use this list:

| Program held (vault item) | Carrier | Alliance | Alliance reach (alliance-tier matches) |
|---|---|---|---|
| United (+ United Business / Chase United Business card) | United | Star Alliance | ANA, EVA Air, Lufthansa, Singapore, Air Canada, etc. |
| Delta | Delta | SkyTeam | Korean Air, Air France, KLM, etc. |
| Alaska Airlines (Kate) | Alaska | oneworld | JAL, Cathay Pacific, Qatar, British Airways, etc. |
| British Airways (Avios) | British Airways | oneworld | JAL, Cathay, Qatar, Alaska, etc. |
| Air France (Flying Blue) | Air France / KLM | SkyTeam | Delta, Korean Air, etc. |
| Hawaiian Airlines (Katie) | Hawaiian | (Alaska/oneworld affiliation) | Alaska ecosystem |

Practical effect: because Devon holds United + Alaska + BA + Delta + Flying Blue, most Star
Alliance / oneworld / SkyTeam premium itineraries earn at least an `alliance` flag; United,
Delta, Alaska, BA, Air France/KLM, and Hawaiian metal earn the stronger `direct` flag. Flag it,
don't price it — loyalty is value the adjusted-price column deliberately can't show.

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

  "recommendation": "string — the final call = the highlighted top row, restated. Multi-paragraph (blank line between paragraphs).",
  "recommendation_reasoning": "string — why. Multi-paragraph.",

  "ranking": {
    "cash_rows": 10,
    "award_rows": 6,
    "rows_shown": 16,
    "points_cents_per_point": 1.4,
    "points_valuation_note": "string — states the ~1.4¢/point business rule of thumb, cites it as a rule of thumb (TPG monthly valuations), and says the rate is shown per row / never hidden.",
    "hard_constraints": [ "string — each hard constraint applied BEFORE ranking (cabin, max stops, arrival deadline, …)" ],
    "filtered_out_count": 7,
    "filtered_out_note": "string — N itineraries filtered out before ranking and NOT shown (not even greyed out); table is real contenders only."
  },

  "consider_instead": [
    { "row_rank": 2,
      "title": "string — the alternate's short name",
      "edge": "string — the concrete, nameable edge (loyalty / better arrival / shorter layover / sourced seat quality)",
      "body": "string — 2–4 sentences on why to pick this over row 1. Omit the whole array if there's no concrete edge to name (zero callouts is valid)." }
  ],

  "ranked_itineraries": [
    { "rank": 1,
      "source": "Google Flights | Ignav | Seats.aero",
      "kind": "cash | award",
      "cabin": "string — the cabin being ranked, e.g. 'Business'",
      "airline": "string",
      "alliance": "string — Star Alliance | oneworld | SkyTeam | (none)",
      "routing_type": "standard | open-jaw | hub-hack",
      "route": "string — e.g. 'SFO→NRT nonstop, rt' or 'SFO→HKG→NRT, rt'",
      "stops": "string — e.g. 'Nonstop' / '1 stop (TPE)' / '2 stops (DOH)'",
      "duration": "string — total travel time",
      "raw_price": "string — the as-quoted price: '$3,950 cash' or '88,000 mi + $240'",
      "points_conversion": "string or null — award only; the SHOWN math, e.g. '88,000 mi × 1.4¢ = $1,232 + $240 tax'",
      "adjusted_price": "string — the sortable adjusted total, e.g. '$1,472' (award = converted; cash = the price)",
      "adjusted_price_num": 1472,
      "loyalty_flag": true,
      "loyalty_tier": "direct | alliance",
      "loyalty_note": "string — which program (e.g. 'United MileagePlus — account + status on file')",
      "seat_quality_note": "string or null — ONLY from a cited source (SeatGuru / airline spec); null if unknown. NEVER invented.",
      "caveat": "string or omit — a per-row flag (e.g. separate-ticket risk on a hub-hack row, open-jaw premium note)",
      "is_recommendation": true }
  ],
  "ranked_note": "string — one line under the table: sorted ascending by adjusted price, award conversion shown, loyalty badge legend (filled = direct account, outline = alliance-only).",

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
- **Ranked field:** rows are rendered in array order — write them ALREADY sorted ascending by
  `adjusted_price_num`, with `rank` matching position (1-based). Exactly one row should carry
  `is_recommendation: true` (row 1); it gets the highlighted "recommendation" treatment (same
  yellow visual used elsewhere). Award rows (`kind: "award"`) render on a blue surface with an
  "Award" tag and their `points_conversion` shown inline under the adjusted price. A
  non-`standard` `routing_type` renders as a small sky-blue tag ("open-jaw"/"hub-hack"). The
  `loyalty` cell renders a filled badge for `loyalty_tier: "direct"`, an outline badge for
  `"alliance"`, nothing when `loyalty_flag` is false. `seat_quality_note` renders verbatim (with
  its source) or an em-dash when null. On viewports ≤760px the whole table collapses to stacked
  cards (each `<td>` labelled by its column) — no horizontal scroll on phones.
- **Consider-instead** callouts render as small dot-grid cards near the TOP of the ranked
  section (right after the how-built / conversion panels), each tagged with its `row_rank` and
  `edge`. Omit the `consider_instead` key entirely for zero callouts.
