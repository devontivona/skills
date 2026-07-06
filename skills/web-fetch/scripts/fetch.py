#!/usr/bin/env python3
"""Fetch a URL and return clean, readable main-content text — the general-purpose
"give me this page's real content" tool. Used by any skill that needs to read a
webpage rather than infer from its URL/title (e.g. skill:craft's resource tagger,
but written to be generic — reach for this any time a task needs to actually read
a page's content).

Usage:
  python3 fetch.py <url>              # prints cleaned text to stdout
  python3 fetch.py <url> --raw        # prints raw HTML (debugging)

As a library:
  import fetch
  result, err = fetch.fetch_text(url)
  # result = {"title": str, "text": str, "degraded": bool, "source": "trafilatura"|"firecrawl"|"meta"|"regex"}
  # err = None, or an "ERROR: ..." string on hard failure

## Strategy: a 3-tier cascade (the pattern the wider agent-skills ecosystem uses —
researched 2026-07-06, see topic:craft for the research brief)

1. **trafilatura** (free, local, no API key) — fetches raw HTML with a real browser
   User-Agent, then extracts main content via content-density heuristics. This
   handles the vast majority of pages well (articles, docs, READMEs, blogs) and
   correctly strips nav/sidebar/footer/menu boilerplate. LIMITATION: trafilatura
   only ever sees server-rendered HTML — it does NOT execute JavaScript, so a
   client-rendered SPA (React/Vue app shell) will look empty to it no matter what.

2. **Firecrawl** (paid API with a keyless free fallback — see below) — only engaged
   if tier 1 comes back thin (<200 chars). Firecrawl runs a real headless browser, so
   it executes JS and sees the fully-rendered page — this is what actually fixes the
   JS-rendered-page gap trafilatura can't solve. Calls `POST
   https://api.firecrawl.dev/v2/scrape` with `formats: ["markdown"], onlyMainContent:
   true`. **Works keyless (no API key) out of the box** — Firecrawl's free tier
   allows unauthenticated scrape/search/interact calls, just rate-limited (confirmed
   working 2026-07-06: a keyless call fully rendered a JS-only SPA that trafilatura
   saw as empty). If `FIRECRAWL_API_KEY` is set in the environment, it's sent for
   higher limits and full endpoint access (firecrawl.dev/pricing: free registered
   tier is 1,000 pages/mo, no card) — but the tool works without one.

3. **Meta-tag fallback** (free, local, no API key) — if both of the above come back
   thin/unavailable, pull whatever's in `<title>` / `og:description` / meta
   `description`. These are often still server-rendered even on SPA sites, so this
   is a last real signal before giving up. Result is flagged `degraded: True`.

4. **Regex tag-stripper** (absolute last resort) — only reachable if trafilatura
   itself isn't installed (e.g. a fresh box with no pip access) AND no meta
   description was found. Noisy (keeps nav cruft), but better than nothing.

A Jina Reader (r.jina.ai) fallback was evaluated as a free JS-rendering option but
anonymous/keyless requests get blocked from typical cloud/datacenter IPs (HTTP 401,
"bad network reputation") — not wired in. Revisit if a free Jina API key is ever
added.

## Setup

trafilatura: `~/.local/bin/pip3 install trafilatura --user` (this box has no system
pip/ensurepip/venv — see SUNNY.md for the bootstrap gotcha; once installed it's on
python3's default sys.path, no path hacking needed).

Firecrawl (optional, only needed to raise limits above the keyless free tier): set
`FIRECRAWL_API_KEY` in the environment before calling, e.g. via the bash tool's
`credentials` map if the key is registered in the vault, or export it directly in
the calling shell. **Without it, this script still fully rescues JS-heavy pages** —
Firecrawl's keyless free tier works out of the box, just at a lower rate limit.
"""
import sys
import os
import re
import json
import urllib.request
import urllib.error

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

FIRECRAWL_ENDPOINT = "https://api.firecrawl.dev/v2/scrape"


