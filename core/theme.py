import base64 as _b64
import os as _os

def _load_logo_b64() -> str:
    """Carrega exa_logo_white.png (fundo transparente, traços brancos) e retorna data URL base64."""
    logo_path = _os.path.join(_os.path.dirname(__file__), "..", "static", "exa_logo_white.png")
    logo_path = _os.path.normpath(logo_path)
    with open(logo_path, "rb") as f:
        return "data:image/png;base64," + _b64.b64encode(f.read()).decode()

# ── Icon Library (Lucide-style, stroke="currentColor") ─────────────────────
ICONS: dict[str, str] = {
    "users": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "user": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "user-check": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/></svg>',
    "dollar": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
    "shield": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>',
    "zap": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "percent": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>',
    "trending-down": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>',
    "trending-up": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "bar-chart": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>',
    "activity": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "repeat": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>',
    "hash": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/></svg>',
    "divide": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="6" r="2"/><line x1="5" y1="12" x2="19" y2="12"/><circle cx="12" cy="18" r="2"/></svg>',
    "refresh": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.38"/></svg>',
    "plug": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6L6 18"/><path d="m6 6 12 12"/><path d="m9 6-3 3 3 3"/><path d="m15 18 3-3-3-3"/></svg>',
    "trash": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>',
}


def kpi_card(
    label: str,
    value: str,
    sub: str = "",
    icon: str = "",
    variant: str = "default",
    sub_type: str = "neutral",
    sparkline: list | None = None,
) -> str:
    """
    Generates HTML for a KPI card.
    variant:   "default" | "feature" | "churn"
    sub_type:  "up" | "down" | "churn" | "neutral"
    sparkline: optional list of 4-5 heights 0-1 for decorative mini bars
    """
    card_cls = {
        "default": "kpi-card",
        "feature": "kpi-card-feature",
        "churn":   "kpi-card-churn",
    }.get(variant, "kpi-card")
    label_cls = "kpi-label-light" if variant == "feature" else "kpi-label"
    value_cls = "kpi-value-light" if variant == "feature" else "kpi-value"
    sub_cls = {
        "up":    "kpi-up",
        "down":  "kpi-down",
        "churn": "kpi-churn",
    }.get(sub_type, "kpi-sub")

    icon_html  = f'<div class="kpi-icon">{ICONS[icon]}</div>' if icon in ICONS else ""
    sub_html   = f'<div class="{sub_cls}">{sub}</div>' if sub else ""
    spark_html = ""
    if sparkline:
        bars = "".join(
            f'<span class="kpi-bar" style="height:{int(h*48)}px"></span>'
            for h in sparkline
        )
        spark_html = f'<div class="kpi-spark">{bars}</div>'
    return (
        f'<div class="{card_cls}">'
        f"{spark_html}"
        f"{icon_html}"
        f'<div class="kpi-text">'
        f'<div class="{label_cls}">{label}</div>'
        f'<div class="{value_cls}">{value}</div>'
        f"{sub_html}"
        f"</div>"
        f"</div>"
    )


