# ct907-site: project notes

Static site for ct907.com (GitHub Pages, no build step). `index.html` is the homepage. `editor/` is a browser-based visual
editor for it (see `editor/README.md`).

## Typography (standing rule)

- **Headings and display text use Signika. Body text uses Merriweather at desktop width (1100px and up) and Lora below
  that** (phones and tablets).
- This applies to **all pages of the website except the Slow Food Album pages**, which already have a strong aesthetic
  identity of their own and keep their own fonts. Do not restyle them.
  - Slow Food Album pages = `slow-food-album/` and `slow-food-recipe-1/` … `slow-food-recipe-4/` (and their live
    versions at `hello.ct907.com/slow-food-*`). If a page is borderline, ask before touching its fonts.
  - The homepage's own "Slow Food" release card is homepage content, so it follows the homepage fonts.
- In `index.html` the base roles are two tokens in `:root`: `--display` (Signika: headings, hero text, labels, card
  titles, footer name) and `--text` (Lora: body copy, links, buttons). Both are loaded by one Google Fonts `<link>` in
  `<head>` (`Lora:wght@400..700` and `Signika:wght@300..700`). Any new page should define the same two roles the same way.
- **Merriweather at desktop width is applied by the page editor**, not by a token: about 14 `font-family: "Merriweather"`
  rules (with weights 300–600) inside the editor's managed block (`editor tweaks`, inside `@media (min-width: 1100px)`),
  and its own `<link>` between the `editor fonts` markers. `--text` is still Lora. A few body elements are not covered by
  those rules and stay Lora at desktop: the three hero arrow links and their asides, and the first `.label`. Leave
  them unless asked. If Merriweather is ever promoted to a token, make it `--text` (and fix `.release .meta` /
  `.release .latest`, which use `--display` and are the only rules that need the editor's `!important`).
- Weights: Signika is 300–700, Lora 400–700 and Merriweather 300–900 (variable); don't use weights outside those (the
  title's weight animation runs 300↔700). The page uses no italics, so no italic font files are fetched (the
  Merriweather link includes the italic axis; add `ital` to the Lora link if italics are introduced).
- Tracking: Signika is narrower than the Josefin Sans it replaced, so display text uses only about -.01em to -.015em of
  negative letter-spacing. Don't reuse the old -.05em / -.06em values.
- Not covered by the rule: the editor's own interface (`editor/`) is a tool rather than a site page and keeps its system
  UI font.

## Paper texture

- The grain over the whole page is a tileable greyscale image laid over everything by `body::after` in `index.html`,
  blended with **`mix-blend-mode: overlay`** (so its dark specks darken the page and its white highlights lift it).
  **The live opacity is 8%**, set by the editor tweak `:root { --grain: 0.08 !important; }`; the base token in `:root`
  is `.4` and the tweak overrides it. The editor's Grain slider edits that tweak.
- **The grain is shown at `--grain-size: 1126px`**, i.e. the 563px file enlarged 2x on purpose, so it is coarse and a
  little soft like a riso print. There is **no sharper retina version**: don't add a `@2x` file or a script that swaps
  one in (the softness is the look, and the 380KB file pushed mobile LCP from 2.3s to 5.8s when it loaded up front).
- One file, `assets/images/paper-texture.webp` (563px, ~110KB, plain greyscale: white = lifts, mid-grey = no change,
  dark = darkens). It sits above everything (`z-index: 9999`, `pointer-events: none`) and is hidden for increased
  contrast, forced colours and print.
- **What overlay looks like.** Overlay moves a pixel by at most (1 − its brightness) either way, so on the near-white
  paper (`--paper` `#fffdf8`) the grain is almost invisible, while on mid-tones (photos, the blue picture, grid lines,
  the accent arrows) the white highlights show clearly. At the live 8% it is barely visible anywhere; ~30–60% shows it,
  and 100% washes the grid and picture out. A darker `--paper` (e.g. `#f2eeea`) gives it more room on the paper but
  looks greyer. Black text stays black (overlay on black is black).
- **Cost.** Overlay needs a real blend mode, so the browser re-composites the whole page every frame. In a
  software-rendered headless Chromium this took scroll frames from ~17ms to ~33ms median on desktop (no change in the
  throttled phone test); it does not depend on opacity, tile size or layer size. Real GPUs should be much cheaper but it
  has not been measured on one: check a mid-range phone. The earlier cheaper version (black pixels with alpha = 255 −
  grey, normal blending) is exactly equivalent to *multiply*, not overlay, and costs nothing; go back to it if the
  highlights aren't worth the cost.
- The supplied tile had a gentle light-to-dark gradient that showed as bands at every tile edge, so its low-frequency
  lighting was flattened (the fine grain is untouched). If the texture is ever replaced, check it for the same thing
  (tile it 2x2, blur it and boost the contrast: the seams show), and save it as a 563px greyscale WebP (quality ~70).
- `--paper` (`#fffdf8`) was lightened to offset the ~4.5% a multiplied texture darkened the page at 40% opacity. Under
  overlay at the live 8% the texture nudges the page lighter by ~0.5 level, so the page averages lighter than `--bg`
  (#F2EEEA), roughly `#FCFAF5`. Retune `--paper` (the grid inks multiply over it, so they would shift with it) if the
  exact background matters.

## Riso shift on headings

- `h1`, `h2`, `h3` and `.lede` (the big sub-headline) have two hard-edged `text-shadow` plates behind the text, like
  off-register riso printing: **yellow up-left by up to 2px and magenta down-right by up to 4px, both at 20%**. One
  rule in `index.html` (next to the paper texture); body text, labels and buttons don't have it.
- It is driven by tokens in `:root`: `--riso-yellow` (#ffe600), `--riso-magenta` (#ff3d9a), `--riso-yellow-shift` (2px),
  `--riso-magenta-shift` (4px) and `--riso-text` (.2, the opacity of both). The editor's **Page & background > Header
  riso shift** has sliders for the two shifts (0–2px, 0–4px) and the opacity (0 switches it off); the colours are in
  Design tokens. Those are site-wide and apply at every width, so change them there rather than with per-element tweaks.
- Colours get their opacity with `rgb(from var(--riso-yellow) r g b / var(--riso-text))` (relative colour syntax:
  Chrome 119+, Safari 16.4+, Firefox 128+; older browsers just show no ghosts). It is off for increased contrast, forced
  colours and print. A per-element `text-shadow` tweak from the editor overrides it on that element.

## Site structure

- Every folder other than `assets/` and `editor/` (`portfolio/`, `ai-*`, `nhb-games/`, `slow-food-*`, …) is a ~400-byte
  redirect stub to `https://hello.ct907.com/<name>/`. The real pages for those live on that other site, outside this
  repo. So today only `index.html` has typography to maintain here; apply the rule above to any real page added to this repo.
