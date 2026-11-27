# Page editor

A visual editor for the homepage. Open it, push things around on the page, and it turns what you did
into code and opens a pull request. There is nothing to install: it is a single static page.

**Open it at `https://ct907.com/editor/`** (once this folder is on `main` and GitHub Pages has deployed it).
It is not linked from the site and is marked `noindex`.

## One-time setup (about two minutes)

1. Create a **fine-grained personal access token**: <https://github.com/settings/personal-access-tokens/new>
   - **Repository access:** *Only select repositories* → `ct907/ct907-site`
   - **Permissions:** *Contents: Read and write* and *Pull requests: Read and write*
   - Give it a short expiry (30 days is plenty).
2. In the editor click **Settings**, paste the token, and tick **Remember on this device** if you want it kept
   (leave it unticked and you'll paste it each time).

The token is only ever sent to `api.github.com`. The page's Content-Security-Policy forbids any other destination,
and it is never written into the page.

## Using it

| Do this | To |
|---|---|
| Click an element | Select it (the label shows its name; the right-hand panel shows its settings) |
| Drag the element | Move it |
| Drag a handle | Resize it |
| Arrow keys (Shift = 10px) | Nudge the selection |
| Double-click text (or press Enter) | Retype it. Enter saves, Esc cancels |
| Ctrl/Cmd + click | Pick the innermost element instead of the one that's already selected |
| Alt + ↑ ↓ ← → | Select parent / first child / previous / next sibling (or use the breadcrumb buttons) |
| Ctrl/Cmd + Z, Ctrl/Cmd + Shift + Z | Undo, redo |
| **390 / 820 / 1280 / 1440 / 1920** or the Width box | Preview at that screen width |
| **Review & push** | See exactly what will be written, then open the pull request |

The panel has number fields for position, size, padding, margin, font size, line height, letter spacing, corner
radius, opacity and the frosted-glass blur; colour pickers for text and fill; and a **Design tokens** section for the
site-wide values (`--ink-c`, `--ink-m`, `--grain`, `--paper`, …). Drag a field's label sideways to scrub the number.

The page is shown as a calm, static canvas: the cursor effects, scroll animations and hover-only text are switched
off or made visible so you can select everything.

### Tweaks are saved per screen width

The preview width decides which screen-width range a tweak belongs to, and the toolbar always shows it:

| Range | Applies at |
|---|---|
| Phone | `max-width: 720px` (the same break the site's own layout uses) |
| Tablet | `721px` to `1099px` |
| Desktop | `1100px` and up |

So a nudge made at 1440 is a desktop-only rule and can't break the phone layout. Design tokens are the exception:
they are site-wide and apply at every width.

Positions and sizes are saved in **`rem`** (so they scale with the text, like the rest of the page), not pixels.

## What gets written

When you push, the editor reads `index.html` from `main`, changes **only** these things, and commits to a new branch
`editor/tweaks-<date>-<time>` with a pull request:

1. **One managed block at the very end of the page's `<style>`**, between two marker comments:

   ```css
   /* ===== editor tweaks: start (managed by /editor/; safe to hand-edit) ===== */
   :root { --grain: 0.5 !important; }
   @media (min-width: 1100px) {
     div.copy.glass { padding-top: 1.875rem !important; color: #b3004a !important; }
   }
   /* ===== editor tweaks: end ===== */
   ```

   Rules use `!important` so they always win over the existing CSS. The block is merged with whatever is already
   on `main` (so two people's tweaks don't overwrite each other), and removing a tweak in the editor removes its line.
   You can hand-edit the block; the editor reads it back as written.
2. **Text edits**, replaced in place in the HTML. If the original text can't be found exactly once (for example the
   page changed since you opened the editor) the edit is *not* applied; it is listed in the pull request for you to do by hand.

Nothing else in the file is touched.

### Folding tweaks back into the real CSS

The block is an override layer, so it grows over time. Whenever it's convenient, ask Claude (or do it by hand) to
move the rules into the main stylesheet and delete the block. Until then it is harmless.

## Good to know

- The preview shows the page **as deployed from `main`**. Changes in an unmerged pull request won't appear.
- Your recorded tweaks are kept in this browser as a draft, so an accidental reload offers to restore them.
- Resizing past a `max-width` / `max-height` in the page's own CSS also lifts that cap (as a visible extra tweak),
  otherwise the handle would appear to do nothing.
- Inline elements (like bold text inside a paragraph) can't be moved by CSS, so they are switched to `inline-block` automatically.
- Rotated elements (the portrait, the tilted photo) can be moved but not resized with the handles: the handles would
  point the wrong way. Use the W / H fields instead.
- Works in current Chrome, Edge, Safari and Firefox on a laptop or desktop. It was tested in Chromium.
