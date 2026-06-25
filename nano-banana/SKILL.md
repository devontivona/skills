---
name: nano-banana
description: Generate and edit images with Google's Nano Banana models (Gemini image API) via a thin local wrapper script. Use whenever the owner wants to CREATE or MODIFY a visual — text-to-image generation, image editing/restoration, app icons & favicons, logos & UI elements, seamless patterns/textures, technical diagrams & flowcharts & architecture mockups, illustrations, stickers, social/marketing imagery, or visual story/step sequences. Triggers: "make/generate/create an image", "draw", "design an icon/logo/favicon", "edit this photo", "restore this photo", "make a diagram of", "generate a pattern/texture", "illustrate". NOT for charts from data (use a plotting tool) or for finding existing images on the web (use browse).
---

# Nano Banana (Gemini image models)

A thin, scriptable wrapper over Google's Nano Banana image models — the same engine as the
official Gemini CLI extension, minus the interactive REPL. Deterministic, fast, one shell call
per image. Every image is saved with a sidecar `.txt` recording the model + prompt (reproducibility).

## Setup (already done, verify if it breaks)

- Script: `scripts/nanobanana.py` (Python 3 stdlib only — no pip installs).
- API key: resolved from the vault credential **`gemini-api-key`**, injected as `NANOBANANA_API_KEY`.
  ALWAYS run via the bash `credentials` map — never paste the key:

      bash(
        command: 'NANOBANANA_API_KEY="$K" python3 ~/.sunny/skills/authored/nano-banana/scripts/nanobanana.py generate --prompt "..." --out ~/work/out.png',
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

- `--out` defaults to `image.png` / `edited.png` in the CWD. The REAL saved extension matches the
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

## Going deeper

For capabilities beyond these templates (advanced multi-image composition, the full option surface),
the upstream extension README is the reference — fetch on demand, don't mirror it here:
https://github.com/gemini-cli-extensions/nanobanana  (raw README:
https://raw.githubusercontent.com/gemini-cli-extensions/nanobanana/main/README.md)
