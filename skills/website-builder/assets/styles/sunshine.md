# Sunshine -- Style Reference
> A loud, confident electric-yellow surface with near-black ink, flat hard-offset shadows, and a dual IBM Plex type system. Bright, graphic, and a little punk.

**Theme:** light, high-craft, restrained

Sunshine pairs a clean paper-white canvas with near-black ink (#202020 / #333333) for the
bulk of the page, and treats a single saturated electric yellow (#f0fb29) as a **rare, high-impact
accent** -- not the base surface. Think of yellow like a designer's one loud color: it shows up
as a hero/header band, an occasional callout section, or a single small accent (a tag, an
icon, an underline) -- never as the default background of ordinary content sections, and never
more than one yellow element visible in a given viewport. This restraint is what separates
Sunshine from an amateur "make it all yellow" pastiche -- see "Yellow usage discipline" below,
it is the most important rule in this doc. Depth on cards comes from flat hard-offset shadows
(no blur) for a bold, printed quality; buttons stay flat (no shadow -- see Buttons). Corners
are nearly square (2px) everywhere -- there are no pills and no soft rounding. Type splits
cleanly: IBM Plex Sans for all display and body, IBM Plex Mono for labels/tags/code, used
sparingly (not as a decorative prefix on every heading -- see "Eyebrow labels" below). Light
Phosphor icons add graphic clarity without clutter. A calm sky blue (#aee3fd) is the only
secondary chromatic color, used for code surfaces and quiet highlights. Use Sunshine when the
content should feel confident and modern but polished -- launch pages, opinionated explainers,
comparisons, microsites -- like a professionally art-directed page, not a themed template.

## Emphasis levels (four surfaces, each with a distinct job)

Sunshine encodes emphasis through background surface, not through more color or more
decoration. There are exactly four levels -- pick the one whose job matches the content, don't
reach for a stronger one just because a section "feels important":

1. **Yellow surface** -- hero/header bands only. The loudest possible surface; reserved for the
   very top of the page (see "Yellow usage discipline" below). No dot-grid texture here -- a
   flat yellow surface is loud enough on its own.
2. **Dark (charcoal) surface** -- a genuinely major callout: a headline recommendation, a
   pull-quote, a single dark CTA band. No dot-grid texture here either -- reserve dark surfaces
   for their own weight. See "Dark Callout" under Components.
3. **Grey surface + dot-grid** -- the "aside" register: supporting info boxes, secondary
   callouts, side-column cards (e.g. "what would change this," "next action"). This is the
   ONLY place the dot-grid texture belongs -- a quiet, low-contrast grey dot field, never
   yellow or dark. See "The Dot Grid" below.
4. **Retro window card** -- a spotlight frame for one larger callout or focal figure (photo,
   diagram, screenshot) that deserves a "look here" treatment beyond a plain card. See "The
   Retro Window Card" below.

If unsure which level a section needs, default down a level, not up -- most content is level-2
in the plain sense (an ordinary white/light-gray card) or doesn't need any of these four at all.

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
| Paper White | `#ffffff` | `--color-paper-white` | THE default page surface -- body background for most sections |
| Ink | `#202020` | `--color-ink` | Primary text, headings, borders, and the shadow color |
| Near Black | `#333333` | `--color-near-black` | Secondary body text, nav links, muted labels |
| Electric Yellow | `#f0fb29` | `--color-electric-yellow` | RARE accent -- a hero/header band, one callout section, or a single small tag/icon/underline. Never the default background of an ordinary content section. See "Yellow usage discipline." |
| Light Gray | `#f5f5f5` | `--color-light-gray` | Neutral card/section surface for calmer passages -- this, not yellow, is the usual "alternate section" background |
| Charcoal | `#202020` | `--color-charcoal` | Dark section backgrounds and dark CTA fills (same hue as ink) |
| Border Gray | `#222222` | `--color-border-gray` | Hairline/solid borders on buttons, cards, inputs |
| Sky Blue | `#aee3fd` | `--color-sky-blue` | Secondary accent only -- code surfaces, inline highlights, quiet callouts |

Contrast rules: ink (#202020) or near-black (#333333) on white/electric yellow passes AA. On
charcoal/dark fills use paper white. Never put electric yellow text on white (fails contrast) --
yellow is a surface/accent, not a text color.

## Yellow usage discipline (read this before building anything)

This is the rule that most separates a professional Sunshine build from an amateur copy: **at
most ONE element should carry electric yellow in any given viewport.** Overusing yellow as a
backdrop is the single most common way this style goes wrong.

**Where yellow IS allowed (pick one per screen, not all of them):**
- A hero/header band at the very top of the page (the first thing a visitor sees).
- One callout or CTA section elsewhere on the page (e.g. a single mid-page banner) -- but if
  the hero already used yellow, prefer white/light-gray/charcoal for this instead of yellow again.
- A single small accent inside an otherwise white/gray/charcoal layout: one tag, one icon
  fill, one underline/highlight, one stat number. Small and singular, not a section fill.

**Where yellow is NOT allowed:**
- As the default page background (`body { background: ... }`) -- that reads as "we colored
  the whole template yellow," not "we used yellow deliberately." Default the page background
  to paper white or light gray.
- As the background of more than one full-width section on the same page.
- As the background of ordinary content sections: card grids, comparison tables, feature
  lists, footers. Footers in particular should be a plain white/light-gray/charcoal band.
- With the dot-grid texture on top -- dot-grid is reserved exclusively for grey aside/callout
  surfaces (see "Emphasis levels" and "The Dot Grid"); a flat yellow surface is loud enough on
  its own and never needs a texture layered on it.
- Stacked on an adjacent section that's ALSO yellow (immediate back-to-back yellow bands).

If you find yourself reaching for `--color-electric-yellow` a third time on a page, stop --
swap it for `--color-light-gray`, `--color-paper-white`, or `--color-charcoal` instead. Ask
"if I removed every yellow element but one, which one would still make the page feel
Sunshine?" -- keep only that one.

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

**Section-to-section rule: only add a border when two adjacent full-width sections share the
same background color.** A color change (white -> light-gray -> charcoal, etc.) is itself the
visual divider -- it doesn't also need a drawn line on top. A border earns its place only when
both sides are the same surface color and a seam is needed to say "these are still two distinct
regions" (e.g. two adjacent white sections, or a nav sitting on the same white as the content
below it). If the sections differ in background color, leave the border off entirely.

Reserve **2px** for genuine major horizontal dividers only, and only where the same-color rule
above says a border belongs there in the first place:
- A table's header bottom-border (the line under `<thead>`), because it's the one rule
  separating "column labels" from "all data."
- A rare same-color band-to-band seam (e.g. two consecutive white sections) where a stronger
  line is doing real structural work.

Do not use 2px for: button/card/tag/input outlines, in-card dividers (e.g. a spec list's
top rule), or a sticky nav's bottom border -- those should be 1px. If in doubt, default to
1px, and remember: no border at all beats a border sitting between two different-colored
sections.

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
- **Asymmetric content+aside grids:** default to a **2:1** column ratio (main:aside), not 3:1
  -- 3:1 reads cramped on the aside column. Only widen toward 3:1 if the aside content is
  genuinely minimal (a single short tag or icon).

## The Dot Grid (signature grey-surface texture) -- use sparingly

A field of small ink dots on a **grey** surface, evoking engineering/graph paper. This texture
is reserved exclusively for level-3 "aside" surfaces (see "Emphasis levels" above) --
supporting info boxes, secondary callouts, side-column cards. It never sits on the
electric-yellow hero surface or a dark/charcoal callout -- those two already carry their own
weight and don't need a texture on top, and a dot pattern under text hurts readability if it's
too dense. Use it in AT MOST one or two places per page.

**When to use it:**
- A grey "aside" card sitting next to the main content column (e.g. a "what would change
  this" or "next action" box beside a recommendation).
- A secondary/supporting callout that shouldn't compete with the page's one yellow hero moment
  or a dark CTA band.

**When NOT to use it:**
- Never on the electric-yellow surface, and never on a dark/charcoal surface -- grey only.
- Never behind long body copy or tables (hurts readability even on grey).
- Never on more than ~2 sections per page, and never two adjacent sections.
- Not on small components (buttons, tags, cards under ~300px).

**CSS -- dots via a single radial-gradient (drop-in):**
```css
/* Ink dots on a grey aside surface -- the ONLY approved dot-grid placement */
.dot-grid {
  background-color: var(--color-light-gray);
  background-image: radial-gradient(circle, rgba(32,32,32,0.32) 0.5px, transparent 0.6px);
  background-size: 20px 20px;      /* dot spacing; ~20px keeps dots legible under text */
  background-position: 0 0;
}
/* Keep text legible: prefer a solid inset panel on top of the grey dot field for dense text */
.dot-grid .panel { background: var(--color-light-gray); }
```
Keep the dot itself hairline (0.5px radius, transparent falloff at ~0.6px) and the spacing
loose (~20px) -- a tighter 1px dot / 14px spacing recipe reads as a busier texture that fights
with text sitting on top of it. Keep the alpha around 0.3-0.35 so foreground type stays
dominant.

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

## Icons -- Phosphor, Light weight only

Sunshine uses **Phosphor Icons, Light weight** (https://phosphoricons.com /
https://github.com/phosphor-icons/homepage) for all iconography -- thin, precise line icons
that match the mono/sans type contrast without adding visual noise. Never mix in a different
icon set or weight (no filled/bold/duotone Phosphor icons in this style -- Light only).

**How to include them in a self-contained HTML file (no build step):**

Preferred -- inline SVG (fully self-contained, no external request, styleable with
`currentColor` so it inherits ink/white automatically):
```html
<!-- Phosphor "coffee", Light weight, inlined -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor" width="24" height="24" aria-hidden="true">
  <path d="M82,56V24a6,6,0,0,1,12,0V56a6,6,0,0,1-12,0Zm38,6a6,6,0,0,0,6-6V24a6,6,0,0,0-12,0V56A6,6,0,0,0,120,62Zm32,0a6,6,0,0,0,6-6V24a6,6,0,0,0-12,0V56A6,6,0,0,0,152,62Zm94,58v8a38,38,0,0,1-36.94,38,94.55,94.55,0,0,1-31.13,44H208a6,6,0,0,1,0,12H32a6,6,0,0,1,0-12H62.07A94.34,94.34,0,0,1,26,136V88a6,6,0,0,1,6-6H208A38,38,0,0,1,246,120Zm-44,16V94H38v42a82.27,82.27,0,0,0,46.67,74h70.66A82.27,82.27,0,0,0,202,136Zm32-16a26,26,0,0,0-20-25.29V136a93.18,93.18,0,0,1-1.69,17.64A26,26,0,0,0,234,128Z"/>
</svg>
```
Fetch any icon's raw path data from the Phosphor core repo at build time:
`https://unpkg.com/@phosphor-icons/core@2/assets/light/<icon-name>-light.svg` (e.g.
`gauge-light.svg`, `drop-light.svg`, `check-circle-light.svg`) -- copy the `<path>` contents
into an inline `<svg viewBox="0 0 256 256" fill="currentColor">` in your page. A handful of
common ones are cached in this skill's `assets/icons/` folder for quick reuse.

Alternative -- icon font via CDN link (simpler markup, one extra network request, fine for a
quick draft): add to `<head>`:
```html
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/light/style.css" />
```
then use `<i class="ph-light ph-coffee"></i>` anywhere. Prefer inline SVG for anything meant
to last or go fully offline-capable; the font link is fine for a fast preview.

**Sizing & color:** default to 20-24px for inline-with-text icons, 32-40px for a standalone
feature icon. Icons inherit `color` via `fill="currentColor"` -- so an icon in ink text is
ink, an icon on a charcoal band is paper white, matching whatever text color surrounds it.
Never recolor an icon electric yellow as a fill (contrast/legibility); yellow icons are fine
only as a small stroke/accent on an already-yellow band.

**Where to use icons:** a small icon beside a stat/feature label, a check/x in a comparison
list, a light bulb/gauge/etc next to a callout, nav or footer link icons, a single hero icon
next to the eyebrow. Use them to add clarity (what kind of thing is this row/section) not
as pure decoration on every line -- a page with an icon on literally everything reads as
noisy as a page with none.

## Components

### Primary Button (sharp, flat -- NO hard-offset shadow)
Fill `--color-ink`, text `--color-paper-white`, `border-radius: 2px`, border `1px solid #202020`,
padding `12px 20px`, `--font-mono` 14px/500, **`text-transform: uppercase`**. **No box-shadow.**
Hover: darken/lighten the fill slightly (e.g. `filter: brightness(1.15)`) or invert to an
outline -- do NOT use the hard-offset "press" shadow on buttons; that's reserved for cards and
the retro window (see "Where hard shadows go" below). NEVER pill-shaped.

### Secondary Button (outline)
Background transparent or `--color-paper-white`, text `--color-ink`, `border-radius: 2px`,
border `1px solid #222222`, same padding + mono label, **uppercase**. No shadow. Sharp corners.

All button labels are UPPERCASE (the mono label, letter-spacing, and all-caps together are
what make the button read as a mono "control" rather than a link) -- put `text-transform:
uppercase` on the shared `.btn` base rule so every variant inherits it.

**Never let button text wrap.** Buttons must render on one line at every viewport width down
to a 375px phone. Set `white-space: nowrap` on `.btn`, keep labels short (2-4 words), and if a
button sits in a flex row that could get tight (e.g. a nav bar), give the row `flex-wrap: wrap`
on the CONTAINER (so buttons drop to a new row as a whole) rather than letting text wrap
inside a single button. Verify this by hand at 375px and 768px widths (see the mandatory
device-size check in SKILL.md) -- wrapped button text is one of the most common and most
amateur-looking responsive bugs.

**Where hard shadows go:** the flat 8px/4px hard-offset shadow (`--shadow-hard-lg` /
`--shadow-hard-sm`) is a CARD and retro-window signature, not a button one. Putting it on
every button is a big part of why an earlier pass of this style felt like a busy knockoff --
reserve it for the handful of elevated surfaces (cards, stat blocks, the retro window, the
footer panel), and keep buttons flat so the shadow still means something when it appears.

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

### Dark Callout
**Role:** Level-2 emphasis (see "Emphasis levels") -- a genuinely major callout: a headline
recommendation, a pull-quote, a single CTA band. Background `--color-charcoal`, text
`--color-paper-white`, `border-radius: 2px`, border `1px solid var(--color-ink)`, generous
padding (32-48px). **No dot-grid texture** -- the dark surface itself carries the weight;
layering texture on top just fights the flat, confident-charcoal look. Use at most one per
page.

### Retro Window Card
**Role:** A single framed focal figure — highlight photo, diagram, screenshot, or a set-apart
sidebar explanation. See "The Retro Window Card" section for full CSS + usage. Square box, 1px
ink border, 8px hard-offset shadow, a bottom-bordered title bar (outlined dots and/or a mono
title) over a 24-32px padded body. Use at most one or two per page — it is a spotlight.

### Eyebrow Label / Tag
`--font-mono` 12-14px/500, letter-spacing 0.5px, uppercase optional. As a tag: 2px radius,
1px solid border, 2-8px padding. Great sitting above an h2/h3 to label a section.

**Don't prefix every eyebrow with `//`.** A leading `//` (or any single repeated glyph) reads
as a designer's one signature flourish the first time and a tic by the fifth -- overusing it is
one of the fastest ways this style reads like an amateur copy rather than an original hand. Use
it sparingly (at most once or twice on a page, e.g. a single "// nerd corner" aside), and let
most eyebrows just be a plain uppercase mono label with no punctuation prefix (`SECTION NAME`,
not `// Section Name`).

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
- Default the page to paper white / light gray; treat electric yellow as a rare, single-use
  accent (hero OR one callout OR one small tag/icon -- see "Yellow usage discipline").
- Keep ALL corners at 2px (max 8px for large media). Sharp is the identity.
- Use flat hard-offset shadows (solid ink, 0 blur) on CARDS and the retro window only --
  never on buttons, which stay flat with no shadow.
- Pair IBM Plex Sans (display/body) with IBM Plex Mono (labels/tags/code) -- lean on that contrast.
- Set every button label to uppercase (`text-transform: uppercase` on the shared `.btn` base)
  and never let button text wrap (`white-space: nowrap`; verify at 375px).
- Keep borders 1px by default; reserve 2px only for major band-to-band section dividers and a table's header rule.
- Apply heavy negative letter-spacing to large headings (-2px to -6px) for the confident look.
- Reserve the dot grid exclusively for grey level-3 aside surfaces (never yellow, never
  dark/charcoal -- see "Emphasis levels" and "The Dot Grid"); keep dots hairline and loose
  (~0.5px dot / ~20px spacing default).
- Keep sky blue secondary -- code surfaces and quiet highlights only.
- Use Phosphor Light-weight icons to add clarity at a glance (stats, comparison checks,
  callouts) -- see "Icons" section.
- Check every build on iPhone (375px) and iPad (834px/1194px) widths before calling it done
  (see SKILL.md's device-size check) -- catches wrapped buttons and other responsive bugs.

### Don't
- NEVER use pills or fully rounded controls, and never radii between 2px and 8px -- no soft
  "friendly" rounding. Sunshine is sharp.
- Never use soft/blurred shadows (any blur or spread > 0) -- the shadow vocabulary is flat offset only.
- Never put a hard-offset shadow on a button -- that's a card/retro-window signature only.
- Never set electric yellow as the default page/section background, never use it on more than
  one element per viewport, and never put ink/near-black text on a busy dot grid without a
  solid panel behind it.
- Don't overuse the dot grid, and never put it on yellow or dark/charcoal surfaces -- grey
  aside boxes only; never adjacent sections; never behind body text/tables.
- Don't introduce a third chromatic color -- the system is yellow + ink + one sky blue.
- Don't render display or body text in the mono face (mono is for labels/tags/code), and don't
  set headings below weight 500.
- Don't prefix every eyebrow/label with `//` -- use it once or twice at most, not as a
  running tic on every heading.
- Don't mix icon sets or weights -- Phosphor Light only, and don't decorate every single line
  with one; use icons where they add meaning.

## Surfaces

| Level | Name | Value | Purpose |
|-------|------|-------|---------|
| 1 | Paper White | `#ffffff` | THE default page background for most sections |
| 2 | Neutral | `#f5f5f5` | The usual "alternate section" background (not yellow); the only surface the dot-grid texture belongs on (aside/secondary callouts -- see "The Dot Grid") |
| 3 | Yellow Accent | `#f0fb29` | RARE: one hero/header band, or one callout, or a single small tag/icon -- never more than one per viewport |
| 4 | Charcoal | `#202020` | Dark sections / dark CTA fills (paper-white text) |
| — | Border | `#202020` / `#222222` | Solid 1px borders (2px reserved for major dividers) and the shadow color |
| — | Sky | `#aee3fd` | Secondary: code surfaces + quiet highlights |

## Imagery
Prefer bold, graphic visuals: high-contrast product shots on white cards (2px radius, hard
shadow), Phosphor Light-weight icons in ink (never multicolor, never mixed weights), and the
dot grid as texture only on grey aside/callout surfaces (never yellow or charcoal -- see
"Emphasis levels"). Keep image density moderate -- type and color do the heavy lifting. No soft
drop shadows on images; if an image needs elevation, give it the flat hard-offset shadow like a
card.

**Section-lead images (a different treatment from the card above):** when an image sits at the
top of a section as its lead visual -- not inside a card grid -- skip the border/shadow card
treatment entirely. Let it sit directly on the page, constrained to its own column's width (not
full-bleed across the section), and give it explicit top and bottom margin (e.g. 24px/32px) --
a bare image doesn't get breathing room by default the way a padded card does, so set that
margin intentionally or it reads cramped against surrounding text.

**Custom illustration (via the nano-banana skill):** when a page needs a bespoke figure rather
than a photo or icon -- a hero character, a diagram, a scene -- generate it with the nano-banana
skill in a hand-drawn pen-and-ink line style with a light sci-fi bent: organic, slightly
imperfect line quality (like a real pen sketch), never a clean vector/clip-art look. Request a
plain white or transparent background so it drops cleanly onto any Sunshine surface; if the
model returns visible background tint or stray artifacts, do a cleanup pass (flatten to pure
white, patch stray marks) before locking the asset in as a reusable canonical version. Treat
these illustrations as section-lead figures per the paragraph above -- no card border/box.

## Layout
Max-width ~1200px on a paper-white canvas (yellow only where the "Yellow usage discipline"
section allows it -- typically the hero). Sticky top nav: wordmark left (Sans 600 or mono
label), nav links (mono 14px), a sharp primary button right (flat, no shadow, `white-space:
nowrap`). Hero is oversized Sans 500 with heavy negative tracking, left-aligned or split 50/50
with a card/visual; a sharp primary + outline secondary button pair beneath (never let button
labels wrap). Sections alternate white and light-gray card clusters, with the occasional
charcoal band -- yellow appears at most once more on the page, in a single callout. Footer is
a plain white/light-gray/charcoal band with mono labels -- never yellow, and never dot-grid
(dot-grid is reserved for grey aside/callout boxes, not full-width bands like the footer).
Generous 64-96px section rhythm.

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
