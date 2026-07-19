---
name: flight-research
description: "Comprehensive multi-source flight search for Devon. Use for ANY flight search request (unless he asks for a quick single lookup): runs a funnel of search strategies across Google Flights, Ignav, and Seats.aero, stores every result in the flightdb SQLite database, ranks deterministically, and messages Devon a recommendation + alternatives + a search-scale summary. Keywords: flights, airfare, book a flight, cheapest flight, business class, open-jaw, positioning flight, hub hacking, award availability, miles, fare calendar, flightdb."
---

# Flight-research — the comprehensive search process

This is what Sunny reaches for whenever Devon asks about finding, comparing, or booking a
flight. **Default to the full comprehensive process below — never a quick single-source
lookup — UNLESS Devon explicitly asks for a "quick" check or "just look at one thing."**

Tell Devon up front a full search takes a bit (multiple sources, possibly a date sweep), so he
knows it's not an instant reply.

## Glossary — use these terms consistently, everywhere

- **Search** — the whole flight-research project for one trip, e.g. "PDX→Auckland Nov 2026." One
  row in flightdb's `searches` table.
- **Strategy** — a named search *technique*: `baseline`, `flex-date-sweep`, `market-arbitrage`,
  `open-jaw`, `hub-hack`. Describes the "how" of one angle of attack.
- **Query** — *one actual search execution* against *one source*: a specific origin/destination,
  date(s), cabin, passenger count, run at some point in time. A strategy is carried out via one
  or more queries.
- **Result** — *one bookable itinerary* a query returned (outbound+return or one-way, with
  price/airline/stops/duration). One query can return many results.
- **Source** — the data provider a query hit: Google Flights, Ignav, or Seats.aero. Not a
  ranking axis of its own — see the ranking algorithm below.

`search → strategy → query → result`, nested. This is flightdb's actual schema
(`~/.sunny/data/projects/flightdb/`) — read its README for the full column reference.

## Sources

Three sources are wired:

1. **Google Flights** (`google-flights` skill, agent-browser). Cash baseline, only source for
   Southwest, has the `&gl=XX` market lever. Its URL fast-path fails for multi-city/premium
   economy — use its interactive fallback for those.
2. **Ignav** (`skill:ignav`). Second cash source: explicit `cabin_class`, multi-passenger,
   `market` currency/locale arbitrage. A young API — spot-check a quoted price against Google
   Flights and flag a lone outlier.
3. **Seats.aero** (`skill:seats-aero`). Points/award availability only, never cash. The
   business/first cross-check layer.

Duffel, Skiplagged, and Kiwi are NOT wired here (business/KYC gate, no sanctioned public API,
unverified terms respectively) — don't imply otherwise.

## Intake — ask only what isn't already given

Batch ~3 questions per iMessage turn. Ask for whatever's missing:

- **Origin(s) / destination(s) or region.**
- **Dates: exact vs a window.** A flexible window triggers the flex-date-sweep strategy below.
- **Cabin class PER traveler.** Always ask explicitly; never assume. When business is a stated
  hard requirement for a traveler, treat it as one — don't quietly suggest premium economy as a
  "saving" unless asked to compare that.
- **Number of travelers.**
- **Max acceptable stops per leg (0 = nonstop only / 1 / 2+).** Always ask, every search — never
  default. This is a HARD CONSTRAINT at ranking time: itineraries exceeding it are filtered out
  before ranking. On long-haul international routes this is one of the biggest price levers
  there is — nonstop-only can eliminate the cheapest fares outright, while allowing 1-2 stops
  often saves hundreds to over $1,000 in business and unlocks better award space. If Devon's
  unsure, name the tradeoff briefly and let him pick.
- **Open-jaw worth exploring?** Ask when the destination has 2+ viable gateway airports/regions.

## Step 1 — collect and store the data

This is the part that changed most. Searches are NOT a flat cross-product of every technique ×
every date × every market — that explodes combinatorially and most of it is redundant. Run it as
a **funnel**: cheap, broad steps narrow down to a winning date(when relevant), and the more
expensive/narrow techniques only run against that narrowed target. This keeps total query count
roughly bounded (~20-35 for a full comprehensive search) and makes the process repeatable.

