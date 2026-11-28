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
- **Overprint style (the CodePen "riso" look), switched in the editor.** The plates can also print the way real riso inks do: the
  heading's own text becomes a third ink (cyan), and the yellow and magenta plates print **over** it with `mix-blend-mode: multiply`,
  so overlaps mix (yellow x cyan = green, all three = near-black, fringes of each ink at the edges). It is built from five tokens in
  `:root` whose defaults are exactly the classic look, so nothing changes until the editor writes others: `--riso-z` (-1 plates behind
  the text, 1 over it), `--riso-blend` (`normal` / `multiply`), `--riso-ink` (`currentColor` = the text keeps its colour; overprint
  uses `#1a84c4`), `--riso-mask` (the grain tile, or `none` for solid ink) and `--riso-grain-size` (default `var(--grain-size)`).
  The ghosts are still only `::before` / `::after`, so the third ink *is* the heading text (it is solid: the grain is on the two
  plates, not the text). The multiply stays inside each heading's own `isolation: isolate` group, so it only mixes the plates with the
  text and each other, never with the page behind. Increased contrast, print and forced colours hide the plates **and** reset the text
  to the page's ink (`[data-riso] { color: inherit }`), and `--riso-ink` is reset in the `prefers-contrast: more` block so the editor
  writes it inside the no-preference guard. The cyan ink alone is ~3.9:1 on the paper (fine for large display text); where the plates
  overlap it is near-black. A per-heading `--riso-*-x/-y/-a` always wins over the global sliders (the page ships several, tuned for
  classic), which is why the editor has a **Clear their own settings** button. `portfolio/index.html` carries the same tokens at their
  classic defaults (no editor there).
- The editor's **Page & background > Header riso** has a **Style: Classic | Overprint** switch (a live preview: Overprint writes
  `--riso-z: 1`, `--riso-blend: multiply`, `--riso-ink: #1a84c4`, opacity .85 and 3px/3px shifts; Classic puts the shipped values back,
  and each style remembers its own settings while you flip), the three global sliders, ink colours, Blend, Grain on/off and size, and
  selecting a heading shows **Riso plates (this heading)** with X/Y/opacity per plate plus text ink, Blend, Plates over/behind and Grain. A text shadow typed on a heading (the Text shadow control) is an extra
  flat shadow on top. Everything is off for increased contrast, forced colours and print. Browser support: Chrome 120+,
  Safari 16.4+, Firefox 128+ for the textured ghosts.

## Baked riso photos (`tools/riso-bake.py`)

- Photos get the riso look **baked into the file**, not applied live: an SVG-filter version (the displacement-noise CodePen) cost ~5x
  the frame budget when measured, and masking photos with the grain texture at runtime was also costly. Baking costs nothing at runtime.
- `python3 tools/riso-bake.py photo.jpg --preset soft|overprint|duo --display-width 300` (Python + numpy + Pillow; a dev tool, the site
  still has no build step). It separates the photo into the heading inks (cyan, magenta, yellow), breaks them up with grain, prints
  yellow up-left and magenta down-right like the heading plates, and multiplies them onto `--paper`. `duo` uses only the wallpaper's
  blue and pink. Photos use a lighter cyan (`#2aa5df`) than the headings' `#1a84c4`, which goes muddy over a whole picture.
- **Don't use `paper-texture.webp` as the ink threshold.** It has a regular fine mesh under its speckle: invisible as an 8% overlay,
  but it prints as a halftone screen. The tool uses synthetic speckle (shared across the three plates, like a real print) instead.
- Grain compresses badly: baked photos come out roughly 1-3x the size of the originals. Check sizes (LCP, see the texture notes
  above) and use `--quality` / `--grain` if a file is too heavy. Keep the original as the source; commit only the baked WebP.
