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
| Drag the orange **⇅ push this & below** grip (or use **Move this & everything below** in the panel) | Move the element and everything under it together |
| **Page & background** in the panel (press Esc to deselect) | Grid, cyan, magenta and paper-grain opacity; the riso shift on headings; page length |
| **Replace image…** in the panel, or drop an image file onto a picture | Swap a picture for your own file |
| **Add layers** in the panel | Add new text, a heading or an image *inside a box*, or floating *decoration* |
| The purple ✦ handle on a decorative layer, or the **Layers** list | Select a layer that sits behind the page content |
| Delete (or the red button) on a layer | Delete a layer you added with the editor (including ones pushed earlier) |
| **390 / 820 / 1280 / 1440 / 1920** or the Width box | Preview at that screen width |
| **Review & push** | See exactly what will be written (and uploaded), then open the pull request |

| **B** / **I** buttons in the **Type** section | Bold / italic: the selected words while you are editing text, otherwise the whole element |
| **Border** in the panel | Border thickness, colour, style, each side, corner radius |
| **All CSS** in the panel | Any CSS property the controls don't cover |

The panel has number fields for position, size, padding, margin and spacing; the **Type**, **Border**, **Shadow, filters & transform**
and **Layout** sections below; colour pickers for text and fill; opacity and the frosted-glass blur; an **All CSS** section; and a
**Design tokens** section for the site-wide values (`--ink-c`, `--ink-m`, `--grain`, `--paper`, …). Drag a field's label
sideways to scrub the number.

### Text styles

The **Type** section has:

- **Font**: the site's two roles (*Heading font* = `var(--display)`, *Body font* = `var(--text)`), the fonts the page already loads,
  and **Google Fonts only**: 54 popular families (sans-serif, serif, monospace, script & display), plus **Other Google font…** for
  any family you type (e.g. *Bricolage Grotesque*). The editor asks Google for the most capable version first (variable weights and
  italics) and falls back to simpler requests until Google accepts one, so a font always loads with the weights it really has.
- **Weight**: only the weights that are actually loaded for the chosen font (Signika 300–700, Lora 400–700, Playfair Display 400–900 …).
- **B**, **I**, **U**, **S** buttons: bold, italic, underline, strikethrough. **While you are editing text, B and I format the selected words**
  (saved as clean `<strong>` / `<em>`); otherwise B and I make the whole element bold or italic. U and S always apply to the whole element.
  There are no keyboard shortcuts for these; use the buttons.
- **Alignment** (left, centre, right, justify), **Case** (as typed, UPPERCASE, lowercase, Capitalize), **font size**, **line height**,
  **letter spacing**, **word spacing**, and a **text shadow** (X, Y, blur, colour).

**How a font reaches the live page.** Picking a font loads it in the preview immediately. When you push, the editor adds **one**
managed `<link>` to the page's `<head>`, between marker comments, asking Google for exactly the families you used:

```html
<!-- ===== editor fonts: start (managed by /editor/; safe to hand-edit) ===== -->
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
<!-- ===== editor fonts: end ===== -->
```

