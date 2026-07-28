---
name: nano-banana
description: Generate and edit images with Google's Nano Banana models (Gemini image API) via a thin local wrapper script. Use whenever the owner wants to CREATE or MODIFY a visual — text-to-image generation, image editing/restoration, app icons & favicons, logos & UI elements, seamless patterns/textures, technical diagrams & flowcharts & architecture mockups, illustrations, stickers, social/marketing imagery, or visual story/step sequences. Triggers: "make/generate/create an image", "draw", "design an icon/logo/favicon", "edit this photo", "restore this photo", "make a diagram of", "generate a pattern/texture", "illustrate". NOT for charts from data (use a plotting tool) or for finding existing images on the web (use browse).
---

# Nano Banana (Gemini image models)

A thin, scriptable wrapper over Google's Nano Banana image models — the same engine as the
official Gemini CLI extension, minus the interactive REPL. Deterministic, fast, one shell call
per image. Every image is saved with a sidecar `.txt` recording the model + prompt (reproducibility).

> NOTE (unified-voice-layer, 2026-07-15): only conversations hold send_image. In a
> scheduled run or subagent, put the FINAL image path in your report instead — the
> conversation relays it and sends the image itself.

## Setup (already done, verify if it breaks)

- Script: `scripts/nanobanana.py` (Python 3 stdlib only — no pip installs).
- API key: resolved from the vault credential **`gemini-api-key`**, injected as `NANOBANANA_API_KEY`.
  ALWAYS run via the bash `credentials` map — never paste the key:

      bash(
        command: 'NANOBANANA_API_KEY="$K" python3 ~/.sunny/skills/authored/skills/nano-banana/scripts/nanobanana.py generate --prompt "..." --out ~/.sunny/scratch/out.png',
        credentials: { K: "gemini-api-key" }
      )

## Models (pick by need; default is fine for most)

| Alias | Model | When |
|-------|-------|------|
| `nb2` (default) | gemini-3.1-flash-image | Fast, high quality — the everyday choice |
| `pro` | gemini-3-pro-image | Highest fidelity, complex scenes, text-in-image, detailed diagrams |

Only these two are used (Nano Banana 2 and Pro — never the older v1). Pass `--model pro`, or any
full model name. Override default with env `NANOBANANA_MODEL`.

## Commands

    # Text-to-image
    nanobanana.py generate --prompt "<desc>" [--out path] [--model nb2|pro]
                           [--aspect 1:1|16:9|9:16|4:3|3:4|...] [--n 1-4] [--ref a.png b.png]

    # Edit / restore / compose (feed one or more input images)
    nanobanana.py edit --prompt "<instruction>" --image in.png [in2.png ...] [--out path] [--model ...]

- Always pass `--out` under `~/.sunny/scratch/` (working images; send_image before GC takes them).
  Without it the script drops `image.png` / `edited.png` in the CWD. The REAL saved extension matches the
  returned format (usually `.jpg`) — read the JSON `saved` array the script prints for actual paths.
- `--ref` on generate = style/subject reference images (not edited, used as guidance).
- `--n` returns multiple variations (suffixed `-1`, `-2`, …).
- Always pass an absolute `--out` under the owner's working area; `cd` somewhere writable first.

## There are no separate "icon/diagram/pattern" commands — they are PROMPTS

The official extension's `/icon`, `/diagram`, `/pattern`, `/story`, `/restore` commands are just
prompt engineering over the same generate/edit calls. Reproduce them with good prompts — see
`references/prompt-patterns.md` for ready templates (app icons & favicons at specific sizes, logos,
UI elements, flowcharts, architecture/database diagrams, seamless patterns & textures, photo
restoration, multi-step visual stories). Read that file whenever the task is one of those.

## Workflow discipline (borrowed from the Hermes illustrator skill)

1. Write a tight, specific prompt — subject, style, composition, palette, background, aspect.
2. Generate to the owner's working dir. The sidecar `.txt` is your reproducibility record.
3. To show the owner, send/attach the file (e.g. email skill) — they can't see local paths.
4. Iterate with `edit` on the produced file rather than regenerating from scratch.

## Gotchas

