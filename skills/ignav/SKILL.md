---
name: ignav
description: "Ignav flight-fare API (ignav.com): live cash one-way/round-trip fares with cabin_class up to first, multi-passenger, and market/currency arbitrage (80 markets). Source sub-skill used by flight-research. Endpoints, X-Api-Key header, worked curl examples. Keywords: ignav, flight fares API, cash fare cross-check, market arbitrage, cabin_class."
---

# Ignav — cash-fare API (source sub-skill)

Ignav (ignav.com) is a small REST API that returns live one-way and round-trip **cash**
fares (price, carrier, segments, duration, baggage) plus a booking-link lookup. It is the
second cash-fare source in the `flight-research` workflow — a genuine cross-check against
Google Flights, not just a fallback. Its differentiator is programmatic parameters Google
Flights' URL trick can't express cleanly: explicit `cabin_class` (through first), multi-passenger
counts, and a `market` parameter for currency/locale arbitrage across 80 country markets.

**Accuracy caveat (do not skip):** Ignav is a young, low-visibility product. Its own FAQ says
"treat displayed prices as approximate" and don't cache more than a few hours. Each price
carries a `status` field (e.g. `"verified"`). Always spot-check a quoted Ignav price against
Google Flights before leaning on it for a booking decision — flag a lone outlier price, don't
present it as gospel.

## Account & auth

- **Signup is DONE** — the account already exists. Do NOT re-signup.
  - Login: `sunny+ignav@waywardlane.com` · Dashboard: https://ignav.com/dashboard
- **API key** — read the value from `~/.sunny/scratch/flight-api-credentials.txt` (the `Ignav …
  API key:` line) and use it directly as the `X-Api-Key` header value. It is a low-value key
  (1,000 free requests, then $2/1,000), not a high-value secret; Devon has the plaintext file.
- **Do NOT use `credential_manage` for this key yet, and do NOT use the credential NAME
  `ignav-api-key` in any bash `credentials:` injection.** That name is currently mis-registered
  in the vault (it points at a card-CVV field, not this key — using it would leak card data).
  Once Devon adds the real key to the 1Password vault, this skill should be updated to register
  a clean credential (e.g. `ignav-api-key` after the bad entry is fixed) and inject it via bash
  `credentials:` instead of reading the plaintext file. Until then: read the scratch file.

Read the key into an env var for a call without printing it:

```bash
K=$(grep -A4 '^Ignav' ~/.sunny/scratch/flight-api-credentials.txt | grep 'API key:' | sed 's/.*API key: *//')
```

- **Cost:** 1,000 free requests, then $2 per 1,000 successful requests. Failed (4xx/5xx)
  requests are never billed. A handful of searches per flight-research run is fine.

## Endpoints

Base: `https://ignav.com` · Auth header on every request: `X-Api-Key: <key>`

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/airports` | GET | Resolve an airport/city to IATA codes. Query param `?q=<text>`. |
| `/api/fares/one-way` | POST | One-way cash fares. |
| `/api/fares/round-trip` | POST | Round-trip cash fares. |
| `/api/fares/booking-links` | POST | Direct booking URLs for a chosen itinerary. |

**No multi-city / open-jaw endpoint exists.** For open-jaw with Ignav, fire two one-way calls
(A→B and C→D) and sum them, then compare against the round-trip endpoint. (`flight-research`
prefers Google Flights' native multi-city search for true open-jaw; Ignav's two-one-way trick is
a numeric cross-check only.)

### Request body params (fares endpoints)

- `origin`, `destination` — IATA codes (required).
- `departure_date` — `YYYY-MM-DD` (required). `return_date` — required for round-trip.
- `cabin_class` — `economy` | `premium_economy` | `business` | `first`. **Always set explicitly**
  — per-traveler cabin must be nailed down per search (see flight-research intake).
- `adults`, `children`, `infants_in_seat`, `infants_on_lap` — passenger counts.
- `market` — 2-letter ISO country code (80 supported). Sets preferred **currency + locale** of
  results and affects which booking providers/fare rules show. This is the programmatic
  market-arbitrage lever — e.g. `US` vs `JP` for a US↔Japan route.
- Filters (optional): `max_stops`, `max_price`, `min_carry_on_bags`, `min_checked_bags`,
  `airlines_include`, `airlines_exclude`, `allow_self_transfer`, `departure_time_range`,
  `return_time_range`.

Mixed-cabin note: Ignav prices ONE `cabin_class` per call. For Devon's common "2 economy + 2
business" pattern, run two calls (one `economy` adults=2, one `business` adults=2) and sum — same
shape as the Google Flights econ/biz split.

## Worked examples (tested live against the real API during this skill's build)

### Airport lookup

```bash
curl -s "https://ignav.com/api/airports?q=San+Francisco" -H "X-Api-Key: $K"
# → [{"code":"SFO","name":"San Francisco International Airport","city":"San Francisco","country":"US"},
#    {"code":"OAK",...},{"code":"SJC",...}]
```

### One-way, economy, market=US

```bash
curl -s -X POST "https://ignav.com/api/fares/one-way" \
  -H "X-Api-Key: $K" -H "Content-Type: application/json" \
  -d '{"origin":"SFO","destination":"NRT","departure_date":"2026-11-21","cabin_class":"economy","adults":1,"market":"US"}'
```

Returns `{"origin","destination","departure_date","itineraries":[…]}`. Each itinerary:
`price:{amount,currency,status}`, `outbound:{carrier,duration_minutes,segments:[…]}`,
`cabin_class`, `bags`, `requires_self_transfer`, and an `ignav_id` (feed to booking-links).
(Live sample this build: cheapest ~$642 USD, STARLUX via TPE, `status:"verified"`.)

### Round-trip, business, 2 adults

```bash
curl -s -X POST "https://ignav.com/api/fares/round-trip" \
  -H "X-Api-Key: $K" -H "Content-Type: application/json" \
  -d '{"origin":"SFO","destination":"NRT","departure_date":"2026-11-21","return_date":"2026-11-28","cabin_class":"business","adults":2,"market":"US"}'
```

Round-trip itineraries add an `inbound` leg alongside `outbound`. (Live sample this build:
cheapest business itinerary ~$9,436 USD for the pair — spot-check against Google Flights before
quoting.)

### Booking links for a chosen itinerary

```bash
curl -s -X POST "https://ignav.com/api/fares/booking-links" \
  -H "X-Api-Key: $K" -H "Content-Type: application/json" \
  -d "{\"ignav_id\":\"<ignav_id from a fare result>\"}"
```

Returns `booking_options:[{legs,links:[{provider_name,provider_type,price,url}]}]` — direct
provider cart URLs. (Occasionally returns a transient error for a just-issued id; re-issue the
fare search to refresh the id and retry.)

## Where this fits

`flight-research` is the orchestrator. Use Ignav there as step 2 (cash cross-check). Don't drive
a full flight search from this sub-skill alone — it documents only the Ignav source.
