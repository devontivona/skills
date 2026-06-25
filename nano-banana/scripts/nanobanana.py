#!/usr/bin/env python3
"""nanobanana.py — thin wrapper over Google's Nano Banana image models (Gemini API).

Generates and edits images via the REST generateContent endpoint. No Gemini CLI,
no REPL — deterministic and scriptable. The API key is read from the environment
(NANOBANANA_API_KEY, then GEMINI_API_KEY, then GOOGLE_API_KEY); never pass it on
the command line. Every generated image gets a sidecar .txt prompt file for
reproducibility.

Usage:
  nanobanana.py generate --prompt "a watercolor fox" [--out fox.png] [--model nb2]
                         [--aspect 16:9] [--n 1] [--ref a.png b.png]
  nanobanana.py edit --prompt "add sunglasses" --image in.png [--out out.png] [--model nb2]

Model aliases: nb2 (gemini-3.1-flash-image, default) | pro (gemini-3-pro-image).
               Only Nano Banana 2 and Pro are used. Or pass any full model name.
Env override: NANOBANANA_MODEL.
"""
import argparse, base64, json, mimetypes, os, sys, time, urllib.request, urllib.error

MODELS = {
    "nb2": "gemini-3.1-flash-image",  # Nano Banana 2 — default, fast, high quality
    "pro": "gemini-3-pro-image",      # Nano Banana Pro — highest fidelity, text-in-image, diagrams
}
DEFAULT_MODEL = "nb2"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

def get_key():
    for k in ("NANOBANANA_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"):
        v = os.environ.get(k)
        if v:
            return v
    sys.exit("ERROR: no API key. Set NANOBANANA_API_KEY (or GEMINI_API_KEY).")

def resolve_model(m):
    if not m:
        m = os.environ.get("NANOBANANA_MODEL") or DEFAULT_MODEL
    return MODELS.get(m, m)

def img_part(path):
    if not os.path.exists(path):
        sys.exit(f"ERROR: input image not found: {path}")
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return {"inlineData": {"mimeType": mime, "data": data}}

def build_body(prompt, refs, aspect, n):
    parts = [{"text": prompt}]
    for r in refs or []:
        parts.append(img_part(r))
    body = {"contents": [{"parts": parts}]}
    gen = {}
    if n and n > 1:
        gen["candidateCount"] = n
    if aspect:
        gen["imageConfig"] = {"aspectRatio": aspect}
    if gen:
        body["generationConfig"] = gen
    return body

def call(model, body, key, retries=3):
    url = ENDPOINT.format(model=model)
    raw = json.dumps(body).encode()
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=raw, headers={
            "Content-Type": "application/json", "x-goog-api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            last = f"HTTP {e.code}: {detail[:500]}"
            if e.code in (429, 500, 503) and attempt < retries - 1:
                time.sleep(2 * (attempt + 1)); continue
            sys.exit(f"ERROR: API call failed — {last}")
        except urllib.error.URLError as e:
            last = str(e)
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1)); continue
            sys.exit(f"ERROR: network error — {last}")
    sys.exit(f"ERROR: {last}")

MIME_EXT = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}

def save_images(resp, out, prompt, model):
    cands = resp.get("candidates", [])
    if not cands:
        fb = resp.get("promptFeedback", {})
        sys.exit(f"ERROR: no candidates returned. Feedback: {json.dumps(fb)[:300]}")
    saved = []
    idx = 0
    base, _ = os.path.splitext(out)
    n_imgs = sum(1 for c in cands for q in c.get("content", {}).get("parts", [])
                 if (q.get("inlineData") or q.get("inline_data")))
    for ci, c in enumerate(cands):
        for q in c.get("content", {}).get("parts", []):
            inline = q.get("inlineData") or q.get("inline_data")
            if not inline:
                continue
            data = base64.b64decode(inline["data"])
            mime = inline.get("mimeType") or inline.get("mime_type") or "image/png"
            ext = MIME_EXT.get(mime, ".png")
            path = f"{base}{ext}" if n_imgs == 1 else f"{base}-{idx+1}{ext}"
            with open(path, "wb") as f:
                f.write(data)
            with open(base + (".txt" if n_imgs == 1 else f"-{idx+1}.txt"), "w") as f:
                f.write(f"model: {model}\nprompt: {prompt}\n")
            saved.append(path); idx += 1
    if not saved:
        # surface any text the model returned (often a refusal/explanation)
        texts = [p.get("text","") for c in cands for p in c.get("content",{}).get("parts",[]) if p.get("text")]
        sys.exit("ERROR: no image data in response. Model said: " + (" ".join(texts)[:400] or "(nothing)"))
    return saved

def main():
    ap = argparse.ArgumentParser(description="Nano Banana image generation/editing")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("generate", "edit"):
        s = sub.add_parser(name)
        s.add_argument("--prompt", required=True)
        s.add_argument("--out", default=None)
        s.add_argument("--model", default=None)
        s.add_argument("--aspect", default=None, help="e.g. 1:1, 16:9, 9:16, 4:3, 3:4")
        if name == "generate":
            s.add_argument("--n", type=int, default=1, help="number of images (1-4)")
            s.add_argument("--ref", nargs="*", default=[], help="reference image(s) for style/subject")
        else:
            s.add_argument("--image", required=True, nargs="+", help="input image(s) to edit")
    a = ap.parse_args()
    key = get_key()
    model = resolve_model(a.model)
    if a.cmd == "edit":
        refs = a.image; n = 1
        out = a.out or "edited.png"
    else:
        refs = a.ref; n = max(1, min(getattr(a, "n", 1), 4))
        out = a.out or "image.png"
    out = os.path.abspath(os.path.expanduser(out))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    body = build_body(a.prompt, refs, a.aspect, n)
    resp = call(model, body, key)
    saved = save_images(resp, out, a.prompt, model)
    print(json.dumps({"model": model, "saved": saved}, indent=2))

if __name__ == "__main__":
    main()