- Output is typically JPEG even if you name it `.png`; the script auto-corrects the extension.
- All outputs carry an invisible SynthID watermark (Google policy) — expected, harmless.
- Text rendered inside images is best with `--model pro`.
- Preview models (`-preview` suffixes) also exist; the GA aliases above are the safe defaults.
- On refusal/no-image, the script prints the model's text explanation — read it, adjust the prompt.
- The API does not support `--n` > 1 (multiple candidates) on this model — it errors with
  "Multiple candidates is not enabled for this model." Loop the generate call once per
  variation instead (see the base-character workflow below) rather than passing `--n`.
- Nano Banana output has NO alpha channel — it's always a flat JPEG. A prompt asking for
  "transparent background" will NOT produce real transparency; you'll get a background that's
  merely plain-colored (e.g. white), not transparent. If true transparency is required, that's a
  separate post-processing step (e.g. a background-removal tool) — don't rely on the prompt alone,
  and say so plainly rather than claiming the output is transparent when it isn't.

- Specific/NAMED object shapes drift when described only in words. Asking for a precise
  silhouette by name (e.g. "a Nick and Nora glass") repeatedly produced a generic
  coupe/wine-glass instead — the model averages toward the common shape. FIX: pass a real
  photo of the exact object as a `--ref` (or `--image` on edit); a shape reference nails it
  where prose can't. (Cocktail-poster job 2026-07-28: burned ~6 word-only rounds, then one
  Wikimedia Nick-and-Nora photo fixed the glass immediately.) Same for "clear/transparent
  glass" material — words alone gave flat opaque tan; anchor material with a reference too.

## CRITICAL: never batch a generate call and its send_image in the same tool-call block

**This is the #1 real-world failure mode with this skill — read before your first call.**
`bash` (running nanobanana.py) and `send_image` are NOT independent calls even though they look
like separate tool invocations — `send_image` depends on the file the bash call just wrote to
disk. Putting them in the same tool-call block (i.e. calling both in one turn) risks `send_image`
firing before the generate call's file write has actually landed, especially over a slower
network round-trip to the Gemini API. The result: `send_image` reports `"status":"delivered"` —
looking completely successful — while the owner receives nothing, or receives a stale/empty file.
This happened repeatedly in practice (multiple back-to-back failed sends) before being traced to
this exact cause.

**The fix — hard sequencing rule:** treat "generate the image" and "send the image" as a
dependent chain, never as independent parallel calls:
1. Call `bash` (nanobanana.py generate/edit) ALONE, wait for its result.
2. Verify the file actually exists and is non-trivial before trusting it — e.g. `ls -la` the
   output path and/or `file <path>` to confirm it's a real image, not a 0-byte placeholder. Don't
   just trust the script's JSON "saved" output — confirm on disk in a separate step.
3. ONLY THEN call `send_image` on the confirmed path, in its own turn (or at minimum after the
   ls/file check has returned) — never bundled into the same block as the generate call.

If sending multiple images, generate all of them first (sequentially or batched among
themselves, since bash-to-bash has no such dependency), confirm each on disk, THEN send them —
don't interleave generate/send/generate/send in a way that tempts batching a pair together.

## Multi-pass consistency workflow (base character + variations)

For a set of illustrations that need to share one consistent character/style (e.g. a mascot
appearing in different scenes or a persona set for a site), don't independently prompt each one
from scratch — text-only prompts drift in style across separate calls. Instead:

1. **Base pass** — generate a handful of candidate versions of the base character/style alone
   (no scene, no action), one at a time (see the `--n` gotcha above — loop individual calls, do
   not pass `--n` > 1). Show them to the owner and lock in one as the canonical base.
2. **Variation pass** — for each variant needed, use `edit` (not `generate`) with the locked-in
   base image passed via `--image`, plus a text prompt describing what should change (a
   different pose, a different small prop) while explicitly instructing the model to preserve
   the established character design, line style, and palette. This anchors every variation to
   the same visual identity instead of letting each one drift independently.
3. **Action/scene pass** — if the action/scene is itself a further variation, either fold it into
   step 2's edit prompt or do one more `edit` pass on the output of step 2, again passing the
   prior image via `--image` so style continuity compounds forward rather than resetting.

This costs more calls than one-shot generation per illustration, but is the reliable way to get
a visually consistent set — much cheaper than discovering after the fact that four independently
generated "personas" look like they came from four different artists.

## Going deeper

For capabilities beyond these templates (advanced multi-image composition, the full option surface),
the upstream extension README is the reference — fetch on demand, don't mirror it here:
https://github.com/gemini-cli-extensions/nanobanana  (raw README:
https://raw.githubusercontent.com/gemini-cli-extensions/nanobanana/main/README.md)
