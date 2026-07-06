#!/usr/bin/env python3
"""Fetch a URL and return clean, readable main-content text (best-effort).

Usage:
  python3 fetch_page.py <url>          # prints cleaned text to stdout
  python3 fetch_page.py <url> --raw    # prints raw HTML (debugging)

Used by the craft resource-tagging job to actually READ a linked page's content
before judging/tagging/describing it, instead of inferring from the URL/title
alone (a mistake flagged 2026-07 — always fetch and read before judging).

Extraction strategy (2026-07-06, upgraded after research into what the wider
agent-skills ecosystem uses — see topic:craft):
  1. Fetch the raw HTML with a real browser User-Agent (many sites block
     default python/curl UAs).
  2. Extract main content with `trafilatura` — a content-density-based
     readability extractor (the most-recommended OSS tool for this across HN
     and popular agent skills). This is a MASSIVE improvement over naive
     tag-stripping: trafilatura correctly drops nav/sidebar/footer/menu
     boilerplate and keeps only the actual article/README/product text. E.g.
     on a GitHub repo page it returns just the README content, not the ~100
     lines of GitHub nav/menu chrome a regex stripper would include.
  3. If trafilatura returns nothing or very little (empty/near-empty result),
     the page is almost certainly JS-rendered (client-side app shell) rather
     than genuinely content-free — trafilatura, like all static-HTML tools,
     cannot see content that only appears after JS runs. In that case fall
     back to whatever meta tags ARE present in the raw HTML (og:description,
     meta description, <title>) since those are often server-rendered even on
     SPA sites, and flag the result as DEGRADED so the caller can note "thin
     content, page is JS-rendered" in its judgment/description rather than
     silently treating a thin scrape as if it were the full picture.
  4. A Jina Reader (r.jina.ai) fallback for JS-rendered pages was evaluated
     but is NOT wired in: anonymous/keyless requests from this box were
     blocked ("bad network reputation" / HTTP 401) during testing. Revisit if
     a Jina API key is ever added, or if this becomes a frequent blocker.

If bs4/lxml/trafilatura are ever unavailable (e.g. a fresh box with no pip
access), falls back further to a crude regex tag-stripper — noisier, but
better than nothing. Always prefer trafilatura when available.
"""
import sys
import re
import urllib.request
import urllib.error

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


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


def fetch_text(url, timeout=12, max_chars=6000):
    """Returns (result_dict, error_str). result_dict has keys:
    title, text, degraded (bool — True if this is a thin JS-shell fallback,
    not real extracted content)."""
    raw, err = _fetch_raw(url, timeout=timeout)
    if err:
        return None, err

    text = None
    try:
        import trafilatura
        text = trafilatura.extract(raw, include_comments=False, include_tables=False)
    except ImportError:
        text = None  # will hit the regex fallback below if this AND the thin-content path both fail

    title, meta_desc = _meta_fallback(raw)

    if text and len(text.strip()) >= 200:
        if len(text) > max_chars:
            text = text[:max_chars]
        return {"title": title, "text": text.strip(), "degraded": False}, None

    # trafilatura found little/nothing -> likely JS-rendered page. Fall back to
    # meta description; if even that's empty, try the crude regex stripper as
    # a last resort (better than returning nothing).
    if meta_desc:
        return {"title": title, "text": meta_desc, "degraded": True}, None

    try:
        html = re.sub(r"<script.*?</script>", "", raw, flags=re.S | re.I)
        html = re.sub(r"<style.*?</style>", "", html, flags=re.S | re.I)
        fallback_text = re.sub(r"<[^>]+>", " ", html)
        fallback_text = re.sub(r"\s+", " ", fallback_text).strip()
    except Exception:
        fallback_text = ""

    if fallback_text and len(fallback_text) > 40:
        return {"title": title, "text": fallback_text[:max_chars], "degraded": True}, None

    return {"title": title, "text": "", "degraded": True}, None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: fetch_page.py <url>", file=sys.stderr)
        sys.exit(1)
    url = sys.argv[1]
    result, err = fetch_text(url)
    if err:
        print(err)
        sys.exit(1)
    if result["degraded"]:
        print("WARNING: degraded extraction (likely JS-rendered page, thin content) —")
    print("TITLE:", result["title"])
    print("TEXT:", result["text"])
