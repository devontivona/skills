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
copy of the example lives at `assets/example-report.json`). In short:

1. Write one JSON file per search to
   `~/.sunny/data/sites/flights/data/reports/<slug>.json` (slug = short kebab-case of the
   route+month, e.g. `sfo-tokyo-nov2026`).
2. The site's server reads that directory fresh per request — no rebuild/restart needed after
   writing a report file (only `devbox restart flights` if you edit `server.js` itself).
3. Confirm it's live: `curl -sI https://flights.waywardlane.com/report/<slug>` and check the
   index lists it, then send Devon the **direct report URL** (not just the index) in your reply.

The report page shows: search parameters (routes, dates/window, travelers/cabins); a
market-arbitrage summary if run; a date-matrix summary (best date-pair) if run; the source
comparison table (Google Flights / Ignav / Seats.aero side by side, cheapest highlighted); an
open-jaw comparison section when relevant; a hub-hacking section when relevant (with risk
caveats always visible); and a final recommendation with reasoning.

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
- Don't skip the date-matrix sweep when dates are flexible, or skip Seats.aero on a business search.
- Don't recommend a positioning flight unless business-class savings exceed $1,000; always show
  the separate-ticket risk caveats regardless.
- Don't present hidden-city/throwaway as a default; always attach the account/contract risk.
- Don't repeat `flight-search-strategy`'s inflated source claims — be accurate about the 3
  sources actually built (Google Flights, Ignav, Seats.aero).
- Don't finish without publishing the report and sending Devon its direct URL.
