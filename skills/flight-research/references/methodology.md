# Flight-research — methodology reference

Deeper technique detail behind the `flight-research` SKILL.md workflow. Read when a search needs
the mechanics, not just the step order. Condensed and adapted from the flight-hacking research
report; sources cited inline so any claim is traceable.

---

## 1. Open-jaw / multi-city routing

**What:** fly into city A, out of city B (or a genuine multi-city itinerary) instead of a
round-trip through one gateway. Wins when (a) the trip genuinely has >1 destination (fly into
Rome, out of Athens after a land tour — one open-jaw beats two one-ways AND beats backtracking to
one gateway), or (b) outbound and return gateway cities carry asymmetric fare levels.

**Tooling / how to run it here:**
- **Google Flights native multi-city** search supports true open-jaw. NOTE the installed
  `google-flights` skill's URL `?q=` fast-path explicitly **fails** for multi-city — use its
  interactive form-fill fallback for open-jaw.
- **ITA Matrix** (matrix.itasoftware.com) — the classic power-user tool for open-jaw + advanced
  routing codes Google Flights' UI can't express. Reach for it when a routing is fiddly.
- **Ignav has no multi-city endpoint** (only one-way + round-trip). Open-jaw via Ignav = sum two
  one-way calls (A→B, C→D) and compare to the round-trip number — a numeric cross-check only.
- Duffel *does* support native multi-city, but Duffel isn't wired into this skill (business/KYC
  gate — see the source notes).

Always present open-jaw **against** the round-trip-into-one-gateway baseline, both numbers shown.

## 2. Hub-hacking / self-connecting (separate positioning ticket)

**What:** book a domestic (or short) positioning leg to a major hub as its OWN ticket, then the
long-haul from that hub as a SECOND independent ticket — instead of one through-fare. Can be far
cheaper (bundled connections are often priced worse than the sum of two one-ways), unlocks a
hub-only deal/mistake fare, or buys a free stopover.

**Devon's explicit rule — the $1,000-business-class positioning-flight rule:** only RECOMMEND a
positioning/separate-ticket play when the savings exceed **$1,000 for a business-class ticket**.
Below that, the separate-ticket risk isn't worth it (you may still mention it as a
not-recommended option). State this threshold as the named rule in any report where hub-hacking
appears.

**Risk caveats (ALWAYS attach — never hide these in a report):**
- **No through-checked baggage** — reclaim and recheck between tickets.
- **No airline rebooking protection across tickets.** Per The Points Guy: on one reservation the
  airline must rebook you free if you misconnect; "when you book two separate itineraries, your
  airlines have no responsibility to help out if you misconnect." Miss leg 2 because leg 1 was
  late → you may buy a new ticket outright.
- **Must re-clear security** (and possibly immigration/customs internationally) — budget real
  time, not just the flight-to-flight gap.

**Buffer-time rule of thumb (per TPG's positioning-flights guide):**

| Positioning-leg type | Minimum buffer before the onward long-haul |
|---|---|
| Domestic, mainline carrier, same-day | 4–6+ hours same-day |
| International connection needing re-clear | more than domestic; lean toward an overnight |
| Any high-value itinerary (premium cabin / mistake fare) | overnight — arrive the day before |
| **Low-cost-carrier positioning leg** | **the largest buffer — often arrive a day or two early**; TPG explicitly warns against LCC positioning legs "unless you have plenty of flexibility" |

Kiwi.com's "virtual interlining" is this same self-connect pattern sold as a product, with a
compensating "Kiwi.com Guarantee" (disruption protection as credit/rebooking) — a materially
different risk profile from a DIY self-connect with zero protection. (Not wired as a source here;
noted for context.)

Source: The Points Guy, "How to Find and Book Airport Positioning Flights"
(thepointsguy.com/guide/positioning-flights/).

## 2b. Stop tolerance as a hard constraint (max stops per leg)

Max acceptable stops per leg is a REQUIRED intake question (see SKILL.md intake) and becomes a
**hard constraint** in the ranked field: any itinerary whose stops exceed the stated max is
filtered out BEFORE ranking and never appears in the table.

Why it's asked every time, never defaulted: stop tolerance is trip-specific (a business day-trip,
a leisure trip, and travel with a toddler answer differently), and on long-haul international
routes it is one of the biggest price levers there is. Demanding nonstop on a route like
PDX/SFO→New Zealand or the US→much of Asia can eliminate the cheapest fares outright; allowing
1–2 stops routinely saves hundreds to well over $1,000 in business, and frequently unlocks the
best AWARD space too (partner award seats often exist on the 1-stop routing when the nonstop is
blocked). Conversely, on a short domestic hop nonstop-only costs little. So: always ask, apply
the answer as the filter, and if Devon is unsure, name the savings tradeoff and let him choose.