Fonts the page already loads (Signika and Lora) are never requested twice. A font that no CSS refers to any more is taken out of the
link again, and the block disappears when it would be empty, so undoing every font choice gives back the original file byte for byte.
Each font you add costs visitors a download, so use a few. (Keep the Slow Food Album pages' own fonts as they are; see `CLAUDE.md`.)

### Border, shadow, filters, transform, layout

- **Border**: thickness for all four sides (or each side on its own), style (solid, dashed, dotted, double …), colour with opacity, and the
  radius of each corner. Setting a colour or a thickness on an element with no border gives it a visible 1px solid one.
- **Shadow, filters & transform**: a box shadow (X, Y, blur, spread, colour, inner), filters (blur, brightness, contrast, saturation,
  grayscale, hue), blend mode, rotation and scale. A filter the page already uses (such as a drop-shadow on a picture) is kept when you add another.
  Rotated or scaled elements hide their resize handles (they would point the wrong way); use the W / H fields.
- **Layout**: display (including *none* to hide it), position, z-index, overflow, and for flex/grid boxes direction, wrap, justify and align.
- **All CSS**: type any property and value (the box suggests property names), for anything not covered above. The browser checks the
  value before it is recorded, and a value can't contain `{ } ;` (outside quotes), `<`, or comment marks, so it can't break the stylesheet.
  Under it, every declaration recorded for the selected element at this width is listed and can be edited as text or removed.

While you work, the preview has CSS transitions switched off so that what you read back from a field is exactly what you set.

### Move this and everything below it

Select an element and an orange dashed line appears across the page at its top edge. The **Move this & everything
below** section (or the orange grip on the line) pushes the element **and every block that starts at or under that
line** down or up together, like inserting or removing space there. Hover the section or the grip to see exactly what
will move (each affected block is outlined, and the panel says how many).

- Type a number, use the **↑ 100 / ↑ 10 / ↓ 10 / ↓ 100** buttons, or drag the grip. The number is the total push for
  this selection; **×** or `0` puts everything back exactly as it was.
- **The page length follows.** Pushing down by 120px makes the page 120px longer (the grid and grain extend with it),
  pushing up makes it shorter. This is a `body { height }` rule; the "Page length" readout shows the effect. Untick
  *Make the page longer or shorter to fit* to move content without changing the length, or set the length directly under
  **Page & background → Len**.
- You can't pull content above the top of the page; the push stops there and says so.
- Each moved block gets a `translate` rule (so there are as many lines in the pull request as blocks that moved), and,
  like every tweak, they are saved for the width range you are previewing.
- "Below" is by position: a block that starts above the line but reaches past it stays put, while its lower children
  move. Things beside the selection that start at the same height come along.

### Page & background

With nothing selected (or in the **Page & background** section when something is), sliders set the opacity of the
printed grid: **Grid** (both ink plates together, where 100% is the reference print and 50% is how the page ships),
**Cyan** and **Magenta** on their own, and the **Grain** of the paper. Sliding back to the shipped value records nothing.

Under them, **Header riso shift** controls the off-register printing on heading text (h1–h3 and the big sub-headline): a
yellow and a magenta copy of the text, printed in opposite directions (yellow up-left, magenta down-right). **Yellow**
goes from 0 to 2px, **Magenta** from 0 to 4px, and **Opacity** applies to both (the page ships at 2px, 4px and 20%; 0%
switches the effect off). They write the tokens `--riso-yellow-shift`, `--riso-magenta-shift` and `--riso-text`, and the
two colours (`--riso-yellow`, `--riso-magenta`) are in **Design tokens**. To change the effect on one heading only, select
it and use its **Text shadow** controls; those read the page's two plates (the panel says "2 shadows here") and replace
them with one when you edit.

These are site-wide and are written inside `@media (prefers-contrast: no-preference)`, so visitors who ask for increased
contrast still get the page's own calm, grain-free fallback (an `!important` rule outside that condition would override it).
The same applies to any design token the page overrides for increased contrast.

### Adding text and images (layers)

The **Add layers** section has two kinds of layer. Each layer gets its own unique class (`ed-text-k3f9`, `ed-deco-t8x2` …)
which is how the editor recognises it, styles it and, later, deletes it.

**Inside a box.** Select a div, section or any other box (or anything inside one: a paragraph offers the section around it;
the panel names the box it will use, and the breadcrumbs pick another). Then **＋ Text**, **＋ Heading** or **＋ Image…**.
*Where* chooses *after the selected item*, *at the start* or *at the end* of the box. A new text layer opens for typing straight away
(Enter saves; creating and naming it is a single undo step). New text and headings get the page's frosted plate (untick it in
the Layer section). A new image is 12rem wide, optimised like a replaced picture, and has an **Alt text** box: describe it,
or leave it empty only if it is purely decorative. The layer is ordinary page content: it moves, resizes and restyles like
anything else, and later you can add more *after* it.

**Decoration.** **＋ Decorative text** and **＋ Decorative image…** make free-floating layers: absolutely positioned in the page,
**behind the page content by default** (pick *in front* in the Layer section), marked `aria-hidden="true"` (and `alt=""` for
images), `pointer-events: none` so they never block a click on the live page, and not selectable by text-selection. They start
at about 35% across and a third of the way down your current view; drag them into place (the page's own boxes cover a layer that
is behind the content, so each one has a small purple **✦ handle** in the editor, and there is the **Layers** list), set the
rotation, opacity and size in the panel. Like every tweak, moves are saved for the width range you are previewing: a
decoration positioned at Desktop is still present at Phone, so check it there and move it, resize it or set its opacity to 0.

**What gets written.** In-flow layers are inserted into the page's HTML right where you put them, indented like their
neighbours. Decorative layers go into one managed block just before `</body>`:

```html
<!-- ===== editor decor: start (managed by /editor/; safe to hand-edit) ===== -->
<span class="ed-deco ed-deco-t8x2" aria-hidden="true">✦ hello ✦</span>
<img class="ed-deco ed-deco-m1q7" src="assets/images/sticker-89cdd76d.webp" alt="" aria-hidden="true" width="500" height="500">
<!-- ===== editor decor: end ===== -->
```

Their styling is in the managed CSS block (a shared `.ed-deco` rule, plus one rule per layer, plus per-width moves). Image layers
upload their file to `assets/images/` in the same commit.

**Safety.** The editor finds the right place with its own small HTML indexer, and does not trust it blindly: first it checks
that it sees exactly the same elements, nested the same way, as the browser does for the *whole* page; then, after inserting, it
has the browser re-read the result and requires exactly one more element, with the new one in the expected box and beside the
expected neighbours. If anything is off (the page changed since you opened the editor, or the markup has unclosed `<p>`/`<li>`
tags) the layer is **not** added, its picture is not uploaded, and it is listed in the pull request instead.

