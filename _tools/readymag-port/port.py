#!/usr/bin/env python3
"""Port Readymag page snapshots (hello.ct907.com) to static, responsive pages.

    python3 _tools/readymag-port/port.py                 # every page in PAGES
    python3 _tools/readymag-port/port.py nhb-games       # one page

Inputs live in _tools/readymag-port/source/ (snapshot HTML that Readymag renders
for each page, plus pages.json). Outputs:
    <slug>/index.html                 the page
    assets/images/<slug>/*            images, downloaded once from Readymag's CDN
    assets/css/rm-text.css            the project's text and link styles
    assets/css/rm-custom.css          the project's custom CSS
See assets/css/rm-page.css for how the markup is laid out.
"""
import hashlib, html, json, os, re, sys, urllib.request
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup, Tag

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "_tools", "readymag-port", "source")
CACHE = os.path.join(ROOT, "_tools", "readymag-port", "cache")
CANVAS = 1024
SITE = "https://ct907.com"
HELLO = "https://hello.ct907.com"
# Ported pages are published unlisted under this prefix (noindex, not in the sitemap) while
# hello.ct907.com stays the public version. Set PREVIEW = "" to publish them at their real paths.
PREVIEW = "/preview"

# Pages to build, with the titles and descriptions the new site uses.
PAGES = {
    "aria-driverless-car-app": "ARIA Rideshare App",
    "ai-driver-visual-language": "AI Driver Visual Language",
    "ai-driver-interaction-surface": "AI Driver Interaction Surfaces",
    "private-capital-management-website": "Investment Firm Website",
    "nhb-games": "NHB Gamification Webapp",
    "research-gateway-design": "Statboard Research Gateway",
    "ai-interaction-design": "AI Driver Interaction Design",
    "ai-visual-identity": "AI Visual Identity",
    "portfolio": "UX Portfolio",
}
ALL_SLUGS = ["welcome", "slow-food-album", "slow-food-recipe-1", "slow-food-recipe-2", "slow-food-recipe-3",
             "slow-food-recipe-4", "portfolio", "research-gateway-design", "aria-driverless-car-app", "nhb-games",
             "ai-interaction-design", "ai-driver-interaction-surface", "private-capital-management-website",
             "ai-driver-visual-language", "ai-visual-identity"]
# Portfolio buttons get their targets at runtime in Readymag, so map them by label.
BUTTON_TARGETS = {
    "NHB - Gamification Platform": "/nhb-games/",
    "Mapletree PCM - Website POC": "/private-capital-management-website/",
    "NLB - Research Gateway POC": "/research-gateway-design/",
    "ARIA Autonomous Car - Rideshare App": "/aria-driverless-car-app/",
    "AI Driver - Interaction Design": "/ai-interaction-design/",
    "AI Driver - Interaction Surfaces": "/ai-driver-interaction-surface/",
    "AI Driver - Visual Language": "/ai-driver-visual-language/",
    "AI Visual Identity": "/ai-visual-identity/",
}
FONT_FALLBACK = {
    "inter": "system-ui, -apple-system, 'Segoe UI', sans-serif",
    "josefin sans": "Futura, 'Century Gothic', sans-serif",
    "custom_109843": "'Josefin Sans', Futura, sans-serif",
    "karla": "system-ui, sans-serif",
    "young serif": "Georgia, serif",
    "custom_154805": "'Young Serif', Georgia, serif",
    "graphik": "Inter, system-ui, sans-serif",      # Graphik is not licensed for self-hosting; Inter stands in
    "georgia": "serif",
}

# ---------------------------------------------------------------- numbers ---
def fmt(n):
    s = f"{n:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s

def mobile_font(n):
    """Phone font size for a canvas font size: body text gets bigger, display text smaller."""
    if n <= 18:
        return max(15.0, n)
    return min(44.0, 15 + (n - 15) * 0.55)

PX = re.compile(r"(-?\d*\.?\d+)px")

def dual(n, m):
    if abs(n) < 1e-9 and abs(m) < 1e-9:
        return "0px"
    return f"calc({fmt(n)} * var(--u) * var(--d) + {fmt(m)}px * var(--m))"

def conv_value(prop, val, ratio, fs=None):
    def rep(mo):
        n = float(mo.group(1))
        if prop == "font-size":
            m = mobile_font(n)
        elif prop == "line-height":
            m = n * ratio
            if fs:
                m = max(min(m, mobile_font(fs) * 1.5), mobile_font(fs) * 1.15)
        elif prop in ("letter-spacing", "text-indent", "word-spacing"):
            m = n * ratio
        else:
            m = n
        return dual(n, m)
    return PX.sub(rep, val)

