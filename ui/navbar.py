"""Navbar bergaya mockup: bar kuning selebar layar, logo di kiri, menu berbentuk pil."""
import streamlit as st

_CSS = """
<style>
/* bar penuh selebar layar, isinya tetap sejajar dengan konten (maks 1400px) */
.st-key-navbar {
    width: 100vw; margin-left: calc(50% - 50vw); box-sizing: border-box;
    background: linear-gradient(90deg, #FFD21F, #FFB800);
    padding: 14px max(32px, calc((100vw - 1400px) / 2 + 32px));
    margin-bottom: 1.75rem;
}
.st-key-navbar [data-testid="stHorizontalBlock"] { gap: 6px !important; flex-wrap: nowrap; align-items: center; }
.st-key-navbar [data-testid="stColumn"] { flex: 0 0 auto !important; width: auto !important; min-width: 0 !important; }
.st-key-navbar [data-testid="stColumn"]:first-child { margin-right: 28px; }

.st-key-navbar [data-testid="stPageLink-NavLink"] {
    border-radius: 999px; padding: .6rem 1.3rem; justify-content: center; white-space: nowrap;
}
.st-key-navbar [data-testid="stPageLink-NavLink"] p,
.st-key-navbar [data-testid="stPageLink-NavLink"] span { color: #1A1400 !important; font-size: 1.05rem; font-weight: 500; margin: 0; }
.st-key-navbar [data-testid="stPageLink-NavLink"]:hover { background: rgba(26,20,0,.12); }

.st-key-nav-active [data-testid="stPageLink-NavLink"],
.st-key-nav-active [data-testid="stPageLink-NavLink"]:hover { background: #1A1400; }
.st-key-nav-active [data-testid="stPageLink-NavLink"] p,
.st-key-nav-active [data-testid="stPageLink-NavLink"] span { color: #FFD21F !important; font-weight: 600; }
</style>
"""

_LOGO = (
    '<div style="display:flex;align-items:center;gap:12px;color:#1A1400;white-space:nowrap">'
    '<svg width="42" height="42" viewBox="0 0 40 40" aria-hidden="true">'
    '<circle cx="20" cy="20" r="18" fill="none" stroke="#1A1400" stroke-width="2"/>'
    '<polygon points="20,10 28,16 25,26 15,26 12,16" fill="#1A1400"/></svg>'
    '<div style="line-height:1.05">'
    '<div style="font-weight:700;font-size:1.4rem;letter-spacing:.02em">SiKupingBesar</div>'
    '<div style="font-size:.7rem;letter-spacing:.14em">UCL LEAGUE SIMULATOR</div>'
    '</div></div>'
)

def render(pages, current):
    """pages: daftar st.Page; current: halaman aktif (hasil st.navigation)."""
    st.markdown(_CSS, unsafe_allow_html=True)
    with st.container(key="navbar"):
        cols = st.columns(len(pages) + 1, vertical_alignment="center")
        cols[0].markdown(_LOGO, unsafe_allow_html=True)
        for col, p in zip(cols[1:], pages):
            key = "nav-active" if p.title == current.title else f"nav-item-{p.url_path or 'home'}"
            with col, st.container(key=key):
                st.page_link(p, label=p.title)