**0. Create the search in flightdb first.**
```bash
python3 ~/.sunny/data/projects/flightdb/flightdb.py search create \
  --id <slug> --title "<route + month>" --params '{"cabin":"business","max_stops":1,"adults":2,...}'
```
Store every intake answer in `--params` — it's the audit trail for what was actually asked for.

**1. Baseline strategy — one fixed date pair (or the stated exact dates), all 3 sources.**
This seeds the funnel and is the reference every other strategy is compared against. Always run
this one. Log each source hit as a `query`, log every itinerary it returns as a `result`.

**2. Flex-date-sweep strategy — ONLY if dates are flexible, and ONLY with real result-list
searches.** Do NOT use Google Flights' calendar/price-graph view for this — it shows a per-day
price NUMBER with no actual bookable itinerary behind it, which is useless for a `result` row
(no airline, no stops, no times — nothing to rank or book). Instead, run a bounded set of
**real** date-pair searches (~6-8 pairs spread across the window, not every combination) against
Google Flights (and Ignav if the window is small enough to be worth it), each logged as its own
`query` with its own `result` rows. The strategy's job is to find the 1-2 *actually cheapest real
date pairs* — narrow the funnel to those before continuing.

**3. Everything after this runs against the winning date pair(s) from step 2 (or the fixed dates
from step 1 if there was no sweep) — NOT against every date pair tried.** This is the answer to
"how do open-jaw / market-arbitrage combine with date sweeping": they don't cross-multiply with
it, they run ONCE against whichever date(s) the funnel has already narrowed to.
   - **Market-arbitrage strategy (international routes).** Re-run the winning date pair via
     Google Flights `&gl=XX` and Ignav's `market` param for 2 country markets (departure +
     destination). Ask before a 3rd.
   - **Open-jaw strategy (if warranted).** Compare open-jaw (into A, out of B) against the
     round-trip-into-one-gateway baseline, for the winning date(s) only.
   - **Hub-hack strategy (when a positioning leg could plausibly beat a through-fare).**
     Calculate a positioning-leg + separate-long-haul-ticket combo for the winning date(s).
     Recommend it only when it clears the **$1,000-business-class threshold** (see
     `references/methodology.md` for the full risk caveats — no through-checked bags, no
     rebooking protection, buffer-time table). Below threshold, it can still be logged as a
     result, just never recommended.
   - **Seats.aero award cross-check.** Run whenever a business/first cash fare is in play — log
     award availability for the winning date(s) as its own strategy/queries.

Log every query and every result via flightdb as you go:
```bash
python3 flightdb.py strategy add --search <slug> --name flex-date-sweep --description "..."
python3 flightdb.py query add --strategy <id> --source google_flights --origin PDX \
  --destination AKL --depart 2026-11-21 --return 2026-12-06 --cabin business --adults 2 --max-stops 1
python3 flightdb.py result add --query <id> --json '[{...}, {...}]'
```

Cut techniques (do not run these — they were removed on review):
- **Hidden-city / throwaway ticketing** — dropped. Rarely used, high account risk, low value for
  how often it actually applies. If Devon explicitly asks about it in the future, treat it as a
  one-off question, not a standing strategy in this funnel.

## Step 2 — rank the options (deterministic, code does it — not judgment)

flightdb's `rank`/`export` commands already implement this as a **simple, deterministic Python
algorithm** — filter, dedupe, sort — driven entirely by the search's stored params. Use it as-is;
don't re-derive ranking logic by eye.

```bash
python3 ~/.sunny/data/projects/flightdb/flightdb.py export --search <slug> \
  --cabin business --max-stops 1 --points-rate 1.4 --limit 20
```

What it does, in order (see the flightdb README for the exact mechanics):
1. **Hard-constraint filter first.** Drops any result violating a stated non-negotiable (wrong
   cabin for a required-cabin traveler, stops over the max, misses an arrival deadline). Filtered
   rows never appear downstream — not even greyed out. The filtered-out count is retained
   (`ranking.filtered_out_count`) so the omission stays visible as a number, never silent.