def parse_style(s):
    out = []
    for part in (s or "").split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            k, v = k.strip().lower(), v.strip()
            if k:
                out.append([k, v])
    return out

def style_get(decls, key):
    for k, v in decls:
        if k == key:
            return v
    return None

def px(v):
    if v is None:
        return None
    m = re.match(r"\s*(-?\d*\.?\d+)px", v)
    return float(m.group(1)) if m else None

def font_family(v):
    first = v.split(",")[0].strip().strip("'\"")
    fb = FONT_FALLBACK.get(first.lower())
    q = f"'{first}'" if " " in first else first
    return f"{q}, {fb}" if fb else v

def conv_decls(decls, ratio=1.0, drop=(), fs=None):
    out = []
    for k, v in decls:
        if k in drop:
            continue
        if k == "font-family":
            v = font_family(v)
        elif "px" in v:
            v = conv_value(k, v, ratio, fs)
        out.append(f"{k}: {v}")
    return "; ".join(out)

def ratio_for(fs):
    return (mobile_font(fs) / fs) if fs else 1.0

# ------------------------------------------------------------------ colour ---
def parse_color(v):
    if not v:
        return None
    v = v.strip()
    m = re.match(r"rgba?\(([^)]+)\)", v)
    if m:
        p = [float(x) for x in re.split(r"[,\s/]+", m.group(1).strip()) if x]
        return (p[0], p[1], p[2], p[3] if len(p) > 3 else 1.0)
    m = re.match(r"#([0-9a-f]{3,8})$", v, re.I)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)
    return None

def lum(c):
    def ch(x):
        x /= 255
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])

def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

def css_color(c):
    return f"rgb({int(c[0])}, {int(c[1])}, {int(c[2])})"

# ------------------------------------------------------------------ images ---
def best_src(img):
    cands = []
    for part in (img.get("srcset") or "").split(","):
        bits = part.strip().split()
        if bits:
            mult = float(bits[1].rstrip("x")) if len(bits) > 1 and bits[1].endswith("x") else 1
            cands.append((mult, bits[0]))
    if img.get("src"):
        cands.append((1, img["src"]))
    return max(cands)[1] if cands else None

def fetch_image(url, slug, local_dir=None):
    """Download one image (once) into assets/images/<slug>/ and return its site path."""
    os.makedirs(CACHE, exist_ok=True)
    if local_dir:          # saved-page images supplied by hand
        m = re.search(r"((?:image|RasterizedImage)-[0-9a-f-]{36})", unquote(url))
        key = m.group(1) if m else os.path.basename(url)
        for f in os.listdir(local_dir):
            if key[-36:][:8] in f or key in f:
                data = open(os.path.join(local_dir, f), "rb").read()
                ext = os.path.splitext(f)[1].lstrip(".")
                break
        else:
            raise SystemExit(f"no local file for {url}")
        name = f"{key.split('-')[0][:3]}-{key[-36:][:8]}.{ext}"
    else:
        u = url
        host = urlparse(u).netloc
        if host == "i-p.rmcdn.net" and "e=" not in u and not urlparse(u).path.endswith((".gif", ".svg")):
            u += ("&" if "?" in u else "?") + "e=webp"
        h = hashlib.sha1(u.encode()).hexdigest()[:10]
        cpath = os.path.join(CACHE, h)
        if not os.path.exists(cpath):
            req = urllib.request.Request(u, headers={"User-Agent": "ct907-readymag-port"})
            with urllib.request.urlopen(req, timeout=60) as r:
                open(cpath, "wb").write(r.read())
        data = open(cpath, "rb").read()
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            ext = "webp"
        elif data[:3] == b"GIF":
            ext = "gif"
        elif data[:8] == b"\x89PNG\r\n\x1a\n":
            ext = "png"
        elif data[:2] == b"\xff\xd8":
            ext = "jpg"
        elif b"<svg" in data[:400]:
            ext = "svg"
        else:
            ext = "bin"
        m = re.search(r"(image|Image|RasterizedImage)-([0-9a-f]{8})", u)
        name = f"{(m.group(1)[:3].lower() if m else 'img')}-{m.group(2) if m else 'x'}-{h[:6]}.{ext}"
    out_dir = os.path.join(ROOT, "assets", "images", slug)
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, name)
    if not os.path.exists(p):
        open(p, "wb").write(data)
    return f"/assets/images/{slug}/{name}"