def _fetch_raw(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            content_type = r.headers.get("Content-Type", "")
            if "text/html" not in content_type and "text" not in content_type:
                return None, f"ERROR: non-text content-type ({content_type})"
            raw = r.read(2_000_000).decode("utf-8", errors="ignore")
            return raw, None
    except urllib.error.HTTPError as e:
        return None, f"ERROR: HTTP {e.code}"
    except Exception as e:
        return None, f"ERROR: {e}"


def _meta_fallback(raw):
    """Pull whatever's in <title>/meta description/og:description — often
    server-rendered even on otherwise JS-only SPA pages."""
    title_m = re.search(r"<title[^>]*>(.*?)</title>", raw, re.S | re.I)
    title = re.sub(r"\s+", " ", title_m.group(1)).strip() if title_m else ""
    desc = ""
    for pattern in (
        r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']',
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
    ):
        m = re.search(pattern, raw, re.S | re.I)
        if m:
            desc = re.sub(r"\s+", " ", m.group(1)).strip()
            break
    return title, desc


def _firecrawl_scrape(url, api_key, timeout=30, max_chars=6000):
    """Tier 2: Firecrawl headless-browser scrape. Works keyless (no api_key) at a
    lower rate limit — Firecrawl's free tier allows unauthenticated scrape calls.
    Returns (result_dict, None) on success, (None, err_str) on failure. Caller
    decides whether to fall through."""
    body = json.dumps({"url": url, "formats": ["markdown"], "onlyMainContent": True}).encode()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(FIRECRAWL_ENDPOINT, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            payload = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return None, f"firecrawl HTTP {e.code}: {e.read().decode()[:300]}"
    except Exception as e:
        return None, f"firecrawl error: {e}"

    if not payload.get("success"):
        return None, f"firecrawl unsuccessful: {json.dumps(payload)[:300]}"

    data = payload.get("data", {})
    markdown = (data.get("markdown") or "").strip()
    title = (data.get("metadata") or {}).get("title", "")
    if len(markdown) > max_chars:
        markdown = markdown[:max_chars]
    if not markdown:
        return None, "firecrawl returned empty markdown"
    return {"title": title, "text": markdown, "degraded": False, "source": "firecrawl"}, None


def fetch_text(url, timeout=12, max_chars=6000):
    """Returns (result_dict, error_str). result_dict has keys:
    title, text, degraded (bool), source (which tier produced the result)."""
    raw, err = _fetch_raw(url, timeout=timeout)
    if err:
        return None, err

    # Tier 1: trafilatura
    text = None
    try:
        import trafilatura
        text = trafilatura.extract(raw, include_comments=False, include_tables=False)
    except ImportError:
        text = None

    title, meta_desc = _meta_fallback(raw)

    if text and len(text.strip()) >= 200:
        if len(text) > max_chars:
            text = text[:max_chars]
        return {"title": title, "text": text.strip(), "degraded": False, "source": "trafilatura"}, None

    # Tier 2: Firecrawl (keyless free tier works out of the box; an API key just
    # raises the rate limit — both paths go through the same call)
    api_key = os.environ.get("FIRECRAWL_API_KEY")  # optional
    fc_result, fc_err = _firecrawl_scrape(url, api_key, max_chars=max_chars)
    if fc_result:
        return fc_result, None
    # fall through on Firecrawl failure too — don't hard-fail the whole call

    # Tier 3: meta description fallback
    if meta_desc:
        return {"title": title, "text": meta_desc, "degraded": True, "source": "meta"}, None

    # Tier 4: crude regex stripper, absolute last resort
    try:
        html = re.sub(r"<script.*?</script>", "", raw, flags=re.S | re.I)
        html = re.sub(r"<style.*?</style>", "", html, flags=re.S | re.I)
        fallback_text = re.sub(r"<[^>]+>", " ", html)
        fallback_text = re.sub(r"\s+", " ", fallback_text).strip()
    except Exception:
        fallback_text = ""

    if fallback_text and len(fallback_text) > 40:
        return {"title": title, "text": fallback_text[:max_chars], "degraded": True, "source": "regex"}, None

    return {"title": title, "text": "", "degraded": True, "source": "none"}, None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: fetch.py <url>", file=sys.stderr)
        sys.exit(1)
    url = sys.argv[1]
    result, err = fetch_text(url)
    if err:
        print(err)
        sys.exit(1)
    if result["degraded"]:
        print(f"WARNING: degraded extraction (source={result['source']}, likely JS-rendered/thin page) —")
    else:
        print(f"(source: {result['source']})")
    print("TITLE:", result["title"])
    print("TEXT:", result["text"])
