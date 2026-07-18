---
name: seats-aero
description: "Seats.aero award/points availability API (partnerapi): award space + mileage cost + taxes per cabin (Y/W/J/F) across 25+ programs. POINTS/AWARD data only, never cash. Source sub-skill used by flight-research as the business/first award cross-check. Keywords: seats.aero, award availability, points, miles, business class award, transpacific award, transatlantic award."
---

# Seats.aero — award/points availability API (source sub-skill)

Seats.aero returns **award (points/miles) availability** — which mileage programs have seats
open on a route/date range, the mileage cost, and the cash taxes, broken out per cabin
(Y = economy, W = premium economy, J = business, F = first). It is the POINTS layer of the
`flight-research` workflow.

**This is award data ONLY — never cash fares.** Its correct role is a *secondary* signal:
whenever a real business- or first-class **cash** fare comes back, run Seats.aero to answer
"is there dramatically better award space here?" Premium-cabin award value routinely beats cash
2–5×, and Devon's household profile (transferable-points-eligible, 2 international business seats)
is exactly the award sweet spot. Present it as "did you know award space exists here," not a
replacement for the cash comparison. Always run it for a business-class search.

## Account & auth

- **Pro subscription is ACTIVE** ($9.99/mo, subscribed 2026-07-17). Do NOT re-subscribe.
  - Login: `sunny+seatsaero@waywardlane.com` · Settings (API tab): https://seats.aero/settings
  - No password was set (email-only signup + Stripe). If a password is ever needed, use "forgot
    password" on that address.
- **API key** — read from `~/.sunny/scratch/flight-api-credentials.txt` (the Seats.aero
  `API key:` line, prefix `pro_`). Send it in the **`Partner-Authorization`** header (NOT
  `Authorization`). Low-value key; read the plaintext directly, don't register a
  `credential_manage` entry for it yet (same posture as ignav — see that skill's auth note).
- **Rate limit / cost:** Pro users get up to 1,000 partner-API calls/day at no extra cost beyond
  the Pro subscription. Non-commercial/personal use is the documented default (commercial use
  needs a written agreement — not our case).

```bash
K=$(grep -A6 '^Seats.aero' ~/.sunny/scratch/flight-api-credentials.txt | grep 'API key:' | sed 's/.*API key: *//')
```

## Endpoint — Cached Search

`GET https://seats.aero/partnerapi/search` · header `Partner-Authorization: <key>`

Query params (URL-encode them):

- `origin_airport` — IATA (e.g. `SFO`).
- `destination_airport` — IATA (e.g. `NRT`).
- `cabin` — `economy` | `premium` | `business` | `first`. (Optional; omit to get all cabins'
  availability flags in one response — the per-cabin `*Available` / `*MileageCost` fields are
  always present regardless.)
- `start_date`, `end_date` — `YYYY-MM-DD` range to sweep.

This is the "what award space exists on this route" endpoint. (Seats.aero also has a "Bulk
Availability" dump-one-program endpoint for broad exploration — not needed for the cross-check
role.)

## Response shape

`{"data":[ … ]}`. Each entry is one program's availability for one date:

- `Route`: `{OriginAirport, DestinationAirport, Distance, Source}` — `Source` is the mileage
  program (e.g. `qantas`, `united`, `aeroplan`).
- `Date`, `ParsedDate`.
- Per cabin `X` ∈ {`Y`,`W`,`J`,`F`}:
  - `XAvailable` (bool) — seat open in that cabin.
  - `XMileageCost` (string) / `XMileageCostRaw` (int) — miles required.
  - `XTotalTaxes` / `XTotalTaxesRaw` (int, in `TaxesCurrency` minor units) — cash taxes.
- `TaxesCurrency` (e.g. `USD`).

## Worked example (tested live during this skill's build)

Transpacific business-class award, SFO→NRT, late Nov 2026:

```bash
curl -s -G "https://seats.aero/partnerapi/search" \
  -H "Partner-Authorization: $K" \
  --data-urlencode "origin_airport=SFO" \
  --data-urlencode "destination_airport=NRT" \
  --data-urlencode "cabin=business" \
  --data-urlencode "start_date=2026-11-21" \
  --data-urlencode "end_date=2026-11-23"
```

Real result from this build (2 entries):

```
2026-11-22  qantas  J available  167,000 miles  + $366.40 USD taxes
2026-11-23  qantas  J available  167,000 miles  + $366.40 USD taxes
```

Interpretation for the report: business award space IS open via Qantas on these dates at 167k
miles + ~$366 taxes each. Against a cash business fare (e.g. Ignav's ~$9,436/pair sample), that's
the classic "points crush cash on premium cabins" signal worth surfacing to Devon — with the
caveat that award space is volatile and must be grabbed fast.

Note `XTotalTaxesRaw` is in minor units (e.g. `36640` = $366.40). Divide by 100 for USD.

## Where this fits

`flight-research` is the orchestrator (step 3 = award cross-check). Don't run a whole flight
search from here — this sub-skill documents only the Seats.aero source.
