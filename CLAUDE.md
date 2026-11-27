# ct907-site: project notes

Static site for ct907.com (GitHub Pages, no build step). `index.html` is the homepage. `editor/` is a browser-based visual
editor for it (see `editor/README.md`).

## Typography (standing rule)

- **Headings and display text use Signika. Body text uses Lora.**
- This applies to **all pages of the website except the Slow Food Album pages**, which already have a strong aesthetic
  identity of their own and keep their own fonts. Do not restyle them.
  - Slow Food Album pages = `slow-food-album/` and `slow-food-recipe-1/` … `slow-food-recipe-4/` (and their live
    versions at `hello.ct907.com/slow-food-*`). If a page is borderline, ask before touching its fonts.
  - The homepage's own "Slow Food" release card is homepage content, so it follows the homepage fonts.
- In `index.html` this is two tokens in `:root`: `--display` (Signika: headings, hero text, labels, card titles, footer
  name) and `--text` (Lora: body copy, links, buttons). Both are loaded by one Google Fonts `<link>` in `<head>`
  (`Lora:wght@400..700` and `Signika:wght@300..700`). Change fonts by editing those, not element by element. Any new page
  should define the same two roles the same way.
- Weights: Signika is 300–700 and Lora 400–700; don't use weights outside those (the title's weight animation runs 300↔700).
  The page uses no italics, so Lora italic is not loaded: add `ital` to the font link if italics are introduced.
- Tracking: Signika is narrower than the Josefin Sans it replaced, so display text uses only about -.01em to -.015em of
  negative letter-spacing. Don't reuse the old -.05em / -.06em values.
- Not covered by the rule: the editor's own interface (`editor/`) is a tool rather than a site page and keeps its system
  UI font.

## Paper texture

- The grain over the whole page is a tileable greyscale image, multiplied at 40% by `body::after` in `index.html`:
  `assets/images/paper-texture.webp` (563px, regular screens, ~110KB) and `paper-texture@2x.webp` (1125px, retina,
  ~380KB), picked with `image-set()`. `--grain` is the opacity, `--grain-size` the tile size in CSS px (563px).
- The supplied tile had a gentle light-to-dark gradient that showed as bands at every tile edge, so its low-frequency
  lighting was flattened (the fine grain is untouched). If the texture is ever replaced, check it for the same thing
  (tile it 2x2, blur it and boost the contrast: the seams show), and retune `--paper`: the texture darkens the page by
  ~4.5%, so `--paper` is lightened to keep the page averaging out to `--bg` (#F2EEEA).

## Site structure

- Every folder other than `assets/` and `editor/` (`portfolio/`, `ai-*`, `nhb-games/`, `slow-food-*`, …) is a ~400-byte
  redirect stub to `https://hello.ct907.com/<name>/`. The real pages for those live on that other site, outside this
  repo. So today only `index.html` has typography to maintain here; apply the rule above to any real page added to this repo.