**Deleting.** You can delete any layer the editor made, including ones pushed in earlier pull requests: the layer, its CSS rules
(and the shared `.ed-deco` rule and the decor block when they are no longer needed) are removed from the file. Adding layers and
deleting them again gives back the original file byte for byte. The editor will not delete anything it didn't create. A deleted
layer's picture file stays in `assets/images/`.

### Replacing pictures

Select a picture (or drop an image file onto it) and choose **Replace image…**. The preview shows it immediately, in the
same frame. By default the file is **optimised for the web**: resized so its longest side is about three times the size
it's shown at (you can set that) and re-encoded as WebP, never making a file bigger than the one you picked. Untick it
to upload your file byte for byte. PNG, JPEG, WebP, AVIF, GIF and SVG are accepted (GIF and SVG are never re-encoded).

**Fit** (cover / contain / fill…) and the **X / Y focal point** set how the picture fills its frame, which is how you
re-crop it. **Revert** goes back to the original.

When you push, the new file is committed to **`assets/images/<name>-<hash>.<ext>`** in the same commit as everything else,
and that picture's `src="…"` in the page is changed to point at it. The hash is the file's content, so replacing a
picture twice never overwrites an old file and the same file used twice is uploaded once.

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

When you push, the editor reads `index.html` from `main`, changes **only** these things, and makes **one commit** on a
new branch `editor/tweaks-<date>-<time>` with a pull request (the commit is built first and the branch only created at the
end, so a failure part-way leaves no stray branch):

1. **One managed block at the very end of the page's `<style>`**, between two marker comments:

   ```css
   /* ===== editor tweaks: start (managed by /editor/; safe to hand-edit) ===== */
   :root { --grain: 0.5 !important; }
   @media (prefers-contrast: no-preference) {
     :root { --ink-c: #59e1ff !important; --ink-m: #e1c1dd !important; }
   }
   @media (min-width: 1100px) {
     div.copy.glass { padding-top: 1.875rem !important; color: #b3004a !important; }
     #music-h { translate: 0rem 7.5rem !important; }
     body { height: 166.25rem !important; }
   }
   /* ===== editor tweaks: end ===== */
   ```

   Rules use `!important` so they always win over the existing CSS. The block is merged with whatever is already
   on `main` (so two people's tweaks don't overwrite each other), and removing a tweak in the editor removes its line.
   You can hand-edit the block; the editor reads it back as written.
2. **Text edits**, replaced in place in the HTML. If the original text can't be found exactly once (for example the
   page changed since you opened the editor) the edit is *not* applied; it is listed in the pull request for you to do by hand.
3. **Replaced pictures**: the new file is added under `assets/images/`, and the picture's `src="…"` attribute is swapped
   for its path. The old address must appear exactly once as a `src`; otherwise the picture is *not* uploaded and is listed
   in the pull request instead. Other mentions of the old address (the portrait's `og:image` and JSON-LD) are left alone,
   so social-share previews keep the old picture until you change those by hand.

4. **New layers**: in-flow layers are written into the HTML at the spot you chose; decorative layers into the managed decor
   block (see *Adding text and images*). Their CSS joins the managed block above.
5. **Google Fonts**: one managed `<link>` in `<head>` (see *Text styles*).

Nothing else in the file is touched.

### Folding tweaks back into the real CSS

The block is an override layer, so it grows over time. Whenever it's convenient, ask Claude (or do it by hand) to
move the rules into the main stylesheet and delete the block. Until then it is harmless.

## Good to know

- The preview shows the page **as deployed from `main`**. Changes in an unmerged pull request won't appear.
- Your recorded tweaks are kept in this browser as a draft, so an accidental reload offers to restore them. Replaced
  pictures and new layers are **not** kept in the draft (their image files are too big for it): after an accidental reload,
  add them again. (The **Reload** button inside the editor keeps everything.) Closing the tab with unsent changes asks you to confirm.
- The push uses GitHub's Git Data API (blobs, tree, commit, ref), which the same *Contents: Read and write* permission covers.
- Pictures are not cropped for you: the page's own CSS fits them to their frames (`object-fit: cover`), and the focal point
  moves that crop. The tile-sized pictures use a ~170px frame, so very wide images will lose their sides.
- Resizing past a `max-width` / `max-height` in the page's own CSS also lifts that cap (as a visible extra tweak),
  otherwise the handle would appear to do nothing.
- Inline elements (like bold text inside a paragraph) can't be moved by CSS, so they are switched to `inline-block` automatically.
- Rotated elements (the portrait, the tilted photo) can be moved but not resized with the handles: the handles would
  point the wrong way. Use the W / H fields instead.
- Works in current Chrome, Edge, Safari and Firefox on a laptop or desktop. It was tested in Chromium.