# ── Global CSS ──────────────────────────────────────────────────────────────
KALLAS_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
  :root {
    --bg:          #EEF2FF;
    --surface:     #ffffff;
    --surface-2:   #F0F4FF;
    --ink:         #0F172A;
    --ink-2:       #334155;
    --ink-3:       #64748B;
    --line:        #DBEAFE;
    --line-2:      #BFDBFE;
    --green:       #2563EB;
    --green-deep:  #1D3186;
    --green-ink:   #0F172A;
    --green-soft:  #DBEAFE;
    --green-mid:   #60A5FA;
    --amber:       #F59E0B;
    --rose:        #EF4444;
    --radius:      22px;
    --radius-sm:   14px;
    --shadow-sm:   0 4px 14px rgba(11,46,107,.07);
    --shadow-md:   0 10px 28px rgba(11,46,107,.09);
    --shadow-lg:   0 20px 48px rgba(11,46,107,.14);
  }

  html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--ink) !important;
    -webkit-font-smoothing: antialiased;
  }

  /* Remove Streamlit defaults */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container {
    padding: 1.8rem 2rem 2rem !important;
    max-width: 1400px !important;
  }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--line-2); border-radius: 99px; }
  ::-webkit-scrollbar-thumb:hover { background: var(--ink-3); }

  /* ── Cards ── */
  .kallas-card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 22px;
    box-shadow: var(--shadow-sm);
  }

  /* ── KPI Sparkline bars (HTML reference pattern) ── */
  .kpi-spark {
    position: absolute;
    top: 14px;
    right: 16px;
    display: flex;
    align-items: flex-end;
    gap: 4px;
    height: 48px;
    opacity: .55;
    pointer-events: none;
  }
  .kpi-bar {
    width: 6px;
    border-radius: 4px;
    background: var(--green);
    display: inline-block;
  }
  .kpi-card-feature .kpi-bar { background: rgba(255,255,255,.7); }
  .kpi-card-churn   .kpi-bar { background: var(--rose); }

  /* ── KPI Cards ── */
  .kpi-card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 18px 20px;
    box-shadow: var(--shadow-sm);
    transition: box-shadow .2s, transform .2s;
    height: 100%;
    display: flex;
    align-items: center;
    gap: 16px;
    text-align: left;
    position: relative;
    overflow: hidden;
  }
  .kpi-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
  }
  .kpi-card-feature {
    background: linear-gradient(135deg, #1e3fa8 0%, #0d1f6e 100%);
    border: none;
    border-radius: var(--radius);
    padding: 18px 20px;
    box-shadow: var(--shadow-md);
    position: relative;
    overflow: hidden;
    transition: box-shadow .2s, transform .2s;
    display: flex;
    align-items: center;
    gap: 16px;
    text-align: left;
  }
  .kpi-card-feature:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
  }
  .kpi-card-churn {
    background: var(--surface);
    border: 1px solid #fecaca;
    border-radius: var(--radius);
    padding: 18px 20px;
    box-shadow: var(--shadow-sm);
    transition: box-shadow .2s, transform .2s;
    display: flex;
    align-items: center;
    gap: 16px;
    text-align: left;
    position: relative;
    overflow: hidden;
  }
  .kpi-card-churn:hover {
    box-shadow: 0 10px 28px rgba(212,84,74,.12);
    transform: translateY(-2px);
  }

  /* ── KPI Text wrapper ── */
  .kpi-text { flex: 1; min-width: 0; }

  /* ── KPI Icon ── */
  .kpi-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    min-width: 44px;
    background: var(--green-soft);
    border-radius: 50%;
    color: var(--green);
    flex-shrink: 0;
  }
  .kpi-card-feature .kpi-icon {
    background: rgba(255,255,255,.15);
    color: rgba(255,255,255,.9);
  }
  .kpi-card-churn .kpi-icon {
    background: #fee2e2;
    color: var(--rose);
  }

  /* ── KPI Typography (bold heavy sans-serif, HTML reference style) ── */
  .kpi-label {
    font-size: 10px;
    font-weight: 700;
    color: var(--ink-3);
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-bottom: 4px;
  }
  .kpi-label-light {
    font-size: 10px;
    font-weight: 700;
    color: rgba(255,255,255,.55);
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-bottom: 4px;
  }
  .kpi-value {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -.03em;
    line-height: 1.1;
    color: var(--green-deep);
    margin: 0 0 4px;
  }
  .kpi-value-light {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -.03em;
    line-height: 1.1;
    color: #ffffff;
    margin: 0 0 4px;
  }
  .kpi-up    { font-size: 11px; color: #16a34a; font-weight: 700; }
  .kpi-down  { font-size: 11px; color: #ef4444; font-weight: 700; }
  .kpi-churn { font-size: 11px; color: var(--rose); font-weight: 700; }
  .kpi-sub   { font-size: 10.5px; color: var(--ink-3); margin-top: 1px; }

  /* ── Section Titles ── */
  .section-title {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 11.5px;
    font-weight: 700;
    color: var(--green-deep);
    letter-spacing: .08em;
    border-left: 3px solid var(--green);
    padding-left: 10px;
    margin-bottom: 16px;
    text-transform: uppercase;
  }
  .section-title-red {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 11.5px;
    font-weight: 700;
    color: #b91c1c;
    letter-spacing: .08em;
    border-left: 3px solid var(--rose);
    padding-left: 10px;
    margin-bottom: 16px;
    text-transform: uppercase;
  }

  /* ── Page Header ── */
  .page-title {
    font-family: 'Instrument Serif', serif;
    font-size: 42px;
    font-weight: 400;
    letter-spacing: -.02em;
    color: var(--ink);
    margin: 0 0 4px;
    line-height: 1.1;
  }
  .page-title em { font-style: italic; color: var(--green); }
  .page-sub { color: var(--ink-2); font-size: 14px; margin: 0; }
  .page-ts  {
    font-size: 11.5px;
    color: var(--ink-3);
    text-align: right;
    padding-top: 22px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 6px;
  }
  .page-ts::before {
    content: '';
    display: inline-block;
    width: 7px; height: 7px;
    background: var(--green);
    border-radius: 50%;
  }

  /* ── Filter Bar ── */
  .filter-bar {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius-sm);
    padding: 14px 20px;
    margin-bottom: 20px;
    box-shadow: var(--shadow-sm);
  }

  /* ── Streamlit widget overrides ── */
  div[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border-color: var(--line) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    background: var(--surface) !important;
  }
  div[data-baseweb="select"] > div:focus-within {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 2px rgba(58,125,82,.15) !important;
  }
  .stDateInput input, .stTextInput input {
    border-radius: 10px !important;
    border-color: var(--line) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
  }
  .stButton > button {
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border-color: var(--line-2) !important;
    color: var(--ink) !important;
    background: var(--surface) !important;
    padding: 9px 16px !important;
    transition: border-color .15s, box-shadow .15s, background .15s !important;
  }
  .stButton > button:hover {
    border-color: var(--green) !important;
    color: var(--green-deep) !important;
    box-shadow: 0 0 0 2px rgba(58,125,82,.12) !important;
  }
  .stButton > button[kind="primary"] {
    background: var(--green) !important;
    color: #fff !important;
    border-color: transparent !important;
  }
  .stButton > button[kind="primary"]:hover {
    background: var(--green-deep) !important;
    box-shadow: var(--shadow-md) !important;
  }

  /* Dataframe */
  .stDataFrame { border-radius: var(--radius-sm) !important; overflow: hidden; border: 1px solid var(--line) !important; }
  .stDataFrame thead th {
    background: var(--surface-2) !important;
    color: var(--ink-3) !important;
    font-size: 10.5px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: .08em !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
  }

  /* ── Logo area (PNG branco sobre fundo escuro) ── */
  [data-testid="stLogo"],
  [data-testid="stLogoLink"] {
    background: linear-gradient(180deg, #1e3fa8 0%, #162f8a 100%) !important;
    padding: 24px 22px 20px !important;
    display: flex !important;
    align-items: center !important;
  }
  [data-testid="stLogo"] img,
  [data-testid="stLogoLink"] img {
    max-height: 100px !important;
    width: auto !important;
    object-fit: contain !important;
  }

  /* ── EXA Blue Sidebar ── */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e3fa8 0%, #0d1f6e 100%) !important;
    border-right: none !important;
    box-shadow: 4px 0 32px rgba(11,31,110,.22) !important;
    width: 240px !important;
    min-width: 240px !important;
  }
  [data-testid="stSidebar"] > div:first-child {
    width: 240px !important;
    min-width: 240px !important;
  }
  [data-testid="stSidebarContent"] {
    background: transparent !important;
  }

  /* Sidebar text */
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] small,
  [data-testid="stSidebar"] .stMarkdown p,
  [data-testid="stSidebar"] div[data-testid="stCaptionContainer"] > p,
  [data-testid="stSidebar"] .stCaption {
    color: rgba(255,255,255,.65) !important;
  }
  [data-testid="stSidebar"] h1,
  [data-testid="stSidebar"] h2,
  [data-testid="stSidebar"] h3,
  [data-testid="stSidebar"] .stSubheader {
    color: rgba(255,255,255,.9) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
  }
  [data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,.12) !important;
  }

  /* Sidebar nav links */
  [data-testid="stSidebarNavLink"] {
    border-radius: 12px !important;
    color: rgba(255,255,255,.7) !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
    padding: 10px 14px !important;
    transition: background .15s, color .15s !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
  }
  [data-testid="stSidebarNavLink"]:hover {
    background: rgba(255,255,255,.1) !important;
    color: #fff !important;
  }
  [data-testid="stSidebarNavLink"][aria-current="page"] {
    background: rgba(255,255,255,.16) !important;
    color: #fff !important;
    font-weight: 700 !important;
  }
  [data-testid="stSidebarNavLink"] span,
  [data-testid="stSidebarNavLink"] p {
    color: inherit !important;
  }
  /* Ícone do nav link (emoji/imagem) — monocromático branco */
  [data-testid="stSidebarNavLinkIcon"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 28px !important;
    height: 28px !important;
    min-width: 28px !important;
    background: rgba(255,255,255,.12) !important;
    border-radius: 8px !important;
    font-size: 15px !important;
    flex-shrink: 0 !important;
    filter: grayscale(1) brightness(5) !important;
  }
  [data-testid="stSidebarNavLink"][aria-current="page"] [data-testid="stSidebarNavLinkIcon"] {
    background: rgba(255,255,255,.22) !important;
    filter: grayscale(1) brightness(6) !important;
  }
  [data-testid="stSidebarNavLink"] img {
    width: 18px !important;
    height: 18px !important;
    object-fit: contain !important;
    filter: grayscale(1) brightness(5) !important;
  }

  /* Sidebar buttons */
  [data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,.08) !important;
    color: rgba(255,255,255,.88) !important;
    border-color: rgba(255,255,255,.18) !important;
    width: 100%;
  }
  [data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,.15) !important;
    border-color: rgba(255,255,255,.32) !important;
    color: #fff !important;
    box-shadow: none !important;
  }

  /* Sidebar expander */
  [data-testid="stSidebar"] details {
    border-color: rgba(255,255,255,.14) !important;
    background: rgba(255,255,255,.05) !important;
    border-radius: 10px !important;
  }
  [data-testid="stSidebar"] .streamlit-expanderHeader,
  [data-testid="stSidebar"] details summary {
    color: rgba(255,255,255,.8) !important;
  }
  [data-testid="stSidebar"] details[open] summary {
    border-bottom: 1px solid rgba(255,255,255,.1) !important;
  }

  /* Sidebar select/input */
  [data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: rgba(255,255,255,.08) !important;
    border-color: rgba(255,255,255,.18) !important;
    color: rgba(255,255,255,.88) !important;
  }
  [data-testid="stSidebar"] div[data-baseweb="select"] svg {
    fill: rgba(255,255,255,.6) !important;
  }

  /* ── EXA Table (custom HTML table — matches reference dashboard) ── */
  .exa-table-wrap {
    width: 100%;
    overflow-x: auto;
    border-radius: var(--radius);
    border: 1px solid var(--line);
    box-shadow: var(--shadow-sm);
    background: var(--surface);
  }
  .exa-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 13px;
    color: var(--ink);
  }
  .exa-table thead tr {
    background: var(--green-deep);
  }
  .exa-table thead th {
    color: #ffffff;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .09em;
    padding: 13px 18px;
    text-align: left;
    white-space: nowrap;
    border: none;
  }
  .exa-table thead th.et-num { text-align: right; }
  .exa-table tbody tr {
    border-bottom: 1px solid var(--line);
    transition: background .12s;
  }
  .exa-table tbody tr:last-child { border-bottom: none; }
  .exa-table tbody tr:hover { background: var(--surface-2); }
  .exa-table tbody td {
    padding: 10px 18px;
    color: var(--ink);
    vertical-align: middle;
  }
  .exa-table tbody td.et-num {
    text-align: right;
    font-variant-numeric: tabular-nums;
    color: var(--ink-2);
    font-weight: 500;
  }
  .exa-table tbody td.et-first { font-weight: 600; color: var(--ink); }

  /* Cohort table */
  .cohort-table { width: 100%; border-collapse: collapse; font-size: 12.5px; font-family: 'Plus Jakarta Sans', sans-serif; }
  .cohort-table th {
    background: var(--green-deep);
    color: #ffffff;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: .08em;
    text-align: center;
    padding: 12px 6px;
    border-bottom: none;
    text-transform: uppercase;
  }
  .cohort-table th:first-child { text-align: left; padding-left: 18px; }
  .cohort-table td { padding: 8px 5px; text-align: center; border-bottom: 1px solid var(--line); }
  .cohort-table td:first-child { text-align: left; padding-left: 18px; font-weight: 600; color: var(--ink); }
  .cell-100 { background: var(--green-deep); color: white;  font-weight: 700; border-radius: 8px; padding: 4px 10px; display: inline-block; width: 88%; }
  .cell-85  { background: var(--green);      color: white;  font-weight: 600; border-radius: 8px; padding: 4px 10px; display: inline-block; width: 88%; }
  .cell-45  { background: #93C5FD; color: #1D3186; border-radius: 8px; padding: 4px 10px; display: inline-block; width: 88%; }
  .cell-30  { background: #BFDBFE; color: #1D3186; border-radius: 8px; padding: 4px 10px; display: inline-block; width: 88%; }
  .cell-15  { background: #DBEAFE; color: var(--ink-2); border-radius: 8px; padding: 4px 10px; display: inline-block; width: 88%; }
  .cell-low { background: var(--surface-2); color: var(--ink-3); border-radius: 8px; padding: 4px 10px; display: inline-block; width: 88%; }
  .cell-null { color: var(--line-2); }

  /* ── Chart card wrappers ── */
  [data-testid="stPlotlyChart"],
  [data-testid="stArrowVegaLiteChart"],
  div.stPlotlyChart,
  div[class*="stPlotlyChart"] {
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: var(--radius) !important;
    padding: 12px 4px 4px !important;
    box-shadow: var(--shadow-sm) !important;
    overflow: visible !important;
  }
  [data-testid="stPlotlyChart"] > div,
  div[class*="stPlotlyChart"] > div {
    overflow: visible !important;
  }

  /* Spinner */
  .stSpinner > div { border-color: var(--green) transparent transparent !important; }

  /* Separator */
  hr { border-color: var(--line) !important; }

  /* Alerts */
  .stAlert { border-radius: var(--radius-sm) !important; }
</style>
"""


def inject_theme():
    import streamlit as st
    st.markdown(KALLAS_CSS, unsafe_allow_html=True)
    # EXA logo acima da navegação do sidebar (st.logo aparece em todas as páginas)
    try:
        st.logo(_load_logo_b64(), size="large")
    except Exception:
        pass


def render_table(df) -> str:
    """Renders a DataFrame as a styled HTML table matching the EXA dashboard reference."""
    import pandas as _pd
    numeric_cols = set(df.select_dtypes(include="number").columns)

    headers = "".join(
        f'<th class="et-num">{col}</th>' if col in numeric_cols else f"<th>{col}</th>"
        for col in df.columns
    )
    rows_html = ""
    for i, (_, row) in enumerate(df.iterrows()):
        cells = ""
        for j, (col, val) in enumerate(row.items()):
            if _pd.isna(val):
                display = "—"
            elif col in numeric_cols:
                display = f"{val:,.0f}" if isinstance(val, (int, float)) and val == int(val) else str(val)
            else:
                display = str(val)
            cls = "et-num" if col in numeric_cols else ("et-first" if j == 0 else "")
            cells += f'<td class="{cls}">{display}</td>'
        rows_html += f"<tr>{cells}</tr>"

    return (
        '<div class="exa-table-wrap">'
        '<table class="exa-table">'
        f"<thead><tr>{headers}</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        "</table></div>"
    )


def page_header(title: str, subtitle: str, italic_word: str = ""):
    import streamlit as st
    from datetime import datetime
    col_t, col_ts = st.columns([5, 1])
    with col_t:
        display = title.replace(italic_word, f"<em>{italic_word}</em>") if italic_word else title
        st.markdown(f'<h1 class="page-title">{display}</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="page-sub">{subtitle}</p>', unsafe_allow_html=True)
    with col_ts:
        st.markdown(
            f'<div class="page-ts">Atualizado {datetime.now().strftime("%d/%m/%Y — %H:%M")}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("<br>", unsafe_allow_html=True)
