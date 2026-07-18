---
name: flight-research
description: "Comprehensive multi-source flight search for Devon. Use for ANY flight search request (unless he asks for a quick single lookup): runs Google Flights + Ignav cash cross-check + Seats.aero award layer, market arbitrage, date-matrix sweep, open-jaw and hub-hacking comparison, and always publishes ONE standardized report to flights.waywardlane.com. Keywords: flights, airfare, book a flight, cheapest flight, business class, open-jaw, positioning flight, hub hacking, award availability, miles, fare calendar."
---

# Flight-research — the comprehensive search process

This is what Sunny reaches for whenever Devon asks about finding, comparing, or booking a
flight. **Default to the full comprehensive process below — never a quick single-source
lookup — UNLESS Devon explicitly asks for a "quick" check or "just look at one thing."** He
asked for a standardized, thorough search every time; that's the whole point of this skill.

Every completed search produces **ONE published report** on the dedicated site
(`flights.waywardlane.com`) — this is mandatory, not optional. Tell Devon the direct report URL
when you finish.

Tell Devon up front a full search takes a bit (multiple sources, possibly a date sweep), so he
knows it's not an instant reply.

## Sources (what's actually built, stated accurately)

Three working sources are wired for this skill. Be accurate about what exists — do NOT repeat
the installed `flight-search-strategy` skill's inflated "Duffel/Skiplagged/Kiwi all zero-config"
framing (per the research, Duffel needs a business/KYC gate, Skiplagged has no sanctioned public
API, Kiwi's current terms are unverified — none of those three are built here).

1. **Google Flights** — the installed `google-flights` skill (agent-browser). Fast cash
   baseline, the ONLY source for Southwest cash prices, and the `&gl=XX` market lever. Its
   econ/biz parallel-session split matches Devon's mixed-cabin need. Accurate and trusted; use
   as-is. (Its URL fast-path fails for multi-city and premium economy — use its interactive
   fallback for those.)
2. **Ignav** — `skill:ignav`. Second cash-fare source with explicit `cabin_class`,
   multi-passenger, and `market` currency/locale arbitrage. Treat as a genuine cross-check
   against Google Flights, not a fallback. It's a young product — spot-check a quoted price
   against Google Flights; flag a lone outlier, don't trust it blindly.
3. **Seats.aero** — `skill:seats-aero`. POINTS/AWARD availability only (never cash). The
   business/first cross-check layer.

## Intake — ask only what isn't already given

Batch questions ~3 per iMessage turn (SUNNY iMessage norm). Ask for whatever's missing:

- **Origin(s) / destination(s) or region** — home airport(s) and where he's going.
- **Dates: exact vs a window.** If dates are flexible, that TRIGGERS the fare-calendar /
  date-matrix sweep (see step 5) — confirm the window.
- **Cabin class PER traveler** — economy / business / mixed. **Always ask explicitly; never
  assume.** Devon's household prior is often 2 economy + 2 business for international trips, but
  that's a prior to confirm, not a rule to apply silently. When he says business is a *hard
  requirement* for certain travelers, treat it as one — do NOT quietly substitute premium
  economy as a cost-saving suggestion unless he asked to compare that.
- **Number of travelers.**
- **Max acceptable stops per leg (0 = nonstop only / 1 / 2+).** **Required — ALWAYS ask, every
  search; never assume a default.** Stop tolerance is trip-specific: a business trip, a leisure
  trip, and travel with a toddler will each answer differently, so there is no safe household
  prior to apply silently. This matters MOST on long-haul international routes: on a trip like
  PDX→New Zealand, demanding nonstop can eliminate the cheapest fares entirely, while allowing
  1–2 stops routinely saves a large amount (hundreds to well over a thousand dollars in
  business), and often unlocks the best award space too. This answer becomes a HARD CONSTRAINT
  in the ranking (see Output): itineraries exceeding the stated max are filtered out before
  ranking and never appear in the table. If Devon is unsure, briefly note the savings tradeoff
  and let him pick — don't decide for him.
- **Open-jaw worth exploring?** Ask when the destination has 2+ viable gateway airports/regions
  (multi-island or multi-city countries, land tours) — see step 6.

## The search process

Run the applicable steps. More calls is expected here — comprehensiveness is the deliverable.

1. **Google Flights baseline.** Fast cash baseline + Southwest coverage. When dates are
   flexible, use its calendar / price-graph "many dates at once" view.
2. **Ignav cash cross-check.** Cash fares with explicit `cabin_class` + `adults` + `market`.
   Cross-check its prices against Google Flights; flag divergence.
3. **Seats.aero award cross-check.** Run this **whenever a business- or first-class cash fare
   comes back — always for a business-class search.** Present award space as a secondary
   "there's a much better points option here" signal, never as a replacement for the cash
   comparison.
4. **Market arbitrage (international routes).** Try at least **2** country markets — the
   departure-country and destination-country markets — via Google Flights `&gl=XX` and Ignav's
   `market` param. **Ask Devon before trying a 3rd** market.
5. **Date-matrix sweep (if dates are flexible).** Run multiple departure×return date pairs, not
   one fixed pair — this is the comprehensive behavior Devon explicitly asked for. Don't skip it
   just because it's more calls. Report the best date-pair found.
6. **Open-jaw comparison (if warranted).** If the trip has genuine multi-destination structure,
   OR the destination country/region has 2+ viable gateway airports, explicitly compare
   **open-jaw (into A, out of B) against the round-trip-into-one-gateway baseline**, and present
   BOTH. Prefer Google Flights' native multi-city search for true open-jaw (the google-flights
   URL fast-path fails for multi-city — use its interactive fallback); Ignav has no multi-city
   endpoint, so with Ignav open-jaw means summing two one-way calls as a numeric cross-check
   only.
