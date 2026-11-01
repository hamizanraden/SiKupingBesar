"""Render komponen HTML + Tailwind (CDN) lewat Jinja2. Logo klub: taruh PNG di assets/logos/<slug>.png."""
import base64, re, zlib
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

_ROOT = Path(__file__).resolve().parent.parent
_ENV = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"),
                   autoescape=select_autoescape(["html"]))
_COLORS = ["#1E3F8A", "#C8102E", "#0A5CA8", "#7A5C12", "#17802F", "#6B2FA0", "#B3122B", "#1B2A5E"]
_HEAD = ('<script src="https://cdn.tailwindcss.com"></script>'
         '<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">'
         '<style>body{margin:0;font-family:Outfit,sans-serif;background:transparent}</style>')

def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def badge(name):
    """Info lencana tim: logo (jika ada filenya) atau lingkaran inisial."""
    p = _ROOT / "assets" / "logos" / f"{slug(name)}.png"
    logo = None
    if p.exists():
        logo = "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()
    parts = name.replace("-", " ").split()
    ini = (parts[0][0] + (parts[1][0] if len(parts) > 1 else parts[0][1:2])).upper() if parts else "?"
    if name.lower().startswith("klub ") and len(parts) > 1:
        ini = parts[1][-2:]
    return dict(initials=ini, color=_COLORS[zlib.crc32(name.encode()) % len(_COLORS)], logo=logo)

_ENV.globals["badge"] = lambda n: badge(n)

def html(template, **ctx):
    """Murni HTML (bisa diuji tanpa Streamlit)."""
    return _HEAD + _ENV.get_template(template).render(**ctx)

def render(template, height=300, **ctx):
    import streamlit.components.v1 as components
    components.html(html(template, **ctx), height=height, scrolling=False)
