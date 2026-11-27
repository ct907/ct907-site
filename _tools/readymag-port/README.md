# Readymag port

Rebuilds the pages of the Readymag project behind hello.ct907.com as static pages on this site.
Jekyll ignores folders that start with `_`, so nothing in here is published.

```bash
pip install beautifulsoup4 lxml
python3 _tools/readymag-port/port.py                 # every page listed in PAGES
python3 _tools/readymag-port/port.py nhb-games       # one page
```

## Inputs (`source/`)

- `<slug>.html`: the pre-rendered snapshot Readymag keeps for each page (`htmlUrl` in the page
  data). It holds every widget with its position on Readymag's 1024px canvas, all text as real
  text, image URLs with crop parameters, and the project's text styles. Captured 27 Nov 2026.
- `ai-visual-identity.saved-article.html`, `ai-visual-identity.text-styles.html` and
  `ai-visual-identity-images/`: Readymag's snapshot of this page is blank, so it is built from a copy of
  the page saved from a browser instead.
- `pages.json`: page list, heights, titles and SEO fields, plus the project's custom CSS.

## Outputs

- `<slug>/index.html` (replaces the redirect stub), `assets/images/<slug>/`, `assets/css/rm-custom.css`.
- Shared, hand-written: `assets/css/rm-page.css`, `assets/css/rm-fonts.css`, `assets/js/rm-page.js`.

## How the pages work

Desktop (900px and up) keeps Readymag's absolute layout and scales it to the window with container
units, the way the Readymag viewer does. Below 900px the same markup reflows into one column: the
generator puts widgets in reading order (an XY-cut over their boxes) and wraps runs of them in
`.rm-band` elements that carry the colour of the section they sat on. See the header of
`assets/css/rm-page.css`.

Things the generator recreates because the snapshot does not include them: the "Browse Projects"
drawer (the off-canvas widgets with a click motion), the in-page jump links and the floating
"Back To Page Sections" button, and the dark label boxes behind "Browse Projects"/"Back To Home"
(`WRAPPER_STYLE`, measured from a live screenshot). Portfolio buttons get their targets from
`BUTTON_TARGETS`.

## Known gaps

- Embeds, videos and Lottie files are not in the snapshots and render as labelled placeholders
  (only the 360° view on `/ai-interaction-design/` among the pages built so far).
- Graphik is a commercial font served by Readymag; Inter stands in until it is licensed or replaced.
- Load and scroll animations are not recreated; hover colours on text links are.
- Images have Readymag's alt text where it existed (almost none); the rest is empty for now.

Downloaded images are cached in `cache/` (git-ignored) so reruns do not hit the CDN.