# ------------------------------------------------------------------- links ---
def page_href(slug):
    """Where a link to another Readymag page should go: its port if built, else the original."""
    if slug in ("", "welcome"):
        return "/"
    if slug in PAGES:
        return f"{PREVIEW}/{slug}/"
    return f"{HELLO}/{slug}/"

def rewrite_href(href):
    if not href:
        return href
    m = re.match(r"^/\d+/([a-z0-9-]+)/?(#.*)?$", href)
    if m:
        return page_href(m.group(1))
    m = re.match(r"^https?://hello\.ct907\.com/([a-z0-9-]*)/?$", href)
    if m:
        return page_href(m.group(1))
    m = re.match(r"^/([a-z0-9-]+)/$", href)
    if m and m.group(1) in ALL_SLUGS:
        return page_href(m.group(1))
    m = re.match(r"^/p(\d+)/?$", href)
    if m:
        return href
    return href

# ----------------------------------------------------------------- widgets ---
class W:
    def __init__(self, **kw):
        self.__dict__.update(kw)

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2

# Runtime-only wrapper classes whose look is known from live screenshots.
WRAPPER_STYLE = {
    "css-1gu1mmv": [["background-color", "rgb(28, 28, 28)"]],   # "Browse Projects" label
    "css-161vgtv": [["background-color", "rgb(28, 28, 28)"]],
    "css-hslu6y": [["background-color", "rgb(28, 28, 28)"]],    # "Back To Home" label
    "css-3w0kxl": [["background-color", "rgb(28, 28, 28)"]],
}

KEEP_CLASS = re.compile(r"^(style-|paragraph-|link-style-|link-\d|align-|unordered-list-item|ordered-list-item|default-list-style|unstyled)")

def clean_text_tree(node, anchors, slug):
    """Rewrite a text widget's content in place: px -> scalable, classes trimmed, links fixed."""
    for el in node.find_all(True):
        if el.name in ("style", "script"):
            el.decompose()
            continue
        decls = parse_style(el.get("style"))
        if el.get("class"):
            keep = [c for c in el["class"] if KEEP_CLASS.match(c)]
            if "default-list-style" in el["class"]:
                keep.append("view-mode")
            if keep:
                el["class"] = keep
            else:
                del el["class"]
        if decls:
            fs = px(style_get(decls, "font-size"))
            if fs is None:
                sizes = [px(style_get(parse_style(d.get("style")), "font-size")) for d in el.find_all(style=True)]
                sizes = [s for s in sizes if s]
                fs = max(sizes) if sizes else None
            ratio = ratio_for(fs) if fs else ratio_for(px(style_get(decls, "line-height")) / 1.35 if px(style_get(decls, "line-height")) else 15)
            el["style"] = conv_decls(decls, ratio, fs=fs)
        for a in ("data-offset-key", "data-block", "data-editor", "data-text", "tabindex", "role"):
            if el.has_attr(a):
                del el[a]
        if el.name == "a":
            if el.has_attr("data-anchor-link-pos"):
                pos = int(float(el["data-anchor-link-pos"]))
                anchors.add(pos)
                el["href"] = f"#y-{pos}"
                del el["data-anchor-link-pos"]
            elif el.get("href"):
                el["href"] = rewrite_href(el["href"])
            if (el.get("href") or "").startswith("http"):
                el["target"] = "_blank"
                el["rel"] = "noopener"
            elif el.has_attr("target"):
                del el["target"]
            for a in ("data-page-uri",):
                if el.has_attr(a):
                    del el[a]

CLASS_FS = {}   # text-style class -> font size in canvas px, from the project's text styles

def max_font(node):
    best = 0
    for el in node.find_all(True):
        f = px(style_get(parse_style(el.get("style")), "font-size"))
        if not f:
            f = max([CLASS_FS.get(c, 0) for c in (el.get("class") or [])] or [0])
        if f and f > best:
            best = f
    return best

def text_color(node):
    for el in node.find_all(style=True):
        c = parse_color(style_get(parse_style(el["style"]), "color"))
        if c:
            return c
    return None

def anim_offset(container):
    """Click/hover motion of a Readymag animation container: (dx, dy) or None."""
    if container is None:
        return None
    st = container.find("style")
    path = re.search(r'offset-path:\s*path\("([^"]+)"\)', html.unescape(container.get("style", "")))
    if not st or not path:
        return None
    end = re.findall(r"100%\s*\{[^}]*offset-distance:\s*(-?[\d.]+)px", st.get_text())
    if not end or float(end[0]) == 0:
        return None
    nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", path.group(1))]
    if len(nums) < 4:
        return None
    return (nums[-2] - nums[0], nums[-1] - nums[1])

