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

- The grain over the whole page is a tileable image laid over everything by `body::after` in `index.html`. **The live
  opacity is 8%**, set by the editor tweak `:root { --grain: 0.08 !important; }`; the base token in `:root` is `.4`
  and the tweak overrides it. The editor's Grain slider edits that tweak.
- **The grain is shown at `--grain-size: 1126px`**, i.e. the 563px file enlarged 2x on purpose, so it is coarse and a
  little soft like a riso print. There is **no sharper retina version**: don't add a `@2x` file or a script that swaps
  one in (the softness is the look, and the 380KB file pushed mobile LCP from 2.3s to 5.8s when it loaded up front).
- One file, `assets/images/paper-texture.webp` (563px, ~110KB). Each pixel is **black with alpha = 255 − the grey
  texture**, which looks exactly like multiplying the grey texture over the page but needs no `mix-blend-mode` (a
  blend mode roughly doubled scroll frame times in testing; don't switch back to one). It sits above everything
  (`z-index: 9999`, `pointer-events: none`) and is hidden for increased contrast, forced colours and print.
- The supplied tile had a gentle light-to-dark gradient that showed as bands at every tile edge, so its low-frequency
  lighting was flattened (the fine grain is untouched). If the texture is ever replaced, check it for the same thing
  (tile it 2x2, blur it and boost the contrast: the seams show) and regenerate the black-alpha file from the grey tile
  (alpha = 255 − grey, 563px, WebP quality 60, alpha_quality 50).
- `--paper` (`#fffdf8`) was lightened to offset the ~4.5% the texture darkened the page at 40% opacity. At the live 8%
  the texture only darkens it ~1%, so the page averages lighter than `--bg` (#F2EEEA). To get back to `--bg` on
  average, set `--paper` to about `--bg / (1 − 0.134 × --grain)` (≈ `#f5f1ec` at 8%); the grid inks multiply over
  `--paper`, so they would shift with it.

## Site structure

- Every folder other than `assets/` and `editor/` (`portfolio/`, `ai-*`, `nhb-games/`, `slow-food-*`, …) is a ~400-byte
  redirect stub to `https://hello.ct907.com/<name>/`. The real pages for those live on that other site, outside this
  repo. So today only `index.html` has typography to maintain here; apply the rule above to any real page added to this repo.
