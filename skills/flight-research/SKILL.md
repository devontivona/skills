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

## Delegate this — don't run it in the main conversation

This process is long (dozens of browser/API queries across 3 sources, multiple strategies,
flightdb writes, then ranking) and does not need Devon's live input once intake is done — it's
exactly the "bounded or long-running work" the **delegation skill** (`skill:delegation`) exists
for. Once intake (below) is answered, hand the whole Step 1 → Step 2 → Step 3 process to a
subagent via `delegate_task` rather than grinding through it in the main thread: give the child
the full intake answers, this skill's path, and the flightdb path, and have it report back with
the finished Step 3 message. Don't run the search inline — it will hold the conversation hostage
and risks the turn cap.

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

Searches are run as a **funnel to a shortlist** — not a flat cross-product of every technique ×
every date × every market (that explodes combinatorially and most of it is redundant), and not a
funnel to a single winning date either (that silently assumes the cheapest date for baseline
round-trip pricing is also cheapest for every other technique — not a safe assumption).

**The shortlist size is NOT one-size-fits-all — it depends on how correlated a strategy's
date-sensitivity actually is with the baseline's:**

- **Market-arbitrage transfers well — keep its shortlist narrow (2-3 dates).** It reprices the
  SAME flights the baseline already found, just at a different point of sale. The demand curve
  that made a date cheap doesn't change by currency, so the baseline's cheap dates are a good bet
  here too. **Run one probe date first** before committing to the full 2-3-date shortlist — if
  the probe shows the arbitrage is a dead end (e.g. `&gl=XX` returns the same price as `&gl=US`,
  or a market param produces no real delta after FX), stop there and log it as a null result
  rather than burning the full shortlist confirming a foregone conclusion.
- **Open-jaw and hub-hack transfer poorly — widen their shortlist to 5-6 dates.** Both involve
  genuinely different flights than the baseline (a different return city for open-jaw; two
  separate tickets with independent pricing for hub-hack), each with their own day-of-week
  demand curve that has no reason to agree with the baseline's. For hub-hack specifically, run a
  **cheap feasibility check first**: is a plausible positioning-leg saving even in the ballpark
  of the $1,000-business threshold, roughly, before spending 5-6 real queries confirming it in
  detail? If the origin is already close to the major hubs (e.g. no long detour needed), the
  math is often foregone — skip straight to logging that as a non-viable strategy instead of
  running it out.
- **Award availability (Seats.aero) transfers worst of all — widen it to 5-6 dates too, treat it
  as close to independent of cash pricing.** Award space isn't demand-curve pricing, it's
  inventory release, which is lumpy and largely uncorrelated with cash fares. A date that's
  expensive in cash can have wide-open saver awards and vice versa — reusing a narrow cash-based
  shortlist here risks missing real award space for no good reason.

This keeps the strategies that genuinely need more coverage covered, without re-introducing the
blowup by widening every strategy uniformly. Total query count for a full comprehensive search
lands roughly in the ~35-55 range depending on which strategies actually apply to the trip.

**Which date axis is actually flexible matters — don't assume both legs are equally free.** A
deadline-driven trip (arrive-by constraint + a fixed stay-length range) often collapses the
OUTBOUND date to just 2-3 legal days while leaving the RETURN date genuinely open across the
whole stay-length window. In that shape, sweep the axis that's actually free (return dates) and
hold the constrained axis (outbound dates) to its legal set — don't spread sweep effort evenly
across both axes by default; check which one the intake constraints actually leave open.

**0. Create the search in flightdb first.**
```bash
python3 ~/.sunny/data/projects/flightdb/flightdb.py search create \
  --id <slug> --title "<route + month>" \
  --params '{"cabin":"business","max_stops":1,"adults":2,"price_unit":"per_person",...}'
```
Store every intake answer in `--params` — it's the audit trail for what was actually asked for.
Always include `price_unit` (almost always `"per_person"` — confirm per source, since Ignav
returns a total for the passenger count while Google Flights varies) so every query/result
logged against this search agrees on the unit; mixing per-person and total-for-N rows without
recording which is which breaks comparisons and dedup.

**1. Baseline strategy — one fixed date pair (or the stated exact dates), all 3 sources.**
This seeds the funnel and is the reference every other strategy is compared against. Always run
this one. Log each source hit as a `query`, log every itinerary it returns as a `result`.