7. **Hub-hacking / positioning-flight option.** When a domestic positioning leg + a separate
   international ticket from a major hub could beat a direct/connected fare, calculate and
   present it as an option — but **only RECOMMEND it when the savings exceed $1,000 for a
   business-class ticket** (Devon's explicit threshold — the **$1,000-business-class
   positioning-flight rule**). Below that threshold, the separate-ticket risk isn't worth it;
   you may still mention it as a non-recommended option. ALWAYS attach the risk caveats: no
   through-checked bags, no airline rebooking protection across separate tickets, and the
   buffer-time rule (several hours same-day minimum, up to a full day+ — largest buffer for
   low-cost-carrier positioning legs). See `references/methodology.md` for the buffer-time table.
8. **Hidden-city / throwaway ticketing.** Mention as a known technique ONLY if directly
   relevant, and ALWAYS attach the contract-of-carriage / account-risk caveat (see methodology).
   Never present it as a default recommendation; never for a round-trip.
9. **Business class is often a HARD requirement.** Re-read step-8 of intake: don't downgrade a
   required-business traveler to premium economy as a "saving" unless asked.

## Output — publish ONE standardized report (mandatory)

Every completed search publishes exactly one report to the flights site. The report schema, the
JSON-on-disk shape, and a full worked example are in `references/report-template.md` (and a
copy of the example lives at `assets/example-report.json` — read it; it's a complete worked
reference, not a stub). In short:

1. Write one JSON file per search to
   `~/.sunny/data/sites/flights/data/reports/<slug>.json` (slug = short kebab-case of the
   route+month, e.g. `sfo-tokyo-nov2026`).
2. The site's server reads that directory fresh per request — no rebuild/restart needed after
   writing a report file (only `devbox restart flights` if you edit `server.js` itself).
3. Confirm it's live: `curl -sI https://flights.waywardlane.com/report/<slug>` and check the
   index lists it, then send Devon the **direct report URL** (not just the index) in your reply.

### The report shape — the ranked field is the primary artifact