def extract(soup):
    pcc = soup.select_one(".page-content-container")
    widgets = []
    for child in pcc.find_all(True, recursive=False):
        if child.name == "style":
            continue
        cls = child.get("class") or []
        cont = child if "animation-container" in cls else None
        if cont is not None or child.name == "a":
            members = [w for w in child.find_all(class_="rmwidget") if w.find_parent(class_="rmwidget") is None]
        elif "rmwidget" in cls:
            members = [child]
        else:
            continue
        for widget in members:
            link = widget.parent if widget.parent is not None and widget.parent.name == "a" else None
            widgets.append(make_widget(widget, cont, link, len(widgets) + 1))
    return widgets

def make_widget(widget, cont, link, order):
    if True:
        wd = parse_style(widget.get("style"))
        x, y = px(style_get(wd, "left")) or 0.0, px(style_get(wd, "top")) or 0.0
        w, h = px(style_get(wd, "width")) or 0.0, px(style_get(wd, "height")) or 0.0
        z = style_get(wd, "z-index")
        opacity = None
        if cont is not None:
            cd = parse_style(cont.get("style"))
            x += px(style_get(cd, "left")) or 0.0
            y += px(style_get(cd, "top")) or 0.0
            z = z or style_get(cd, "z-index")
            opacity = style_get(cd, "opacity")
        kind = next((c[7:] for c in widget.get("class", []) if c.startswith("widget-")), "unknown")
        return W(kind=kind, x=x, y=y, w=w, h=h, z=int(float(z or 1)), node=widget, link=link, cont=cont,
                 data_id=widget.get("data-id"), opacity=opacity, wstyle=wd, order=order, motion=anim_offset(cont))

