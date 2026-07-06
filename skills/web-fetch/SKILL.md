---
name: web-fetch
description: Fetch a URL and get back clean, readable main-content text (not raw HTML) for an AI to read, summarize, or judge — a general-purpose "actually read this page" tool. Use whenever a task needs to read a webpage's real content rather than infer from its URL or title alone — reading an article, checking what a linked tool/repo/product actually is, researching a page, or any job (like Craft resource-tagging) that needs to judge or describe something behind a link. Handles JS-rendered pages via an optional Firecrawl fallback.
---

# web-fetch: URL → clean readable text

A small, reusable extraction tool: give it a URL, get back the page's real content as
plain text, with nav/ads/boilerplate stripped out — good enough to read, judge, or
summarize from. Built originally for skill:craft's resource-tagging job, but written
generic — reach for this any time a task needs to actually read a page rather than
guess from its link or title.

## Usage

As a library (preferred inside another skill's procedure):

```python
import sys
sys.path.insert(0, "~/.sunny/skills/authored/skills/web-fetch/scripts")  # expand ~ first
import fetch
result, err = fetch.fetch_text("https://example.com/some-article")
if err:
    # hard failure (404, timeout, blocked, non-HTML) — fall back to whatever
    # context you already have (e.g. a saved blurb) rather than guessing
    ...
else:
    result["title"]     # page title
    result["text"]      # extracted main content, ~6000 char cap
    result["degraded"]  # True if this is a thin/fallback result (see below) —
                         # treat as lower-confidence, note it if you use it
    result["source"]    # "trafilatura" | "firecrawl" | "meta" | "regex" | "none"
```

Or from bash / as a quick manual check:
```
python3 ~/.sunny/skills/authored/skills/web-fetch/scripts/fetch.py "https://example.com"
```

## How it works: a 3-tier cascade

This mirrors the pattern the wider AI-agent-skills ecosystem actually uses for this
problem (researched 2026-07-06 — trafilatura-first, headless-browser/paid-API
fallback for JS pages; see topic:craft for the full research brief with citations).

1. **trafilatura** (free, local, always tried first) — fetches raw HTML with a real
   browser User-Agent, extracts main content via content-density heuristics. Handles
   the large majority of pages well: articles, blog posts, docs, GitHub READMEs. It
   correctly drops nav/sidebar/footer/menu chrome — e.g. on a GitHub repo page it
   returns just the README, not ~100 lines of GitHub's own navigation. **Limitation:
   it never executes JavaScript** — a client-rendered SPA (React/Vue app shell) looks
   empty to it no matter what, because it only ever sees the server-sent HTML.

2. **Firecrawl** (optional, only runs if `FIRECRAWL_API_KEY` is set in the
   environment AND tier 1 came back thin, <200 chars) — a paid API with a generous
   free tier (1,000 pages/mo, no card required — firecrawl.dev/pricing) that runs a
   real headless browser, so it executes JS and can see fully-rendered content. This
   is the actual fix for the JS-rendering gap trafilatura can't close. If no API key
   is set, this tier is silently skipped — the tool still works fine via tiers 1/3/4,
   it just can't rescue JS-heavy pages beyond a thin meta-description fallback.

3. **Meta-tag fallback** (free, local) — if trafilatura and Firecrawl both come back
   thin/unavailable, pulls `<title>` / `og:description` / meta `description`. These
   are often still server-rendered even on SPA sites, so it's a real (if thin)
   signal. Result is flagged `degraded: True` — treat it as lower-confidence input,
   not a full read of the page.

4. **Regex tag-stripper** (last resort) — only reached if trafilatura itself isn't
   installed and no meta description exists. Noisy (keeps nav cruft) but better than
   nothing.

**On `degraded: True` results**: still usable (e.g. for a rough tag/category
judgment), but don't present a description built from a degraded fetch with full
confidence — say the content was thin/JS-rendered if that's relevant to how the
result gets used downstream.

## Setup

**trafilatura** (required for tier 1 — install once per box):
```
curl -sL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
python3 /tmp/get-pip.py --user
~/.local/bin/pip3 install trafilatura --user
```
This box has no system pip/ensurepip/venv and no sudo (`apt install python3-pip`
fails without a password) — the get-pip.py + `~/.local/bin/pip3` path above is the
one that actually works; `python3 -m pip` keeps failing even after a successful
get-pip.py run. Once installed, `import trafilatura` works from any script with no
path hacking — `~/.local/lib/python3.10/site-packages` is already on `python3`'s
default `sys.path`.

**Firecrawl** (optional, only needed for the JS-rendering fallback tier): get a free
API key at firecrawl.dev (free tier: 1,000 pages/mo, no card), register it as a
vault credential (e.g. name it `firecrawl-api-key`), then pass it into any bash call
that needs it via the credentials map so the key is never exposed in your context:

```
bash(
  command: 'FIRECRAWL_API_KEY="$K" python3 ~/.sunny/skills/authored/skills/web-fetch/scripts/fetch.py "https://example.com"',
  credentials: { K: "firecrawl-api-key" }
)
```

Without a key set, `fetch.py` still runs fine — it just can't rescue JS-heavy pages
past the thin meta-tag fallback.

## Gotchas

- Fetches send a real browser User-Agent — some sites still block non-browser
  traffic outright (Cloudflare bot detection, etc.); that shows up as an
  `ERROR: HTTP 403` or similar from tier 1's raw fetch, which short-circuits the
  whole cascade (Firecrawl isn't tried on a raw-fetch failure, only on a *thin
  result* from trafilatura — a distinction worth knowing if a page hard-blocks the
  initial request rather than just being JS-heavy).
- A Jina Reader (r.jina.ai) fallback was evaluated as a free JS-rendering option but
  anonymous/keyless requests get blocked from this box's IP (HTTP 401, "bad network
  reputation" — common for cloud/datacenter IPs). Not wired in; revisit if a free
  Jina API key is ever added.
- ~6000 char cap on extracted text by default (`max_chars` param) — plenty for
  judgment/description-writing, not meant for full-document analysis of very long
  pages.