- Not applied to the site yet: the homepage's photos are hosted on Readymag's CDN, so using one means committing the baked file under
  `assets/images/` and swapping its `src` (the editor's **Replace image...** does both in one pull request).

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

## Frosted glass and the title animation

- **Blur has two tokens.** `--blur` (4px) is for *clickable* plates (links, buttons, the album card) and `--blur-static` (24px) for
  every other frosted plate (headings, paragraphs, labels, the footer name…). One rule does it:
  `.glass:not(a, button, .release) { --blur: var(--blur-static) }`, set on the plate itself so it also beats a `--blur`
  inherited from a section (`#ux-portfolio { --blur: 2px }` still sets the UX section's links). A per-element `--blur`
  from the editor (the **Bl** field) still wins. 24 means 24 CSS px; Figma's "background blur 24" would be 12px here.
  The larger radius costs a little more scroll time in a software-rendered test (more slow frames, same median); the
  grain's overlay blend and the plates themselves are the bigger cost.
- **The CHRIS TAN title animates its weight** (`h1 { animation: weight 6s infinite }`, 300 ↔ 700, in `index.html`). An
  `!important` `font-weight` on the h1 beats any animation, so the editor's Weight control on the title (it writes
  `font-weight: N !important`) freezes it, as `font-weight: 600 !important` did until it was removed from the tweak block.
  The editor's preview always runs with motion reduced, so the animation is only seen on the real page.

## Site structure

- `index.html` (homepage) and `portfolio/index.html` are real pages. Every other folder besides `assets/` and `editor/`
  (`ai-*`, `nhb-games/`, `slow-food-*`, …) is a ~400-byte redirect stub to `https://hello.ct907.com/<name>/`. The real pages
  for those live on that other site (Readymag), outside this repo. Apply the typography rule above to any real page added
  to this repo. To migrate another Readymag page, replace its stub with the real page (keep the same folder name, so old
  links keep working).
- **`portfolio/index.html`** was migrated from the Readymag page `hello.ct907.com/portfolio` (the CHRIS TAN landing page
  with the project list and contact details) and then restyled to **look like the homepage**. It is a standalone file with
  its own inline CSS and no editor support (the editor only manages `index.html`).
  - **It copies the homepage's design system, it does not share it.** From `index.html`, with the homepage's *live* values:
    the `:root` tokens (palette, `--ink-c` #cdf6ff / `--ink-m` #f6ecf5, `--grain` .08, riso and glass tokens), the fluid
    root font size and `--pad`, the grid + grain layers, `.glass` plates and their soft edges, the riso heading plates, the
    animated h1 weight, `.arrow-link`, `.label`, `.badge`, the footer, the reduce-motion toggle, reveal-on-scroll, the hover
    and press tints and the contrast / print / forced-colours fallbacks. **If you change any of those in `index.html`,
    change the copy in `portfolio/index.html` too.** (Pulling them into shared files under `assets/` would remove the
    duplication, but it means refactoring `index.html`, which the editor reads and writes; not done.)
  - **Not copied:** the liquid cursor effect (the lens that follows the pointer and the poured hover tint) — hover and press
    use the plain CSS tints the homepage itself falls back to on touch — and the editor's per-element `translate` nudges.
    From 1100px the editor's live *values* are reproduced as plain rules in the "desktop values" block (stronger yellow
    plate and a 40% magenta plate on h1, h2 and the sub-headline, light 300 weights, Merriweather on the greeting, the
    riso decor shapes in place of the badges, 2px blur on link plates).
  - Riso plates apply to `h1`, `h2` and `.lede` only. The period labels are `h3.label` (small uppercase plates like the
    homepage's `.label`), which deliberately get no riso plates; labels never do.
  - Fonts follow the standing rule through the same `--display` / `--text` tokens, but here **Merriweather is the `--text`
    token itself from 1100px up** (`@media (min-width: 1100px) { :root { --text: "Merriweather", … } }`), with its own
    `<link media="(min-width: 1100px)">`. So there are no per-element Merriweather rules to maintain.
  - Orange text uses `--accent-text` (#c2370f, 4.7:1 on `--bg`) because the accent #ff6546 is only 2.5:1; the accent stays
    for arrows and shapes. Keep any text at 4.5:1 or better.
  - Layout: the hero is a two-column grid (text stack | tilted portrait) that stacks at **960px**, not the homepage's 720px:
    beside the portrait the title wraps on a tablet. The toggle shares the homepage's `ct907-motion` key, so a visitor's
    choice carries over between the two pages.
  - The portrait is `assets/images/chris-tan-profile.webp` (696×600, the same crop Readymag used). The decor shapes are the
    homepage's `riso-shapes-deco-copy-4` / `-copy-2` images; they are `display: none` (so never fetched) below 1100px, where
    the grey `.badge` squares show instead, as on the homepage.
  - The footer adds a "Home" link (the Readymag page had no way back); Instagram, Linktree and Email are the homepage's.
  - The eight project links are root-relative (`/nhb-games/` …), so they go through the redirect stubs today and start
    pointing at the real pages automatically once those are migrated.