def render_widget(wd, slug, anchors, local_dir, drawer=False):
    """Return (html, meta) for one widget."""
    geo = f"--x: {fmt(wd.x)}; --y: {fmt(wd.y)}; --w: {fmt(wd.w)}; --h: {fmt(wd.h)}; --z: {wd.z}"
    extra = [d for d in wd.wstyle if d[0] not in ("left", "top", "width", "height", "z-index", "zoom", "cursor", "bottom", "margin-left")]
    if drawer and wd.motion:
        geo += f"; --dx: {fmt(wd.motion[0])}; --dy: {fmt(wd.motion[1])}"
    if wd.opacity not in (None, "1"):
        extra.append(["opacity", wd.opacity])
    did = f' data-id="{wd.data_id}"' if wd.data_id else ""
    meta = {}
    k = wd.kind
    if k == "text-v3":
        tv = wd.node.select_one(".text-viewer") or wd.node
        wrap = wd.node.find("div", recursive=False)
        label = ""
        for c in (wrap.get("class") or []) if wrap is not None else []:
            if c in WRAPPER_STYLE:
                extra = extra + WRAPPER_STYLE[c]
                label = " is-label"
        clean_text_tree(tv, anchors, slug)
        inner = "".join(str(c) for c in tv.contents)
        style = geo + (("; " + conv_decls(extra)) if extra else "")
        meta["font"] = max_font(tv)
        meta["color"] = text_color(tv)
        meta["text"] = tv.get_text(" ", strip=True)
        return f'<div class="w w-text{label}"{did} style="{style}">{inner}</div>', meta
    if k == "picture":
        img = wd.node.find("img")
        bg = wd.node.select_one(".bgpic")
        src = best_src(img) if img else None
        if not src and bg is not None and bg.get("url"):
            src = bg["url"]
        if not src:
            return "", {}
        path = fetch_image(html.unescape(src), slug, local_dir)
        istyle = []
        if bg is not None:
            bd = parse_style(bg.get("style"))
            for key in ("border-radius", "box-shadow", "opacity", "filter"):
                v = style_get(bd, key)
                if v and v not in ("none", "1"):
                    istyle.append([key, v])
            bp = style_get(bd, "background-position")
            if bp and bp != "50% 50%":
                istyle.append(["object-position", bp])
        if img is not None:
            for key, v in parse_style(img.get("style")):
                if key in ("border-radius", "opacity") and v not in ("1",):
                    istyle.append([key, v])
        alt = html.escape((img.get("alt") if img is not None else "") or "", quote=True)
        lazy = ' loading="lazy" decoding="async"' if wd.y > 700 else ' decoding="async"'
        ist = f' style="{conv_decls(istyle)}"' if istyle else ""
        small = " is-small" if wd.w < 160 else ""
        style = geo + (("; " + conv_decls(extra)) if extra else "")
        tag = "div"
        href = ""
        if wd.link is not None and wd.link.get("href"):
            tag, href = "a", f' href="{html.escape(rewrite_href(wd.link["href"]), quote=True)}"'
        meta.update(image=path, area=wd.w * wd.h)
        return (f'<{tag} class="w w-picture{small}"{did}{href} style="{style}">'
                f'<img src="{path}" alt="{alt}" width="{round(wd.w)}" height="{round(wd.h)}"{lazy}{ist}></{tag}>'), meta
    if k == "shape":
        style = geo + (("; " + conv_decls(extra)) if extra else "")
        svg = wd.node.find("svg")
        inner = ""
        if svg is not None:
            ow, oh = svg.get("width", "").replace("px", ""), svg.get("height", "").replace("px", "")
            if not svg.get("viewbox") and not svg.get("viewBox") and ow and oh:
                svg["viewBox"] = f"0 0 {ow} {oh}"
            svg["preserveAspectRatio"] = svg.get("preserveaspectratio", "none")
            for a in ("width", "height", "preserveaspectratio"):
                if svg.has_attr(a):
                    del svg[a]
            svg["aria-hidden"] = "true"
            if svg.has_attr("role"):
                del svg["role"]
            inner = str(svg)
        for im in wd.node.find_all("img"):
            path = fetch_image(html.unescape(best_src(im)), slug, local_dir)
            inner += f'<img src="{path}" alt="" style="width:100%;height:100%;object-fit:contain">'
        meta["bg"] = parse_color(style_get(wd.wstyle, "background-color"))
        return f'<div class="w w-shape"{did} style="{style}" aria-hidden="true">{inner}</div>', meta
    if k == "button":
        label = wd.node.select_one(".text")
        label = label.get_text(strip=True) if label else ""
        href = None
        if wd.link is not None:
            if wd.link.has_attr("data-anchor-link-pos"):
                pos = int(float(wd.link["data-anchor-link-pos"]))
                anchors.add(pos)
                href = f"#y-{pos}"
            elif wd.link.get("href"):
                href = rewrite_href(wd.link["href"])
        href = href or (rewrite_href(BUTTON_TARGETS[label]) if label in BUTTON_TARGETS else None)
        style = geo + (("; " + conv_decls(extra)) if extra else "")
        meta["text"] = label
        if href:
            ext = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
            return f'<a class="w w-button"{did} href="{html.escape(href, quote=True)}"{ext} style="{style}">{html.escape(label)}</a>', meta
        return f'<span class="w w-button"{did} style="{style}">{html.escape(label)}</span>', meta
    if k == "background":
        return "", {}
    # iframe embeds, video, lottie, hotspots: not capturable yet
    labels = {"iframe": "Embedded content: code still to be supplied", "video": "Video: file still to be supplied",
              "lottie": "Animation: Lottie file still to be supplied"}
    style = geo + (("; " + conv_decls(extra)) if extra else "")
    meta["placeholder"] = k
    return f'<div class="w w-placeholder" data-kind="{k}"{did} style="{style}" role="img" aria-label="{labels.get(k, k)}">{labels.get(k, k)}</div>', meta

# ----------------------------------------------------------- reading order ---
def xy_cut(ws):
    if len(ws) <= 1:
        return list(ws)
    for axis in ("y", "x"):
        key = (lambda w: w.y) if axis == "y" else (lambda w: w.x)
        end = (lambda w: w.y + w.h) if axis == "y" else (lambda w: w.x + w.w)
        s = sorted(ws, key=key)
        groups, cur, reach = [], [s[0]], end(s[0])
        for w in s[1:]:
            if key(w) >= reach - 2:
                groups.append(cur)
                cur, reach = [w], end(w)
            else:
                cur.append(w)
                reach = max(reach, end(w))
        groups.append(cur)
        if len(groups) > 1:
            out = []
            for g in groups:
                out.extend(xy_cut(g))
            return out
    return sorted(ws, key=lambda w: (round(w.y / 24), w.x))

# --------------------------------------------------------------- page build ---
def page_bg(soup):
    bg = soup.select_one(".page-fixed-bg-container .widget-background")
    c = parse_color(style_get(parse_style(bg.get("style")), "background-color")) if bg else None
    return c or (255, 255, 255, 1)

def describe(texts):
    for t in texts:
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) >= 90:
            if len(t) > 158:
                t = t[:155].rsplit(" ", 1)[0].rstrip(",;:") + "…"
            return t
    return ""

