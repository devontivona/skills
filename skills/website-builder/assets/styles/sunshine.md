# Sunshine -- Style Reference
> A loud, confident electric-yellow surface with near-black ink, flat hard-offset shadows, and a dual IBM Plex type system. Bright, graphic, and a little punk.

**Theme:** light (high-chroma)

Sunshine is the brightest style in the library. A single saturated electric yellow (#f0fb29)
owns the page as the dominant surface -- not an accent, the background itself -- paired with
near-black ink (#202020 / #333333) for maximum contrast. Depth comes only from flat,
hard-offset shadows (no blur), which give cards and buttons a bold, printed, graphic-novel
quality. Corners are nearly square (2px) everywhere -- there are no pills and no soft
rounding. Type splits cleanly: IBM Plex Sans for all display and body, IBM Plex Mono for
labels, tags, and code. A calm sky blue (#aee3fd) is the only secondary color, used for code
surfaces and quiet highlights. Use Sunshine when the content should feel energetic, modern,
and unafraid: launch pages, bold explainers, opinionated comparisons, playful microsites.

## Fonts (self-contained HTML)

Both faces are on Google Fonts -- one `<link>`, no licensed fonts. Add to `<head>`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
```

| Role | Font | Weights |
|------|------|---------|
| Display / headings | **IBM Plex Sans** | 500 (600 sparingly) |
| Body / UI | **IBM Plex Sans** | 400, 500 |
| Labels / tags / code | **IBM Plex Mono** | 400, 500 |

## Tokens -- Colors

| Name | Value | Token | Role |
|------|-------|-------|------|
| Electric Yellow | `#f0fb29` | `--color-electric-yellow` | THE page surface -- dominant background behind hero and most sections |
| Ink | `#202020` | `--color-ink` | Primary text, headings, button fill, and the shadow color |
| Near Black | `#333333` | `--color-near-black` | Body text, nav links, secondary headings on yellow |
| Paper White | `#ffffff` | `--color-paper-white` | Text on dark fills; card surface when yellow needs a rest |
| Light Gray | `#f5f5f5` | `--color-light-gray` | Neutral card/section surface for calmer passages |
| Charcoal | `#202020` | `--color-charcoal` | Dark section backgrounds and dark CTA fills (same hue as ink) |
| Border Gray | `#222222` | `--color-border-gray` | Hairline/solid borders on buttons, cards, inputs |
| Sky Blue | `#aee3fd` | `--color-sky-blue` | Secondary accent only -- code surfaces, inline highlights, quiet callouts |

Contrast rules: ink (#202020) or near-black (#333333) on electric yellow passes AA. On
charcoal/dark fills use paper white. Never put electric yellow text on white (fails contrast) --
yellow is a surface, not a text color.

## Tokens -- Typography

### IBM Plex Sans -- display + body. `--font-sans`
- **Display weights:** 500 (use 600 only for a single hero line if needed)
- **Tracking:** tight and negative at large sizes (see scale); 0 for body
- **Role:** Every heading and all body copy. The look is big, medium-weight headlines with
  heavy negative tracking -- confident, not delicate.

### IBM Plex Mono -- labels, tags, code. `--font-mono`
- **Weights:** 500 for labels/tags (slight positive tracking), 400 for code
- **Role:** Eyebrow labels, badges, nav/button micro-labels, code and technical values.
  The mono/sans contrast is a signature -- lean on it for labels and tags.

### Type Scale

| Role | Font | Size | Line height | Letter spacing | Token |
|------|------|------|-------------|----------------|-------|
| hero | Sans | 96px | 108px | -6px | `--text-hero` |
| h2 | Sans | 64px | 72px | -4px | `--text-h2` |
| h3 | Sans | 40px | 46px | -2.5px | `--text-h3` |
| h4 | Sans | 32px | 36px | -2px | `--text-h4` |
| h5 | Sans | 24px | 30px | -1.5px | `--text-h5` |
| h6 | Sans | 20px | 24px | -1.25px | `--text-h6` |
| body-lg | Sans | 18px | 28px | 0 | `--text-body-lg` |
| body | Sans | 16px | 20px | 0 | `--text-body` |
| label | Mono | 14px | 16px | 0.5px | `--text-label` |
| label-sm | Mono | 12px | 16px | 0.25px | `--text-label-sm` |
| code | Mono | 16px | 24px | 0 | `--text-code` |

On viewports <= 991px, scale the hero down (e.g. clamp to ~15vw) so it never overflows; keep
the negative tracking proportional.

## Tokens -- Spacing & Shapes

**Base unit:** 8px. Scale (px): 0, 1, 2, 4, 8, 16, 24, 32, 40, 48, 64, 80, 96 --
tokens `--space-0` … `--space-96`.

### Border Radius -- NEARLY SQUARE ONLY

| Element | Value | Token |
|---------|-------|-------|
| buttons | 2px | `--radius-sharp` |
| cards | 2px | `--radius-sharp` |
| inputs | 2px | `--radius-sharp` |
| tags / badges | 2px | `--radius-sharp` |
| large media panels | 8px (max) | `--radius-soft` |

There are NO pills and NO fully round controls in Sunshine. Everything is 2px; only large
image/media panels may use 8px. This is a hard rule -- see Don'ts.

### Borders -- 1px by default, 2px reserved for major dividers

Default every border to **1px solid ink/border-gray** -- buttons, cards, tags, inputs, the
retro window's frame, table containers. A page where every outline is 2px reads busy and
cartoonish; keep the outline weight quiet so the flat hard-offset shadows (below) do the work
of standing things out.

Reserve **2px** for genuine major horizontal dividers only:
- Band-to-band seams between full-width sections (e.g. where a dot-grid stats band or a dark
  CTA band meets the surface above/below it).
- A table's header bottom-border (the line under `<thead>`), because it's the one rule
  separating "column labels" from "all data."

Do not use 2px for: button/card/tag/input outlines, in-card dividers (e.g. a spec list's
top rule), or a sticky nav's bottom border -- those should be 1px. If in doubt, default to
1px and only go to 2px when the line is doing real structural work (separating whole page
regions), not decorating a component.

### Shadows -- flat, hard-offset, zero blur

| Name | Value | Token |
|------|-------|-------|
| hard-lg | `8px 8px 0 0 #202020` | `--shadow-hard-lg` |
| hard-sm | `4px 4px 0 0 #202020` | `--shadow-hard-sm` |

Shadows are always solid ink with 0 blur and 0 spread -- a printed offset, never a soft glow.
Interactive elements can "press": on hover translate by the offset and drop the shadow, e.g.
`transform: translate(4px,4px); box-shadow: none;` for a hard-sm button.

### Layout
- **Page max-width:** 1200px, centered.
- **Section rhythm:** 64-96px vertical gap.
- **Card padding:** 24-32px. **Element gap:** 8-16px.
- Heroes are big and left-aligned or split; avoid timid centered stacks for the main headline.

## The Dot Grid (signature background) -- use sparingly

A field of small ink dots on a surface, evoking engineering/graph paper. It is a signature
Sunshine texture -- powerful precisely because it is rare. Use it in AT MOST one or two places
per page.

**When to use it:**
- The footer (its canonical home).
- One hero or CTA band as a backdrop behind bold type.
- Occasionally a single feature/stat panel to make it stand out.

**When NOT to use it:**
- Never behind long body copy or tables (hurts readability).
- Never on more than ~2 sections per page, and never two adjacent sections.
- Not on small components (buttons, tags, cards under ~300px).

**CSS -- dots via a single radial-gradient (drop-in):**
```css
/* Ink dots on the electric-yellow surface (footer/CTA default) */
.dot-grid {
  background-color: var(--color-electric-yellow);
  background-image: radial-gradient(circle, rgba(32,32,32,0.28) 1px, transparent 1.1px);
  background-size: 17px 17px;      /* dot spacing; 12-20px reads well -- keep it fine, not chunky */
  background-position: 0 0;
}
/* Dots on a dark section: light dots on charcoal */
.dot-grid--dark {
  background-color: var(--color-charcoal);
  background-image: radial-gradient(circle, rgba(255,255,255,0.18) 1px, transparent 1.1px);
  background-size: 17px 17px;
}
/* Keep text legible: lay content over a solid inset panel when needed */
.dot-grid .panel { background: var(--color-electric-yellow); }
```
Tune `background-size` for density (bigger = sparser) and the alpha for subtlety. Keep the
dots small and tight (~1px dot, ~17px spacing is the default) -- a larger/looser grid reads
chunky and fights the fine engineering-paper texture that makes this signature work. Keep
dots low-contrast so foreground type stays dominant.

## The Retro Window Card (signature framed figure) — use for a single focal detail

A framed panel styled like a classic desktop/browser window: a square-cornered box with a
1px ink border, the signature 8px hard-offset shadow, and a title bar (bottom-bordered, with
little "window chrome" lines or a label) sitting above a padded body. It reads as a deliberate,
retro-computing "exhibit frame" and draws the eye.

**When to use it (sparingly — it's a spotlight, not a container for everything):**
- A single figure that deserves emphasis: a highlight photo, a diagram/illustration, or a
  screenshot.
- A sidebar-style aside or callout explaining one detail (a "how it works" note, a spec, a
  definition) set apart from the main flow.
- The one "hero exhibit" of a section — e.g. the standout product in a comparison.

**When NOT to use it:**
- Not as the default card for a grid of many items (use the plain Card for those) — the frame
  loses its impact if repeated everywhere. One, maybe two, per page/section.
- Not around long-form body text or full data tables.
- Don't nest a dot grid inside it and put text on the dots (keep the body a solid surface).

**CSS (drop-in):**
```css
.retro-window {
  background: var(--color-paper-white);
  border: 1px solid var(--color-ink);
  border-radius: var(--radius-sharp);        /* 2px — essentially square */
  box-shadow: var(--shadow-hard-lg);         /* 8px 8px 0 ink */
  overflow: hidden;                          /* keep the title bar corners crisp */
  max-width: 480px;                          /* it's a focal figure, not full-bleed */
}
.retro-window__bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--color-ink);
  background: var(--color-paper-white);       /* or --color-electric-yellow for a louder bar */
}
/* left-side "traffic light" dots (outlined, on-brand — not red/yellow/green) */
.retro-window__dots { display: flex; gap: 6px; }
.retro-window__dots i {
  width: 10px; height: 10px; border-radius: 50%;
  border: 1px solid var(--color-ink); display: inline-block;
}
/* optional title text in mono */
.retro-window__title {
  font-family: var(--font-mono); font-size: var(--text-label-sm);
  letter-spacing: 0.5px; color: var(--color-near-black); margin-left: 4px;
}
.retro-window__body { padding: 24px; }         /* 24-32px */
.retro-window__body img { display: block; width: 100%; height: auto; }
```
```html
<figure class="retro-window">
  <div class="retro-window__bar">
    <span class="retro-window__dots"><i></i><i></i><i></i></span>
    <span class="retro-window__title">how-it-works.txt</span>
  </div>
  <div class="retro-window__body">
    <!-- one photo, diagram, or a short aside/explanation -->
  </div>
</figure>
```
Variants: use an electric-yellow title bar for a louder exhibit; swap the dots for a single
mono title if you want it to read more like a text-file window. The dots stay outlined ink
(no colored traffic lights) to respect the two-color system. Round dots are the ONE allowed
exception to the sharp-corner rule — they're an intentional retro motif, not a UI control.

## Components

### Primary Button (sharp, hard shadow)
Fill `--color-ink`, text `--color-paper-white`, `border-radius: 2px`, border `1px solid #202020`,
padding `12px 20px`, `--font-mono` 14px/500, **`text-transform: uppercase`**,
`box-shadow: var(--shadow-hard-sm)`. Hover: `transform: translate(4px,4px); box-shadow: none;`
(the "press"). NEVER pill-shaped.

### Secondary Button (outline)
Background transparent or `--color-paper-white`, text `--color-ink`, `border-radius: 2px`,
border `1px solid #222222`, same padding + mono label, **uppercase**. Optional hard-sm shadow.
Sharp corners.

All button labels are UPPERCASE (the mono label, letter-spacing, and all-caps together are
what make the button read as a mono "control" rather than a link) -- put `text-transform:
uppercase` on the shared `.btn` base rule so every variant inherits it.

**Specificity gotcha:** give button-variant classes a compound selector, e.g.
`.btn.btn--primary` / `.btn.btn--secondary`, not a bare `.btn--primary`. A generic ambient
rule elsewhere (e.g. `.nav a { color: ... }`) can have equal CSS specificity to a bare
`.btn--primary`, and equal-specificity rules resolve by source order -- whichever is
declared later in the stylesheet silently wins, which can leave a button with the wrong
text color (e.g. invisible dark-on-dark text) even though the button's own rule looks
correct in isolation. Compounding the selector guarantees the button's own styling always
wins regardless of where either rule sits in the file.

### Card
Background `--color-paper-white` (or `--color-light-gray`), `border-radius: 2px`, border
`1px solid #202020`, `box-shadow: var(--shadow-hard-lg)`, padding 24-32px. On an electric-yellow
section a white card with a hard ink shadow is the workhorse container. (The shadow, not the
border, is what should read as bold -- keep the outline a quiet 1px.)

### Retro Window Card
**Role:** A single framed focal figure — highlight photo, diagram, screenshot, or a set-apart
sidebar explanation. See "The Retro Window Card" section for full CSS + usage. Square box, 1px
ink border, 8px hard-offset shadow, a bottom-bordered title bar (outlined dots and/or a mono
title) over a 24-32px padded body. Use at most one or two per page — it is a spotlight.

### Eyebrow Label / Tag
`--font-mono` 12-14px/500, letter-spacing 0.5px, uppercase optional. As a tag: 2px radius,
1px solid border, 2-8px padding. Great sitting above an h2/h3 to label a section.

### Code / Highlight Surface
Background `--color-sky-blue`, ink text, `--font-mono` 16px, 2px radius, 16-24px padding. The
only place sky blue leads. Also usable for a quiet inline highlight (sky-blue background behind
a word).

### Input
Background `--color-paper-white`, `border-radius: 2px`, border `1px solid #222222`, padding
`12px 16px`, ink text, `--font-sans` 16px. Sharp, like everything else.

### Stat / Feature Block
Big `--text-h2`/`--text-h3` number in Sans 500 with heavy negative tracking, a mono label
beneath. Optionally one such band sits on the dot grid.

## Do's and Don'ts

### Do
- Let electric yellow be the dominant surface -- it is the background, not an accent.
- Keep ALL corners at 2px (max 8px for large media). Sharp is the identity.
- Use only flat hard-offset shadows (solid ink, 0 blur). Let buttons "press" on hover.
- Pair IBM Plex Sans (display/body) with IBM Plex Mono (labels/tags/code) -- lean on that contrast.
- Set every button label to uppercase (`text-transform: uppercase` on the shared `.btn` base).
- Keep borders 1px by default; reserve 2px only for major band-to-band section dividers and a table's header rule.
- Apply heavy negative letter-spacing to large headings (-2px to -6px) for the confident look.
- Reserve the dot grid for the footer plus at most one other band; keep dots small and low-contrast (~1px dot / ~17px spacing default).
- Keep sky blue secondary -- code surfaces and quiet highlights only.

### Don't
- NEVER use pills or fully rounded controls, and never radii between 2px and 8px -- no soft
  "friendly" rounding. Sunshine is sharp.
- Never use soft/blurred shadows (any blur or spread > 0) -- the shadow vocabulary is flat offset only.
- Never set electric yellow as a text color, and never put ink/near-black text on a busy dot
  grid without a solid panel behind it.
- Don't overuse the dot grid (no more than ~2 sections, never adjacent, never behind body text/tables).
- Don't introduce a third chromatic color -- the system is yellow + ink + one sky blue.
- Don't render display or body text in the mono face (mono is for labels/tags/code), and don't
  set headings below weight 500.

## Surfaces

| Level | Name | Value | Purpose |
|-------|------|-------|---------|
| 1 | Yellow Surface | `#f0fb29` | The dominant page background |
| 2 | Paper Card | `#ffffff` | Cards/containers that sit on yellow (with hard ink shadow) |
| 3 | Neutral | `#f5f5f5` | Calmer section/card surface when yellow needs a rest |
| 4 | Charcoal | `#202020` | Dark sections / dark CTA fills (paper-white text) |
| — | Border | `#202020` / `#222222` | Solid 2px borders and the shadow color |
| — | Sky | `#aee3fd` | Secondary: code surfaces + quiet highlights |

## Imagery
Prefer bold, graphic visuals: high-contrast product shots on white cards (2px radius, hard
shadow), simple line icons in ink (mono stroke, never multicolor), and the dot grid as texture.
Keep image density moderate -- type and color do the heavy lifting. No soft drop shadows on
images; if an image needs elevation, give it the flat hard-offset shadow like a card.

## Layout
Max-width ~1200px on the electric-yellow canvas. Sticky top nav: wordmark left (Sans 600 or
mono label), nav links (mono 14px), a sharp primary button right. Hero is oversized Sans 500
with heavy negative tracking, left-aligned or split 50/50 with a card/visual; a sharp primary +
outline secondary button pair beneath. Sections alternate yellow, white-card clusters, and the
occasional charcoal band. Footer is the dot grid (ink dots on yellow, or light dots on
charcoal) with mono labels. Generous 64-96px section rhythm.

## Quick Start -- CSS Custom Properties

```css
:root {
  /* Colors */
  --color-electric-yellow: #f0fb29;
  --color-ink: #202020;
  --color-near-black: #333333;
  --color-paper-white: #ffffff;
  --color-light-gray: #f5f5f5;
  --color-charcoal: #202020;
  --color-border-gray: #222222;
  --color-sky-blue: #aee3fd;

  /* Fonts -- both on Google Fonts (see <link>) */
  --font-sans: 'IBM Plex Sans', ui-sans-serif, system-ui, -apple-system, sans-serif;
  --font-mono: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, monospace;

  /* Type scale */
  --text-hero: 96px; --text-h2: 64px; --text-h3: 40px; --text-h4: 32px;
  --text-h5: 24px; --text-h6: 20px; --text-body-lg: 18px; --text-body: 16px;
  --text-label: 14px; --text-label-sm: 12px; --text-code: 16px;

  /* Weights */
  --fw-regular: 400; --fw-medium: 500; --fw-semibold: 600;

  /* Spacing (8px base) */
  --space-1: 1px; --space-2: 2px; --space-4: 4px; --space-8: 8px; --space-16: 16px;
  --space-24: 24px; --space-32: 32px; --space-40: 40px; --space-48: 48px;
  --space-64: 64px; --space-80: 80px; --space-96: 96px;

  /* Radius -- sharp only */
  --radius-sharp: 2px; --radius-soft: 8px;

  /* Shadows -- flat hard offset, zero blur */
  --shadow-hard-lg: 8px 8px 0 0 #202020;
  --shadow-hard-sm: 4px 4px 0 0 #202020;

  /* Layout */
  --page-max-width: 1200px;
}
```