**2. Flex-date-sweep strategy — only if dates are flexible, and only with real result-list
searches.** Do NOT use Google Flights' calendar/price-graph view for this — it shows a per-day
price NUMBER with no actual bookable itinerary behind it, which is useless for a `result` row
(no airline, no stops, no times — nothing to rank or book). Instead, run a bounded set of
**real** date-pair searches (~8-10 pairs spread across the window, not every combination) against
Google Flights (and Ignav if the window is small enough to be worth it), each logged as its own
`query` with its own `result` rows. The strategy's job is to rank all the real date pairs tried
by price — the shortlist each downstream strategy draws from (2-3 or 5-6, per the split above)
comes out of this one ranked list.

**Every query on a search with a real arrival deadline must set `--arrival <date>`** (the
destination-local landing date, which can be a day or two after `--depart` on a long-haul or
dateline-crossing route) — this is what lets Step 2's `--arrive-by` filter actually enforce the
deadline in code, instead of you checking it by eye per row. Skipping this on even a few queries
means those rows silently bypass the deadline check (flightdb warns when this happens, but don't
rely on the warning catching it after the fact — set `--arrival` as you go).

**If the trip needs more than one cabin (e.g. 2 economy + 2 business), log EVERY query with its
actual `--cabin`** — don't run economy-only queries and assume business scales the same way; the
two cabins have different fares, different stop patterns, and sometimes different award
availability entirely. Step 2's `export --per-cabin` handles combining them at ranking time; your
job here is just to make sure both cabins are actually represented in the logged queries/results.