def build(slug, pages_meta, text_css_rules):
    title = PAGES[slug]
    local_dir = None
    if slug == "ai-visual-identity":
        raw = open(os.path.join(SRC, "ai-visual-identity.saved-article.html"), encoding="utf-8").read()
        local_dir = os.path.join(SRC, "ai-visual-identity-images")
        snap = open(os.path.join(SRC, "aria-driverless-car-app.html"), encoding="utf-8").read()  # for text styles
    else:
        raw = open(os.path.join(SRC, f"{slug}.html"), encoding="utf-8").read()
        snap = raw
    soup = BeautifulSoup(raw, "lxml")
    CLASS_FS.clear()
    page_rules = []
    if slug == "ai-visual-identity":
        collect_text_css(BeautifulSoup(open(os.path.join(SRC, "ai-visual-identity.text-styles.html"), encoding="utf-8").read(), "lxml"), page_rules)
    else:
        collect_text_css(soup, page_rules)
    pm = next(p for p in pages_meta if p["uri"] == slug)
    H = pm["height"]
    bgc = page_bg(soup) if soup.select_one(".page-fixed-bg-container .widget-background") else page_bg(BeautifulSoup(snap, "lxml"))
    if slug == "ai-visual-identity":
        bgc = page_bg(soup) if soup.select_one(".widget-background") else (0, 0, 0, 1)
    widgets = extract(soup)
    anchors = set()

    drawer, main, offcanvas = [], [], []
    for w in widgets:
        if w.x >= CANVAS - 2 or w.x + w.w <= 2 or w.y >= H or w.y + w.h <= 0:
            (drawer if (w.motion and w.x >= CANVAS - 40) else offcanvas).append(w)
        else:
            main.append(w)
    # the drawer's own background shape sits partly above the page (y < 0); keep it with the drawer
    rendered = {}
    for w in main + drawer:
        rendered[id(w)] = render_widget(w, slug, anchors, local_dir, drawer=w in drawer)

    # drawer trigger: the "Browse Projects" text
    toggle_ids = set()
    for w in main:
        m = rendered[id(w)][1]
        if w.kind == "text-v3" and re.fullmatch(r"browse projects", (m.get("text") or "").strip(), re.I):
            toggle_ids.add(id(w))

    def norm(t):
        return re.sub(r"[^a-z0-9]", "", (t or "").lower())
    texts_w = [w for w in main if w.kind == "text-v3"]
    deco = set()
    for w in texts_w:
        t = rendered[id(w)][1].get("text", "")
        if len(t) > 8 and not re.search(r"[A-Za-z0-9]", t):
            deco.add(id(w))
    for a_ in texts_w:
        for b_ in texts_w:
            if a_ is b_ or id(a_) in deco or id(b_) in deco:
                continue
            ta, tb = norm(rendered[id(a_)][1].get("text")), norm(rendered[id(b_)][1].get("text"))
            if not ta or not tb or not (ta.startswith(tb) or tb.startswith(ta)):
                continue
            ix = max(0, min(a_.x + a_.w, b_.x + b_.w) - max(a_.x, b_.x)); iy = max(0, min(a_.y + a_.h, b_.y + b_.h) - max(a_.y, b_.y))
            if ix * iy > 0.3 * min(a_.w * a_.h, b_.w * b_.h):
                deco.add(id(min(a_, b_, key=lambda w: (len(norm(rendered[id(w)][1].get("text"))), w.z))))
    for i in deco:
        h, m = rendered[i]
        rendered[i] = (h.replace('class="w w-text', 'class="w is-deco w-text', 1), m)

    # bands: big solid shapes behind content become section colours on mobile
    shapes = [w for w in main if w.kind == "shape"]
    band_shapes = [s for s in shapes if s.w >= 200 and s.h >= 90 and rendered[id(s)][1].get("bg") and rendered[id(s)][1]["bg"][3] >= 0.6]
    pictures = [w for w in main if w.kind == "picture" and w.w >= 280 and w.h >= 160]
    content = [w for w in main if w.kind != "shape"]
    ordered = xy_cut(content)

    def band_of(w):
        inside = [s for s in band_shapes if s.x - 1 <= w.cx <= s.x + s.w + 1 and s.y - 1 <= w.cy <= s.y + s.h + 1 and s.z < w.z]
        if inside:
            s = min(inside, key=lambda s: s.w * s.h)
            return rendered[id(s)][1]["bg"]
        return None

    # h1: the biggest text near the top of the page
    def wordy(w):
        t = rendered[id(w)][1].get("text", "")
        return sum(ch.isalpha() for ch in t) >= 4 and "is-label" not in rendered[id(w)][0][:80]
    tops = [w for w in main if w.kind == "text-v3" and w.y < 650 and id(w) not in toggle_ids and wordy(w)]
    h1w = max(tops, key=lambda w: (rendered[id(w)][1].get("font", 0), -w.y), default=None)

    bands, cur, cur_bg = [], [], "unset"
    for w in ordered:
        b = band_of(w)
        meta = rendered[id(w)][1]
        if w.kind == "text-v3" and meta.get("color"):
            base = b or bgc
            if contrast(meta["color"], base) < 2.2:     # text that sat on a picture: give it a backdrop
                b = (22, 22, 22, 1) if lum(meta["color"]) > 0.4 else (242, 242, 242, 1)
        key = css_color(b) if b else None
        if cur and key != cur_bg:
            bands.append((cur_bg, cur))
            cur = []
        cur_bg = key
        cur.append(w)
    if cur:
        bands.append((cur_bg, cur))

    # anchors: before the first widget at or below the target position
    anchor_before = {}
    for pos in sorted(anchors):
        tgt = next((w for w in ordered if w.y >= pos - 8), None)
        if tgt is not None:
            anchor_before.setdefault(id(tgt), []).append(pos)

    def emit(w):
        h, meta = rendered[id(w)]
        if not h:
            return ""
        if id(w) in toggle_ids:
            h = h.replace("<div ", '<div data-drawer-toggle role="button" tabindex="0" aria-controls="rm-drawer" aria-expanded="false" ', 1)
        if w is h1w:
            h = re.sub(r"<(p|h2|h3)(\s|>)", r"<h1\2", h, count=1)
            h = re.sub(r"</(p|h2|h3)>", "</h1>", h, count=1)
        pre = "".join(f'<span class="rm-anchor" id="y-{p}" style="--y: {p}"></span>' for p in anchor_before.get(id(w), []))
        return pre + h

    body = []
    for key, ws in bands:
        style = f' style="--band: {key}"' if key else ""
        body.append(f'<div class="rm-band"{style}>' + "".join(emit(w) for w in ws) + "</div>")
    shapes_html = "".join(rendered[id(s)][0] for s in shapes)

    drawer_html = ""
    if drawer:
        dshapes = [w for w in drawer if w.kind == "shape" and rendered[id(w)][1].get("bg")]
        dbg = rendered[id(max(dshapes, key=lambda s: s.w * s.h))][1]["bg"] if dshapes else (25, 0, 255, 1)
        items = [w for w in xy_cut([w for w in drawer if w.kind != "shape"])]
        drawer_html = (f'<nav class="rm-drawer" id="rm-drawer" aria-label="Projects" style="--drawer-bg: {css_color(dbg)}">'
                       '<button type="button" class="rm-drawer-close">Close</button>'
                       + "".join(rendered[id(w)][0] for w in drawer if w.kind == "shape")
                       + "".join(rendered[id(w)][0] for w in items) + "</nav>")

    # fixed widgets (e.g. "Back To Page Sections")
    fixed_html = ""
    for fx in soup.select(".fixed-position-container > a, .fixed-position-container-top > a"):
        lbl = fx.select_one(".text")
        if fx.has_attr("data-anchor-link-pos") and lbl:
            pos = int(float(fx["data-anchor-link-pos"]))
            anchors.add(pos)
            tgt = next((w for w in ordered if w.y >= pos - 8), None)
            if tgt is not None and pos not in anchor_before.get(id(tgt), []):
                anchor_before.setdefault(id(tgt), []).append(pos)
                body = None  # rebuild below with the new anchor
            fixed_html += f'<a class="rm-fixed" href="#y-{pos}" data-show-after="{pos + 400}">{html.escape(lbl.get_text(strip=True))}</a>'
    if body is None:
        body = []
        for key, ws in bands:
            style = f' style="--band: {key}"' if key else ""
            body.append(f'<div class="rm-band"{style}>' + "".join(emit(w) for w in ws) + "</div>")

    texts = [rendered[id(w)][1].get("text", "") for w in ordered if w.kind == "text-v3"]
    desc = describe(texts)
    imgs = [rendered[id(w)][1] for w in ordered if w.kind == "picture" and rendered[id(w)][1].get("image")]
    og = max(imgs, key=lambda m: m["area"])["image"] if imgs else None
    placeholders = [rendered[id(w)][1]["placeholder"] for w in main if rendered[id(w)][1].get("placeholder")]

    used = set(re.findall(r'class="([^"]+)"', "".join(body) + drawer_html))
    used = {c for group in used for c in group.split()}
    def needed(rule):
        names = set(re.findall(r"\.([A-Za-z0-9_-]+)", rule.split("{")[0])) - {"rm-canvas", "hover", "current", "view-mode", "edit-mode"}
        return not names or names & used
    page_css = "\n".join(r for r in page_rules if needed(r))
    head = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)} – Chris Tan</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
