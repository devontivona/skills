# Nano Banana prompt patterns

Ported from the official extension's `/icon`, `/diagram`, `/pattern`, `/story`, `/restore`,
and `/generate` style options. These are PROMPTS for the `generate`/`edit` commands — there
are no special subcommands. Fill the brackets, keep prompts specific.

## Generation styles (append to any generate prompt)
photorealistic · watercolor · oil-painting · sketch · pixel-art · anime · vintage ·
modern · abstract · minimalist · line-art · 3d-render · isometric · flat-vector

## Variations to request (for --n multiples or successive runs)
lighting (dramatic/soft) · mood · color-palette · angle/perspective · season · time-of-day

## Aspect ratios (via --aspect)
1:1 (icons, avatars) · 16:9 (banners, slides) · 9:16 (stories/phone) · 4:3 · 3:4 (portrait) · 21:9

---

## Icons / favicons / logos / UI elements
Run once per size (Nano Banana renders one canvas; don't expect a sprite sheet). For an icon SET,
loop sizes and post-resize if needed.

- App icon:
  `"App icon: <subject>. <style, e.g. flat, rounded-square, gradient> style. Centered, simple,
   bold silhouette, solid <color> background, no text, high contrast, crisp edges."` --aspect 1:1
- Favicon: same but `"...extremely simple, legible at 16x16, single focal shape, no fine detail."`
- Logo:
  `"Logo for <name/idea>: <style> wordmark/lettermark, <palette>, vector, clean negative space,
   white background, scalable."` --model pro  (pro renders text best)
- UI element:
  `"UI <icon name> icon, <minimal|outline|filled> style, 1px-feel strokes, single color <hex>,
   transparent-look background, pixel-aligned."`

## Diagrams / flowcharts / architecture / database (use --model pro)
- Flowchart:
  `"Clean flowchart diagram of <process>. Left-to-right, labeled boxes and arrows, <professional|
   hand-drawn> style, readable sans-serif labels, white background, balanced spacing."`
- Architecture:
  `"System architecture diagram: <components & relationships>. Boxed services, directional arrows,
   grouped tiers, legend, neutral palette, crisp labels, technical/professional look."` --aspect 16:9
- Database schema:
  `"Entity-relationship diagram for <domain>: tables with field lists, primary/foreign keys,
   crow's-foot relationships, hierarchical layout, monospaced field names, white background."`
- Tip: spell out every node/edge explicitly in the prompt; pro for legible text.

## Patterns / textures / wallpaper
- Seamless pattern:
  `"Seamless tileable <motif> pattern, <geometric|floral|organic> style, <palette>, even density,
   edges that wrap perfectly, flat, no shadows."` --aspect 1:1
- Texture:
  `"Seamless <material, e.g. wood grain / concrete / linen> texture, natural variation, tileable,
   neutral lighting."`
- Wallpaper:
  `"Repeating <motif> wallpaper, <sparse|medium|dense> density, <palette>, balanced composition."`

## Photo restoration / enhancement (edit command)
- `edit --image old.jpg --prompt "Restore this photo: remove scratches, dust and tears, repair
   creases, denoise, sharpen, correct fading and color cast, keep faces and details natural —
   no added content."` --model pro
- Colorize: `"...colorize this black-and-white photo with realistic, period-accurate colors."`

## Image editing (edit command)
- Add/remove: `"add <thing> to <where>"` / `"remove <thing>, fill background naturally"`
- Restyle: `"restyle as <style> while keeping composition and subject"`
- Background: `"replace background with <scene>, match lighting and perspective"`
- Compose (multi-image): pass several `--image` files: `"place the product from image 1 onto the
   scene in image 2, realistic shadows and scale"`

## Visual story / step sequence
No native multi-frame call — generate frames one-by-one with a shared style suffix for consistency,
numbering outputs. Template per frame:
`"Step <i> of <n>: <what happens this step>. <consistent style + palette + character description
 repeated every frame>. Same art style as the series."`
Types: process · tutorial · timeline · before-after · narrative.
Keep a constant "style block" string and append it to every frame's prompt so the set matches.