**3. Everything after this runs against the appropriate shortlist from step 2** (or the fixed
dates from step 1 if there was no sweep) — not against every date pair originally tried:
   - **Market-arbitrage strategy (international routes).** Re-run the top 2-3 shortlisted date
     pairs via Google Flights `&gl=XX` and Ignav's `market` param for 2 country markets
     (departure + destination). Ask before a 3rd market.
   - **Open-jaw strategy (if warranted).** Compare open-jaw (into A, out of B) against the
     round-trip-into-one-gateway baseline, for the top 5-6 shortlisted date pairs — wider than
     market-arbitrage's shortlist, since it's a different set of flights with its own pricing
     pattern.
   - **Hub-hack strategy (when a positioning leg could plausibly beat a through-fare).**
     Calculate a positioning-leg + separate-long-haul-ticket combo for the top 5-6 shortlisted
     date pairs (the positioning leg has its own day-of-week pricing, independent of the
     long-haul leg's). Recommend it only when it clears the **$1,000-business-class threshold**
     (see `references/methodology.md` for the full risk caveats — no through-checked bags, no
     rebooking protection, buffer-time table). Below threshold, it can still be logged as a
     result, just never recommended.
   - **Seats.aero award cross-check.** Run whenever a business/first cash fare is in play, across
     the top 5-6 shortlisted date pairs — award inventory release is lumpy and largely
     independent of cash pricing, so it gets the wider shortlist too, not the narrow one. When
     logging a one-way award result (common — award availability is often asymmetric), note that
     it will NOT compete against round-trip cash fares at ranking time by default (see Step 2)
     — that's intentional, not a bug to work around.

Log every query and every result via flightdb as you go:
```bash
python3 flightdb.py strategy add --search <slug> --name flex-date-sweep --description "..."
python3 flightdb.py query add --strategy <id> --source google_flights --origin PDX \
  --destination AKL --depart 2026-11-21 --return 2026-12-06 --arrival 2026-11-23 \
  --cabin business --adults 2 --max-stops 1
python3 flightdb.py result add --query <id> --json '[{...}, {...}]'
```

Hidden-city / throwaway ticketing is not part of this funnel — rarely used, high account risk,
low value for how often it actually applies. If Devon explicitly asks about the technique, treat
it as a one-off question, not a standing strategy.

## Step 2 — rank the options (deterministic, code does it — not judgment)

flightdb's `rank`/`export` commands implement this as a **simple, deterministic Python
algorithm** — filter, dedupe, sort — driven entirely by the search's stored params. Use it as-is;
don't re-derive ranking logic by eye.

**Single-cabin search:**
```bash
python3 ~/.sunny/data/projects/flightdb/flightdb.py export --search <slug> \
  --cabin business --max-stops 1 --arrive-by 2026-11-24 --depart-after 2026-11-20 \
  --points-rate 1.4 --limit 20
```

**Mixed-cabin search (e.g. 2 economy + 2 business) — use `--per-cabin`, not two separate
`--cabin` calls you sum by hand:**
```bash
python3 ~/.sunny/data/projects/flightdb/flightdb.py export --search <slug> \
  --per-cabin economy,business --max-stops 1 --arrive-by 2026-11-24 \
  --points-rate 1.4 --limit 20
```
This runs the full pipeline once per cabin and returns a `combined_top_pick_total` (each cabin's
#1 price, summed) — check the returned `price_scope` on each row before treating that total as
final, since it's a sum of per-person figures, not automatically multiplied by traveler count.

What the pipeline does, in order (see the flightdb README for the exact mechanics):
1. **Hard-constraint filter first.** Drops any result violating a stated non-negotiable: wrong
   cabin for a required-cabin traveler, stops over the max, misses `--arrive-by` (only enforced
   on queries that actually logged an `--arrival` date — see Step 1's note), earlier than
   `--depart-after`, or wrong `--leg-scope`. Filtered rows never appear downstream — not even
   greyed out. The filtered-out count is retained (`ranking.filtered_out_count`) so the omission
   stays visible as a number, never silent.
2. **Leg-scope filter (default: round-trip only).** A bare one-way fare or award does NOT compete
   against a complete round-trip itinerary by default — they answer different questions, and a
   cheap one-way shouldn't silently become "the recommendation" for a round-trip search. Only
   pass `--leg-scope one_way` or `--leg-scope any` when that's genuinely what you want ranked
   (e.g. summing two one-ways for an open-jaw comparison).
3. **Dedup.** Collapses repeat finds of the same itinerary surfaced by overlapping queries
   (`dedup_key`), so a rank position is one distinct itinerary, not a repeat.
4. **Adjusted price.** Cash rows use the total price as-is. Award rows convert points to a
   cash-equivalent using a stated, visible rate — default 1.4¢/point for business-class
   redemptions (a rule of thumb, cite it as such — e.g. The Points Guy's monthly valuations).
   Always show the conversion string (`"88,000 mi × 1.4¢ = $1,232 + $240 tax = $1,472"`), never
   hide it. Confirm every row's `price_scope` (per-person vs a group total) before comparing
   across sources — flightdb records this per result, but a source that returns a group total
   needs it set explicitly at `result add` time (see Step 1).
5. **Sort ascending by adjusted price.** Cash and award rows land on one sortable ranking because
   step 4 already put them in comparable dollars.
6. **Same inputs → same output, every time.** This is the whole point of pushing ranking into
   code instead of doing it by eye — a re-run against unchanged data reproduces the same order.

`export`'s JSON is what step 3 (below) reads to build Devon's message. Don't hand-modify its
ranking — if the ranking feels wrong, fix the underlying data (a wrong stop count, a
miscategorized cabin, a missing `--arrival` date) or the params, not the ordering.

## Step 3 — present the options: message Devon

The deliverable is an iMessage, structured as:

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
  fare-calendar tool list, market-arbitrage mechanics, business-cabin tactics.
- `~/.sunny/data/projects/flightdb/README.md` — the full schema + CLI reference for every
  command referenced above.

## Don'ts

- Don't do a quick single-source lookup unless Devon explicitly asked for "quick"/"just one thing."
- Don't assume cabin class or stop tolerance — ask per traveler / every search.
- Don't use Google Flights' calendar/price-graph view for the date sweep — it has no real
  itinerary behind its numbers. Run real date-pair searches instead.
- Don't cross-multiply every strategy against every date pair or market — funnel to a shortlist
  (Step 1). Keep market-arbitrage's shortlist narrow (2-3 dates, since it reprices the same
  flights the baseline already found); widen open-jaw's, hub-hack's, and the award
  cross-check's shortlists to 5-6 dates each, since those don't inherit the baseline's pricing
  pattern.
- Don't rank by eye — use `flightdb export`/`rank`; if the order looks wrong, fix the data/params
  feeding it, not the algorithm's output.
- Don't let a one-way fare/award compete against round-trip itineraries — `rank`/`export` default
  to `--leg-scope round_trip` for exactly this reason; only widen it deliberately.
- Don't run two separate `--cabin` export calls and sum them by hand for a mixed-cabin trip — use
  `--per-cabin`.
- Don't claim an arrival deadline is enforced unless every relevant query logged `--arrival` and
  you passed `--arrive-by` at ranking time — check for `warning_no_arrival_date` in the output.
- Don't hide the points→cash valuation — always show the per-point rate and the conversion math.
- Don't recommend a positioning flight unless business-class savings exceed $1,000; always name
  the risk caveats regardless of recommendation.
- Don't run hidden-city/throwaway as a standing strategy.
- Don't publish an HTML report — message Devon per Step 3.
- Don't invent loyalty program logic or a seat-quality note without a cited source — a
  seat-quality note, if included, needs a real citation or it's omitted.