## 3. Fare calendar / flexible-date matrix search

**What:** search a grid of departure-date × return-date pairs instead of one fixed pair. The
cheapest pair is very often NOT the one the traveler guesses first. This is the date-matrix
sweep the skill runs whenever dates are flexible.

**Tools:**
- **Google Flights calendar / price-graph** — built-in, free, price-trend graph + date grid.
  Default recommendation.
- **ITA Matrix** — flexible-date + routing-code power tool.
- **Skyscanner "Whole month" / "Cheapest month"** — month-at-a-glance when dates are wide open.
- **Kayak Explore** — similar grid, coarser than Google Flights.
- None of Ignav / Duffel / Skiplagged / Kiwi expose a native date-matrix endpoint — matrix search
  on those = fire N individual date-pair queries and compare (which is exactly what the skill
  does with Ignav across a handful of candidate pairs).

## 4. Country / market pricing arbitrage

Same route/date genuinely prices differently by which country storefront you search:
- **Google Flights `&gl=XX`** — set the market via ISO country code. Also a currency selector in
  its top-left menu. God Save the Points: "for some [flights] you'll actually find real
  savings… Norwegian Airlines is a prime example… Same for flights within Asia."
- **Ignav `market` param** — 2-letter ISO code, 80 markets; sets currency + locale AND affects
  which booking providers/fare rules appear. Programmatic arbitrage, stronger on this axis than
  most APIs.
- **Workflow:** departure-country market first, then destination-country market, then ASK Devon
  before a 3rd/VPN market. (Duffel/SerpAPI don't support market selection — a known blind spot,
  irrelevant here since neither is wired.)

## 5. Business / premium-cabin tactics

- **Positioning to catch a cheaper business fare ex-a-different-city.** European (and some ME/Asia)
  origins to long-haul destinations are routinely priced far below the reverse in business.
  God Save the Points' concrete case: "Emirates has €1500 business class deals from Milan to New
  York, which is almost 3× cheaper than New York to Milan." Tactic: buy a cheap positioning fare
  INTO the favorable city, then the discounted business fare FROM there — eating one extra one-way
  to reset. (godsavethepoints.com/flight-deal-savings-concepts/)
- **Points/miles frequently crush cash on premium cabins** (2–5× cash-per-mile value). This is
  the Seats.aero cross-check's whole reason for existing: run cash as primary, surface award
  space as a secondary "much better points option?" signal whenever a real business/first cash
  fare returns — especially for Devon's transferable-points-eligible, 2-international-business-seat
  profile.
- **Mistake/error fares** are real in business class but are caught via alert services
  (Going/Scott's Cheap Flights, Thrifty Traveler, Secret Flying), NOT on-demand API search. Worth
  a one-line mention that monitoring services exist; not buildable as an on-demand search here.

## 6. Hidden-city & throwaway ticketing — LEGAL/POLICY RISK (flag every time)

- **Hidden-city:** book a longer published fare and skip the final connecting segment, because
  carriers sometimes price a longer routing below the shorter nonstop in premium cabins (thinner
  O&D competition on the nonstop). TPG's worked case: "business class from LA to New York is
  expensive, but business class from LA to Puerto Rico via New York, less so."
- **Throwaway:** buy intending to skip a leg (usually the last), e.g. leaving from an inconvenient
  city and transiting your real home city.
- **The caveats to ALWAYS attach:** this violates the contract of carriage of virtually every
  major airline. Real consequences that have happened: the airline **voids the remainder of the
  ticket the moment a segment is skipped** (so it ONLY works one-way or as the LAST segment —
  never mid-trip, never on a round-trip); airlines have pursued frequent-flyer **account bans and
  retroactive fare-difference billing** for pattern use (Lufthansa sued a customer; AA and United
  have both pursued account clawbacks). **No checked bags** (they route to the ticketed final
  destination, not your real stop). Present with the risk explicit; never as a default
  recommendation. Skiplagged is the consumer product for this — note it's an unofficial/scrape
  source, not a sanctioned API, if it ever comes up.

## Source availability (accurate, for reference)

Only three sources are actually wired into this skill: **Google Flights** (installed skill,
accurate/trusted, Southwest + `&gl=` market), **Ignav** (`skill:ignav`, cash cross-check, young —
spot-check), and **Seats.aero** (`skill:seats-aero`, award/points only). Duffel (business/KYC
gate), Skiplagged (no sanctioned public API), Kiwi Tequila (current terms unverified), and Amadeus
self-service (historically individual-friendly but unverified this cycle) are NOT built here — do
not imply they are. Do not repeat the installed `flight-search-strategy` skill's "zero config for
all" framing.