<link rel="canonical" href="{HELLO}/{slug}/">
{'<meta name="robots" content="noindex, nofollow">' if PREVIEW else ''}
<meta property="og:type" content="article">
<meta property="og:site_name" content="Chris Tan">
<meta property="og:title" content="{html.escape(title)} – Chris Tan">
<meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:url" content="{HELLO}/{slug}/">
{f'<meta property="og:image" content="{SITE}{og}">' if og else ''}
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="{css_color(bgc)}">
<link rel="preload" href="/assets/fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/rm-fonts.css">
<link rel="stylesheet" href="/assets/css/rm-page.css">
<style>
{page_css}
</style>
<link rel="stylesheet" href="/assets/css/rm-custom.css">
<script src="/assets/js/rm-page.js" defer></script>
<!-- Migrated from hello.ct907.com/{slug}/ (Readymag) by _tools/readymag-port/port.py. -->
</head>
"""
    page = (head + f'<body class="rm" style="--page-bg: {css_color(bgc)}">\n<a class="rm-skip" href="#main">Skip to content</a>\n'
            f'<main id="main" class="rm-page"><div class="rm-canvas" style="--H: {H}">\n'
            + drawer_html + "\n" + shapes_html + "\n" + "\n".join(body) + "\n</div></main>\n" + fixed_html + "\n</body>\n</html>\n")
    out_dir = os.path.join(ROOT, PREVIEW.strip("/"), slug)
    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(page)
    return {"slug": slug, "widgets": len(main), "drawer": len(drawer), "dropped_offcanvas": len(offcanvas),
            "bands": len(bands), "anchors": sorted(anchors), "images": len(imgs), "placeholders": placeholders,
            "desc": desc[:70], "toggle": bool(toggle_ids), "h1": rendered[id(h1w)][1].get("text", "")[:40] if h1w else None}

# ------------------------------------------------------------ shared CSS ---
def collect_text_css(soup, rules):
    st = soup.select_one("#text-global-styles style")
    if not st:
        return
    css = st.get_text()
    for m in re.finditer(r"([^{}]+)\{([^}]*)\}", css):
        sel, body = m.group(1).strip(), m.group(2)
        if "edit-mode" in sel or "editor-block" in sel:
            continue
        decls = parse_style(body)
        fs = px(style_get(decls, "font-size"))
        if fs and re.fullmatch(r"\.(style|paragraph)-[0-9a-f-]{36}|\.unstyled", sel):
            CLASS_FS[sel[1:]] = fs
        if style_get(decls, "text-align") == "align-left":
            decls = [d for d in decls if d[0] != "text-align"]
        sel = ", ".join(".rm-canvas " + s.strip() for s in sel.split(","))
        rule = f"{sel} {{ {conv_decls(decls, ratio_for(fs) if fs else 1.0, fs=fs)} }}"
        if rule not in rules:
            rules.append(rule)

def write_custom_css(pages_meta_project):
    ci = pages_meta_project.get("ci_css", "")
    # keep the well-formed rules; the two trailing dark-mode blocks in Readymag were never closed
    cut = ci.find('[data-id="687cee8daf9cfcc8c3d53f2a"] {\n@media')
    if cut > 0:
        ci = ci[:cut]
    ci = re.sub(r"@keyframes font-weight \{.*?\n\}\n", "", ci, flags=re.S)
    ci = ci.replace(" p span {", " :is(p, h1, h2) span {")   # the page title becomes an h1 in the port
    css = ("/* Custom CSS carried over from the Readymag project (keyed to widget ids). */\n"
           "@keyframes font-weight { 0% { font-variation-settings: \"wght\" 100; } 50% { font-variation-settings: \"wght\" 700; } 100% { font-variation-settings: \"wght\" 100; } }\n"
           + ci.strip() + "\n@media (prefers-reduced-motion: reduce) { [data-id] p span { animation: none !important; } }\n")
    open(os.path.join(ROOT, "assets", "css", "rm-custom.css"), "w").write(css)

def main():
    meta = json.load(open(os.path.join(SRC, "pages.json")))
    slugs = sys.argv[1:] or list(PAGES)
    rules = None
    os.makedirs(os.path.join(ROOT, "assets", "css"), exist_ok=True)
    report = []
    for s in slugs:
        report.append(build(s, meta["pages"], rules))
    write_custom_css(meta["project"])
    for r in report:
        print(json.dumps(r))

if __name__ == "__main__":
    main()
