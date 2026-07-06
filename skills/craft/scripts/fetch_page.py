#!/usr/bin/env python3
"""Fetch a URL and return cleaned, readable text content (best-effort).

Usage:
  python3 fetch_page.py <url>          # prints cleaned text to stdout
  python3 fetch_page.py <url> --raw    # prints raw HTML (debugging)

Used by the craft resource-tagging job to actually READ a linked page's content
before judging/tagging/describing it, instead of inferring from the URL/title
alone (a mistake flagged 2026-07 — always fetch and read before judging).

Sends a real browser User-Agent (many sites block default python/curl UAs).
Strips script/style/nav/header/footer/svg before extracting text — crude but
good enough for "does this page look like X" judgment calls, not a citation-
grade extraction. If the fetch fails (timeout, 403, non-HTML), prints an
explicit ERROR line so the job can fall back to "insufficient info" behavior
in Craft, but the SKILL.md rule is to prefer FAILING/skipping a doc over
inferring from the link alone.
"""
import sys
import re
import urllib.request
import urllib.error

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


def fetch_text(url, timeout=12, max_chars=6000):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            content_type = r.headers.get("Content-Type", "")
            if "text/html" not in content_type and "text" not in content_type:
                return None, f"ERROR: non-text content-type ({content_type})"
            raw = r.read(2_000_000).decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        return None, f"ERROR: HTTP {e.code}"
    except Exception as e:
        return None, f"ERROR: {e}"

    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(raw, "lxml")
        for tag in soup(["script", "style", "nav", "header", "footer", "svg", "noscript", "form"]):
            tag.decompose()
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        text = soup.get_text(separator=" ", strip=True)
    except Exception:
        # bs4/lxml unavailable — crude regex fallback
        html = re.sub(r"<script.*?</script>", "", raw, flags=re.S | re.I)
        html = re.sub(r"<style.*?</style>", "", html, flags=re.S | re.I)
        m = re.search(r"<title[^>]*>(.*?)</title>", raw, re.S | re.I)
        title = re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
        text = re.sub(r"<[^>]+>", " ", html)

    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_chars:
        text = text[:max_chars]
    return {"title": title, "text": text}, None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: fetch_page.py <url>", file=sys.stderr)
        sys.exit(1)
    url = sys.argv[1]
    result, err = fetch_text(url)
    if err:
        print(err)
        sys.exit(1)
    print("TITLE:", result["title"])
    print("TEXT:", result["text"])