The report leads with the recommendation and then a **full ranked table of every real
contender** — that table is the centerpiece, not a top-line verdict with the evidence buried
below. **The recommendation is explicitly "the top row of the table," not a separately-derived
claim.** The point (Devon's own): if he doesn't want your #1, the report is still useful because
he can see the whole ranked field and pick a different row for an intangible reason you can't
price (airline loyalty, a better business seat, a shorter layover). Present the recommendation
as row 1 of visible data he can second-guess — never a conclusion handed down apart from the
evidence.

Order on the page: recommendation (= the highlighted top row, restated) → **ranked field**
(the table) → search parameters → source-comparison table (now supporting context) →
market-arbitrage / date-matrix / open-jaw / hub-hacking narrative sections (elaboration around
the data) → hidden-city note. The narrative sections are kept — they become supporting context
around the table, not replaced by it.

### The ranking algorithm (execute exactly — don't re-derive it)

Rank the cabin that actually has variance worth ranking (usually the premium/business cabin;
a near-commodity economy leg can stay summarized in the source table). Steps:

1. **Hard-constraint filter FIRST, before ranking.** Drop any itinerary that violates a hard
   constraint: wrong cabin for a required-cabin traveler; **stops exceeding the stated max per
   leg** (the intake answer above); misses the arrival deadline; or any other stated
   non-negotiable. **Filtered-out itineraries do NOT appear in the table at all — not even
   greyed out.** Keep the table to real contenders only. Record how many were filtered and why
   (the `ranking.filtered_out_*` fields) so the omission is visible without listing them.
2. **Adjusted total price per surviving row.** For a cash fare, adjusted price = the total
   price. For an award/points row, convert to a cash-equivalent using a **stated, VISIBLE
   valuation-per-point**: default **~1.4¢/point for business-class redemptions**. This is a
   rule of thumb (cite it as such — e.g. The Points Guy's monthly valuations,
   thepointsguy.com/guide/monthly-valuations/), NOT a market price. The exact conversion used
   MUST be shown on the report itself — per award row AND in the ranking note — never hidden as
   an internal-only calculation. Changing the assumption can change the ranking, so it's shown.
3. **Sort ascending by adjusted total price** — cheapest first. Cash and award rows sit on one
   sortable table precisely because award rows were converted in step 2.
4. **Tag every row (do NOT collapse into a hidden weighted score).** Ranking, not scoring —
   burying judgment in one opaque number is exactly what Devon rejected. Each row carries these
   fields (encoded in the JSON schema — see `references/report-template.md`):
   - `source` — Google Flights / Ignav / Seats.aero.
   - `airline` + `alliance` — carrier and its alliance.
   - `routing_type` — `standard` (round-trip) / `open-jaw` / `hub-hack` (positioning).
   - `stops` — stops per leg.
   - `duration` — total travel time.
   - `adjusted_price` (+ `adjusted_price_num` for sorting) and, for award rows,
     `raw_price` + `points_conversion` (the shown "88,000 mi × 1.4¢ = …" string).
   - `loyalty_flag` / `loyalty_tier` / `loyalty_note` — see step 5.
   - `seat_quality_note` — **only ever populated from real sourced information** (e.g. a cited
     SeatGuru / airline-published cabin spec). **Never invented or guessed.** If unknown, leave
     it null/omitted — do NOT fabricate a plausible-sounding claim. A named source is required
     whenever it's present.
5. **Loyalty flag.** Cross-reference each row's airline/alliance against Devon's known loyalty
   programs (the lookup list is baked into `references/report-template.md` so you don't
   re-discover it every search — it's derived from the 1Password "Kate & Devon" vault). Set
   `loyalty_tier: "direct"` when the carrier itself is a program Devon holds an account with
   (renders as a filled badge); `loyalty_tier: "alliance"` when he only reaches it through an
   alliance partner he holds (outline badge). Loyalty is real value the price column can't
   capture — flag it, don't price it.
6. **Show the top 15–20 rows** (configurable; default 20), cheapest-adjusted-first, with the #1
   row highlighted (`is_recommendation: true`).
7. **"Consider instead" callouts.** After the highlighted top row, if a DIFFERENT row in the
   top ~3–5 has a concrete, nameable edge — existing loyalty status, meaningfully better
   schedule/arrival time, meaningfully shorter connection, or sourced better seat quality —
   call it out as its own short callout near the top of the table (`consider_instead[]`), the
   way decision-coach surfaces disagreement instead of smoothing it over. Do NOT fold it into
   the recommendation, and do NOT manufacture a callout when there isn't a concrete edge to
   name — zero callouts is correct when the top row is strictly best.

The page still also shows: search parameters; the source-comparison table (Google Flights /
Ignav / Seats.aero side by side, cheapest cash highlighted); a market-arbitrage summary if run;
a date-matrix summary (best date-pair) if run; an open-jaw comparison when relevant; a
hub-hacking section when relevant (risk caveats always visible); and the recommendation +
reasoning up top.

## References

- `references/methodology.md` — full methodology detail: open-jaw specifics, the hub-hacking
  buffer-time table, fare-calendar tool list, market-arbitrage mechanics, business-cabin
  tactics, and the hidden-city risk writeup. Read it when a search needs the deeper technique
  detail; the SKILL.md body stays focused on the workflow.
- `references/report-template.md` — the report template + on-disk JSON schema (single source of
  truth for report shape) + the worked example.
- `assets/example-report.json` — the exact JSON of the baked-in example report (also live on the
  site as `sfo-tokyo-nov2026`) so future-Sunny can see the expected shape without a live fetch.

## Don'ts

- Don't do a quick single-source lookup unless Devon explicitly asked for "quick"/"just one thing."
- Don't assume cabin class — ask per traveler, every search.
- Don't assume a stop tolerance — ask max stops per leg every search (it's a hard constraint,
  and it's where long-haul international savings hide). Never silently default to nonstop-only.
- Don't collapse the field into one hidden weighted score, and don't hand down a recommendation
  separate from the table — the recommendation IS the top row of the visible ranked field.
- Don't invent a `seat_quality_note` — populate it only from a cited source, else leave it null.
- Don't hide the points→cash valuation — show the per-point rate on the report, every award row.
- Don't skip the date-matrix sweep when dates are flexible, or skip Seats.aero on a business search.
- Don't recommend a positioning flight unless business-class savings exceed $1,000; always show
  the separate-ticket risk caveats regardless.
- Don't present hidden-city/throwaway as a default; always attach the account/contract risk.
- Don't repeat `flight-search-strategy`'s inflated source claims — be accurate about the 3
  sources actually built (Google Flights, Ignav, Seats.aero).
- Don't finish without publishing the report and sending Devon its direct URL.
