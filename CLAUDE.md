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

- `h1`, `h2` and `.lede` (the big sub-headline) have a **yellow plate up-left (up to 2px) and a magenta plate down-right (up to 4px),
  both at 20%, carrying the paper-grain texture** (so they look like ink on paper). Body text, labels and buttons don't have it.
- Each plate is a pseudo-element (`::before` yellow, `::after` magenta) printing a copy of the heading's text
  (`content: attr(data-riso)`), shifted with `translate`, coloured with `rgb(from var(--riso-yellow) r g b / alpha)` and masked
  by `assets/images/paper-texture.webp` as a **luminance** mask at `--grain-size`: the grain's dark specks let the paper show
  through the ink. The script at the bottom of `index.html` writes the text into `data-riso` and keeps it current (a
  MutationObserver, because the editor retypes headings and adds copies of them) and measures `--riso-dy`, how far the real text
  sits below where a plain line would put it (the sub-headline's raised caret makes its first line taller), so the ghost lines up.
  It only tags a heading when the browser has `rgb(from …)` and `mask-image`; otherwise the heading keeps the **flat**
  `text-shadow` plates the CSS also defines (so does no-JS).
- **The card title (`.release h3`) keeps the flat plates on purpose**: its card-wide link is `h3 a::after { position: absolute;
  inset: 0 }`, which only covers the card while the h3 is not positioned, and the ghosts need a positioned host.
- Tokens in `:root`: `--riso-yellow` (#ffe600), `--riso-magenta` (#ff3d9a), `--riso-yellow-shift` (2px), `--riso-magenta-shift`
  (4px), `--riso-text` (.2). One heading can override the plates with `--riso-yellow-x/-y/-a` and `--riso-magenta-x/-y/-a`
  (offset px, opacity); they are deliberately **not** declared in `:root`, so the plates fall back to the shifts and `--riso-text`.
  Today's tweak block gives the headings (h1, sub-headline, three h2) a yellow-only plate at -2px/-1px by that route (the
  magenta plate is `--riso-magenta-a: 0`); remove that override to bring the magenta plate back.
- The editor's **Page & background > Header riso shift** has the three global sliders, and selecting a heading shows **Riso
  plates (this heading)** with X/Y/opacity per plate. A text shadow typed on a heading (the Text shadow control) is an extra
  flat shadow on top. Everything is off for increased contrast, forced colours and print. Browser support: Chrome 120+,
  Safari 16.4+, Firefox 128+ for the textured ghosts.

## Page editor: structural edits (`editor/index.html`)

- **Selection.** `sel` is the active element, `selMore` the rest of a multi-selection; `setProp` / `resetProps` / `isTweaked`
  act on all of them when called without an element, and moves, nudges and the X/Y/W/H fields loop over `targets()`.
  Shift+click = a run of like elements, Ctrl/Cmd+click = toggle, Alt+click = innermost (Ctrl/Cmd+click used to mean that).
- **Deleting** an existing element marks it in `state.deleted` (path from `<body>`, tag/id/classes, a text fingerprint) and
  hides it in the preview with `data-ed-del`; the node stays in the DOM, so paths and selectors keep their meaning. On push
  it is cut from the HTML **last** (descending path order, ignoring layers placed in the same push) and the browser must
  read back exactly that many fewer elements. Rules keyed with `:nth-child` are rewritten for the page without it
  (`rekeyForDeletions`, using a detached copy of the preview).
- **Duplicating** creates a layer of kind `clone` (class `ed-copy-xxxx`, markup saved at click time, ids made unique). Layers
  and copies change what `:nth-child(k)` means for later siblings in the preview, so every structural change goes through
  `withRekey`, which renames the rules, text edits and picture swaps that depend on a position (`state.renames` remembers
  that a renamed baseline rule is not a change of its own). `originals` / `imgOrig` are keyed by element, not selector, for
  the same reason. Don't store selectors across a structural change.
- Source edits happen in this order in `buildNewSource`: text, pictures, new layers and copies, removal of pushed layers,
  deletions, then the managed style block. Path lookups in the source skip layers already placed in that push (`srcAt` with `ign`).

## Site structure

- Every folder other than `assets/` and `editor/` (`portfolio/`, `ai-*`, `nhb-games/`, `slow-food-*`, …) is a ~400-byte
  redirect stub to `https://hello.ct907.com/<name>/`. The real pages for those live on that other site, outside this
  repo. So today only `index.html` has typography to maintain here; apply the rule above to any real page added to this repo.