2. **Dedup.** Collapses repeat finds of the same itinerary surfaced by overlapping queries
   (`dedup_key`), so a rank position is one distinct itinerary, not a repeat.
3. **Adjusted price.** Cash rows use the total price as-is. Award rows convert points to a
   cash-equivalent using a stated, visible rate — default 1.4¢/point for business-class
   redemptions (a rule of thumb, cite it as such — e.g. The Points Guy's monthly valuations).
   Always show the conversion string (`"88,000 mi × 1.4¢ = $1,232 + $240 tax = $1,472"`), never
   hide it.
4. **Sort ascending by adjusted price.** Cash and award rows land on one sortable ranking because
   step 3 already put them in comparable dollars.
5. **Same inputs → same output, every time.** This is the whole point of pushing ranking into
   code instead of doing it by eye — a re-run against unchanged data reproduces the same order.

`export`'s JSON is what step 3 (below) reads to build Devon's message. Don't hand-modify its
ranking — if the ranking feels wrong, fix the underlying data (a wrong stop count, a
miscategorized cabin) or the params, not the ordering.

## Step 3 — present the options: message Devon, don't publish a report

**No HTML report for now** — that whole presentation layer (report site, JSON report schema,
`flights.waywardlane.com`) is on hold pending a separate design pass. The deliverable is an
iMessage.

Structure the message as:

**A. The recommendation** — the #1 ranked row (adjusted-price winner among survivors), with a
one-line reason (why it's the pick — usually just "cheapest that clears every constraint," but
say if something else makes it a clear pick, e.g. a notably shorter layover).

**B. 2-3 alternatives** — other rows worth naming, each with a concrete, specific reason to
consider it over the #1 (meaningfully better timing, existing loyalty status, sourced better
seat quality, a real price-vs-risk tradeoff on a hub-hack option). Never list an alternative with
a generic "also decent" — if there's no real edge to name, don't include it padding out to 3.

**C. Search-scale statistics** — a short numeric summary, not prose: how many sources checked,
how many strategies run, how many queries executed, how many results returned (raw, then
deduped), how many filtered out and why. Pull these straight from `flightdb search show
--json` and the `export` ranking block — don't recompute by hand.

Keep the whole message tight — this is iMessage, not a report page. A short recommendation
paragraph, a short list of alternatives, a couple lines of stats. If Devon wants the full ranked
field beyond the top handful, that's available on request via `flightdb export`/`rank` directly
— don't dump all 15-20 rows into the message by default.

## References

- `references/methodology.md` — open-jaw specifics, the hub-hacking buffer-time table,
  fare-calendar tool list, market-arbitrage mechanics, business-cabin tactics. (Its old
  hidden-city section is no longer part of the active workflow — kept only as background if
  Devon asks about the technique directly.)
- `~/.sunny/data/projects/flightdb/README.md` — the full schema + CLI reference for every
  command referenced above.

## Don'ts

- Don't do a quick single-source lookup unless Devon explicitly asked for "quick"/"just one thing."
- Don't assume cabin class or stop tolerance — ask per traveler / every search.
- Don't use Google Flights' calendar/price-graph view for the date sweep — it has no real
  itinerary behind its numbers. Run real date-pair searches instead.
- Don't cross-multiply every strategy against every date pair or market — funnel down to a
  winning date first (Step 1), then run the narrower techniques once against it.
- Don't rank by eye — use `flightdb export`/`rank`; if the order looks wrong, fix the data/params
  feeding it, not the algorithm's output.
- Don't hide the points→cash valuation — always show the per-point rate and the conversion math.
- Don't recommend a positioning flight unless business-class savings exceed $1,000; always name
  the risk caveats regardless of recommendation.
- Don't run hidden-city/throwaway as a standing strategy — it's cut from the default funnel.
- Don't publish an HTML report right now — message Devon per Step 3 instead.
- Don't invent loyalty program logic or a seat-quality note without a cited source — loyalty
  scoring is cut from this version entirely; a seat-quality note (if you have one) still needs a
  real citation or it's omitted.
