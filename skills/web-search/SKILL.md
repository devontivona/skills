---
name: web-search
description: Search the web and get back ranked results with usable page content in one call — for any task that needs to find information online, verify a specific claim, or research a topic quickly. Use whenever a task needs "go search for X" rather than reading one already-known URL (that's skill:web-fetch) or driving/interacting with a site (that's skill:browse). Primary tool is the firecrawl-cli `search` command (search + content extraction in a single request); falls back to curl against a known authoritative source, or to skill:browse when a site needs real navigation/interaction.
---

# web-search: query → ranked results with real content

A general-purpose "go find this on the web" tool, composable from any other skill or task.
Distinct from its two neighbors:
- **skill:web-fetch** — you already have a URL, you just want its clean text.
- **skill:browse** — the target needs real interaction (login, forms, clicking through a flow,
  a JS-heavy site that won't render via a plain fetch).
- **web-search (this skill)** — you don't have a URL yet; you need to find and read something.

## Why this over a plain search API

Most "web search" tools return links + snippets only — you then have to fetch each result
separately to actually read it, doubling the round trips and the token cost. Firecrawl's search
does search + full-page content extraction in one call: `--scrape` returns ranked results with
real markdown content already pulled from each page, not just a title/snippet. That's the
default move here — search once, read the content directly from the same response.

## Setup (one-time per box)

Install the CLI globally and confirm the credential:

```bash
npm install -g firecrawl-cli
```

The Firecrawl API key is already registered as the credential `firecrawl-api-key` (shared with
skill:web-fetch's JS-rendering fallback). Pass it into any bash call via the credentials map —
never put it in a command string directly:

```
bash(
  command: 'firecrawl search "..." --scrape --limit 5 --json',
  credentials: { FIRECRAWL_API_KEY: "firecrawl-api-key" }
)
```

If `firecrawl` isn't found, it's not installed on this box yet — run the `npm install -g` above
first (lands in the nvm-managed global bin, no sudo needed on this host).

## Basic usage

```bash
firecrawl search "<query>" --scrape --limit 5 --json
```

- `--scrape` is the important flag — without it you get bare links+snippets, defeating the
  point of using this over a plain search API. Always pass it unless you genuinely only need
  a list of URLs (rare).
- `--limit N` — default 5, max 100. Start small (3-5); raise only if the first pass doesn't
  surface what you need.
- `--json` — compact JSON, easiest to parse programmatically. Omit for pretty-printed output
  if you're eyeballing it directly.
- Output includes, per result: `url`, `title`, `description`, `position`, and (with `--scrape`)
  `markdown` — the actual extracted page content, ready to read and cite.

### Useful filters
- `--sources web,news,images` — narrow or widen result types (default: web).
- `--categories github,research` — filter to GitHub repos or research papers/PDFs.
- `--tbs qdr:d|qdr:w|qdr:m|qdr:y` — time filter (past day/week/month/year) for
  freshness-sensitive queries ("latest," "recent," "as of").
- `--location "<city, state, country>"` / `--country <ISO code>` — geo-target a query.

## How to actually search well

- **Target the specific claim, not the general topic.** For fact-checking a specific number or
  entity (the whole point of skill:decision-coach's SME persona), query for the specific thing —
  "Acme Wealth Management AUM fee schedule" beats "wealth management fees" — and prefer querying
  toward an authoritative source by name when you know one exists (e.g. "FINRA BrokerCheck
  <advisor name>" rather than a generic search hoping BrokerCheck surfaces).
- **Read the returned markdown before citing it.** The response gives you real page content
  inline — actually read it and check it supports the claim you're verifying, don't just cite
  the URL because it showed up in results.
- **Cite the real URL every time.** Every fact pulled from a search result needs its source URL
  named in whatever you're producing — never present a search-derived fact without it.
- **If results are thin or off-target, refine the query rather than accepting weak results.**
  Try a more specific phrase, add `--categories`/`--tbs`, or query a known authoritative
  domain by name — don't settle for the first mediocre batch.

## When to fall back instead

- **A specific authoritative source you already know the URL/domain for, and a plain fetch
  will do** (e.g. hitting a regulator's public disclosure page directly) — use `curl` or
  skill:web-fetch directly; a search round-trip adds nothing when you already know where to
  look.
- **The source needs real interaction** — login, a search form that doesn't expose a query
  string, pagination requiring clicks, a JS-heavy SPA that Firecrawl's scrape can't render
  usefully — reach for skill:browse instead. Don't force firecrawl search to do a browser's job.
- **Firecrawl itself is unavailable** (no credential, API down) — fall back to `curl` directly
  against a known source, or skill:browse for anything requiring real navigation. Don't silently
  skip verification because the primary tool failed — say so and use the fallback.

## Gotchas

- `firecrawl search` without `--scrape` returns snippets/descriptions only — easy to forget and
  end up doing a second fetch pass per result. Default to `--scrape` on.
- Result content can still be thin on JS-heavy pages even with `--scrape` (Firecrawl renders,
  but some sites still resist). If a specific result's `markdown` field is clearly incomplete
  for what you need, fetch that one URL directly via skill:web-fetch or skill:browse rather than
  trusting the thin search-result content.
- This shares the `firecrawl-api-key` credential with skill:web-fetch's fallback tier — same
  Firecrawl account, same free-tier usage quota (1,000 pages/mo as of setup). Heavy search usage
  and web-fetch's JS-fallback usage both draw from the same pool.
