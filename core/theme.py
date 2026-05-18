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


def _spark_svg(points: list, color: str = "#2540ea", width: int = 96, height: int = 22) -> str:
    """Mini SVG sparkline alinhado ao template."""
    if not points or len(points) < 2:
        return ""
    pts = [float(p) for p in points]
    pmin, pmax = min(pts), max(pts)
    rng = pmax - pmin if pmax != pmin else 1.0
    step = width / (len(pts) - 1)
    coords = []
    for i, p in enumerate(pts):
        x = i * step
        y = height - ((p - pmin) / rng) * (height - 2) - 1
        coords.append(f"{x:.1f},{y:.1f}")
    polyline = " ".join(coords)
    return (
        f'<svg class="spark" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg" fill="none" stroke="{color}" '
        f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
        f'<polyline points="{polyline}" /></svg>'
    )


def kpi_group(cards: list, churn: bool = False) -> str:
    """
    Renderiza vários KPI cards num único grid (estilo template Onboarding).
    Cada card: {label, value, unit?, sub?, delta?:{dir,v}, spark?:list, churn?:bool}
    """
    cols_cls = f"cols-{len(cards)}" if len(cards) in (4, 6) else "cols-6"
    items = []
    for c in cards:
        is_churn = churn or c.get("churn", False)
        cls = "exa-kpi churn" if is_churn else "exa-kpi"
        unit_html = f'<span class="unit">{c.get("unit","")}</span>' if c.get("unit") else ""
        delta = c.get("delta") or {}
        dir_ = (delta.get("dir") or "flat").lower()
        dv = delta.get("v") or ""
        delta_html = ""
        if dv:
            arrow = {"up": "↑", "down": "↓", "flat": "→"}.get(dir_, "→")
            delta_html = f'<span class="delta {dir_}">{arrow} {dv}</span>'
        spark = c.get("spark") or []
        spark_color = "#d62a39" if is_churn else "#2540ea"
        spark_html = _spark_svg(spark, color=spark_color) if spark else ""
        sub_html = f'<div class="sub">{c.get("sub","")}</div>' if c.get("sub") else ""
        items.append(
            f'<div class="{cls}">'
            f'<div class="label"><span>{c["label"]}</span>'
            f'<span class="help" title="{c.get("help","")}">ⓘ</span></div>'
            f'<div class="value">{c["value"]}{unit_html}</div>'
            f'<div class="foot">{spark_html}{delta_html}</div>'
            f'{sub_html}'
            f'</div>'
        )
    return f'<div class="exa-kpi-grid {cols_cls}">{"".join(items)}</div>'


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
<link href="https://cdn.jsdelivr.net/npm/geist@1.3.1/dist/fonts/geist-sans/style.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/geist@1.3.1/dist/fonts/geist-mono/style.css" rel="stylesheet">

<style>
  :root {
    /* Paleta alinhada ao template (paper / ink neutros) */
    --bg:          #fbfaf7;
    --paper:       #fbfaf7;
    --paper-2:     #f5f3ee;
    --surface:     #ffffff;
    --surface-2:   #f5f3ee;
    --card:        #ffffff;
    --ink:         #0a0d14;
    --ink-900:     #0a0d14;
    --ink-800:     #14171f;
    --ink-700:     #1f242e;
    --ink-2:       #2c3340;
    --ink-3:       #4a5160;
    --ink-400:     #6b7280;
    --ink-300:     #8a93a3;
    --ink-200:     #b9bfc9;
    --ink-100:     #dde1e8;
    --hair:        #eef0f4;
    --line:        #eef0f4;
    --line-2:      #dde1e8;
    --blue:        #2540ea;
    --blue-deep:   #1d36c9;
    --blue-soft:   #eef1ff;
    --blue-mid:    #60A5FA;
    --good-500:    #1f9d57;
    --bad-600:     #d62a39;
    /* Fontes alinhadas ao template */
    --font-sans:   "Geist", -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
    --font-mono:   "Geist Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
    --font-serif:  "Instrument Serif", "Times New Roman", serif;
    /* aliases para compatibilidade */
    --green:       #2563EB;
    --green-deep:  #1D3186;
    --green-ink:   #0B1629;
    --green-soft:  #EBF1FF;
    --green-mid:   #60A5FA;
    --amber:       #F59E0B;
    --rose:        #EF4444;
    --emerald:     #10B981;
    --radius:      20px;
    --radius-sm:   12px;
    --shadow-sm:   0 1px 3px rgba(11,23,64,.05), 0 6px 20px rgba(37,99,235,.08);
    --shadow-md:   0 3px 10px rgba(11,23,64,.07), 0 18px 40px rgba(37,99,235,.11);
    --shadow-lg:   0 8px 24px rgba(11,23,64,.09), 0 32px 64px rgba(37,99,235,.15);
    --sidebar-w:   248px;
  }

  html, body, [class*="css"] {
    font-family: var(--font-sans) !important;
    background: var(--paper) !important;
    color: var(--ink-900) !important;
    -webkit-font-smoothing: antialiased;
  }
  .stApp {
    background: var(--paper) !important;
  }

  /* ── Remove Streamlit chrome (header, toolbar, decoration) ── */
  #MainMenu, footer, header { visibility: hidden !important; display: none !important; }
  [data-testid="stHeader"],
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"],
  [data-testid="manage-app-button"],
  div[class*="StatusWidget"],
  .stApp > header { display: none !important; height: 0 !important; overflow: hidden !important; }

  /* ── BARRA BRANCA: zerar o padding-top que o Streamlit injeta para compensar o header ── */
  section[data-testid="stMain"]                         { padding-top: 0 !important; margin-top: 0 !important; }
  section[data-testid="stMain"] > div:first-child       { padding-top: 0 !important; margin-top: 0 !important; }
  .stMainBlockContainer                                  { padding-top: 0 !important; margin-top: 0 !important; }
  [data-testid="stAppViewBlockContainer"]                { padding-top: 0 !important; }
  /* Override inline style="padding-top:Npx" injetado pelo Streamlit */
  .stMainBlockContainer[style]                           { padding-top: 0 !important; }

  /* ── MARGENS: conteúdo colado nas bordas do conteiner ── */
  .block-container {
    padding: 0.5rem 1.25rem 2rem !important;
    max-width: 100% !important;
    margin: 0 !important;
  }

  /* ── Esconder labels de seção do sidebar nav ("app", "chat", etc) ── */
  [data-testid="stSidebarNavSectionHeader"],
  .stSidebarNavSectionHeader,
  [data-testid="stSidebarNavSeparator"],
  [data-testid="stSidebarNav"] > div:first-child:not(:has(a)),
  [data-testid="stSidebarNav"] > ul:first-child > li:first-child:not(:has(a)),
  [data-testid="stSidebarNav"] h1,
  [data-testid="stSidebarNav"] h2,
  [data-testid="stSidebarNav"] h3,
  [data-testid="stSidebarNav"] > div > p,
  [data-testid="stSidebarNav"] > p,
  /* div que contém <p> mas não contém links (= section header) */
  [data-testid="stSidebar"] nav div:has(> p):not(:has(a)),
  [data-testid="stSidebar"] nav > div > div > p,
  [data-testid="stSidebar"] nav > * > div > p,
  [data-testid="stSidebar"] nav > p,
  [data-testid="stSidebar"] nav > div > p,
  [data-testid="stSidebar"] nav p:not([data-testid="stSidebarNavLinkLabel"]):not([class*="NavLink"]) {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    opacity: 0 !important;
    visibility: hidden !important;
    pointer-events: none !important;
  }
  /* Esconder link de nav que aponta para /app (entry script) */
  [data-testid="stSidebarNav"] a[href$="/app"],
  [data-testid="stSidebarNav"] a[href$="/app/"],
  [data-testid="stSidebarNav"] a[href*="/app?"],
  [data-testid="stSidebarNav"] li:has(a[href$="/app"]),
  [data-testid="stSidebarNav"] li:has(a[href$="/app/"]) {
    display: none !important;
    height: 0 !important;
    overflow: hidden !important;
    visibility: hidden !important;
  }

  /* Restaura visibilidade do label do link em si */
  [data-testid="stSidebarNavLink"] span,
  [data-testid="stSidebarNavLink"] p {
    display: inline-block !important;
    height: auto !important;
    min-height: 0 !important;
    max-height: none !important;
    opacity: 1 !important;
    visibility: visible !important;
    pointer-events: auto !important;
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
    padding: 24px;
    box-shadow: var(--shadow-sm);
    transition: box-shadow .2s, transform .2s;
  }
  .kallas-card:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }

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
    border-left: 3px solid var(--blue) !important;
    border-radius: var(--radius);
    padding: 18px 20px;
    box-shadow: var(--shadow-sm);
    transition: box-shadow .25s, transform .25s;
    height: 100%;
    display: flex;
    align-items: center;
    gap: 16px;
    text-align: left;
    position: relative;
    overflow: hidden;
  }
  .kpi-card:hover { box-shadow: var(--shadow-md); transform: translateY(-3px); }

  .kpi-card-feature {
    background: linear-gradient(135deg, #1e3fa8 0%, #0b1a6b 100%);
    border: none;
    border-radius: var(--radius);
    padding: 18px 20px;
    box-shadow: var(--shadow-md);
    position: relative;
    overflow: hidden;
    transition: box-shadow .25s, transform .25s;
    display: flex;
    align-items: center;
    gap: 16px;
    text-align: left;
  }
  .kpi-card-feature::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 120px; height: 120px;
    background: rgba(255,255,255,.06);
    border-radius: 50%;
  }
  .kpi-card-feature:hover { box-shadow: var(--shadow-lg); transform: translateY(-3px); }

  .kpi-card-churn {
    background: var(--surface);
    border: 1px solid #fecaca;
    border-left: 3px solid var(--rose) !important;
    border-radius: var(--radius);
    padding: 18px 20px;
    box-shadow: var(--shadow-sm);
    transition: box-shadow .25s, transform .25s;
    display: flex;
    align-items: center;
    gap: 16px;
    text-align: left;
    position: relative;
    overflow: hidden;
  }
  .kpi-card-churn:hover { box-shadow: 0 10px 32px rgba(239,68,68,.14); transform: translateY(-3px); }

  /* ── KPI Text wrapper ── */
  .kpi-text { flex: 1; min-width: 0; }

  /* ── KPI Icon ── */
  .kpi-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 46px;
    height: 46px;
    min-width: 46px;
    background: var(--blue-soft);
    border-radius: 14px;
    color: var(--blue);
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(37,99,235,.15);
  }
  .kpi-card-feature .kpi-icon {
    background: rgba(255,255,255,.18);
    color: rgba(255,255,255,.95);
    box-shadow: 0 2px 8px rgba(0,0,0,.15);
  }
  .kpi-card-churn .kpi-icon {
    background: #fee2e2;
    color: var(--rose);
    box-shadow: 0 2px 8px rgba(239,68,68,.15);
  }

  /* ── KPI Typography ── */
  .kpi-label {
    font-size: 9.5px;
    font-weight: 800;
    color: var(--ink-3);
    letter-spacing: .13em;
    text-transform: uppercase;
    margin-bottom: 3px;
  }
  .kpi-label-light {
    font-size: 9.5px;
    font-weight: 800;
    color: rgba(255,255,255,.6);
    letter-spacing: .13em;
    text-transform: uppercase;
    margin-bottom: 3px;
  }
  .kpi-value {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -.04em;
    line-height: 1.05;
    color: var(--blue-deep);
    margin: 0 0 4px;
  }
  .kpi-value-light {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -.04em;
    line-height: 1.05;
    color: #ffffff;
    margin: 0 0 4px;
  }
  .kpi-up    { font-size: 11px; color: #059669; font-weight: 700; }
  .kpi-down  { font-size: 11px; color: #dc2626; font-weight: 700; }
  .kpi-churn { font-size: 11px; color: var(--rose); font-weight: 700; }
  .kpi-sub   { font-size: 10.5px; color: var(--ink-3); margin-top: 2px; line-height: 1.4; }

  /* ── Section Titles ── */
  .section-title {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 10.5px;
    font-weight: 800;
    color: var(--blue-deep);
    letter-spacing: .11em;
    border-left: 3px solid var(--blue);
    padding: 6px 14px 6px 11px;
    background: rgba(37,99,235,.06);
    border-radius: 0 10px 10px 0;
    margin-bottom: 18px;
    text-transform: uppercase;
  }
  .section-title-red {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 10.5px;
    font-weight: 800;
    color: #991b1b;
    letter-spacing: .11em;
    border-left: 3px solid var(--rose);
    padding: 6px 14px 6px 11px;
    background: rgba(239,68,68,.06);
    border-radius: 0 10px 10px 0;
    margin-bottom: 18px;
    text-transform: uppercase;
  }

  /* ── Page Header (template-style: eyebrow + serif italic + lede) ── */
  .page-eyebrow {
    font-family: var(--font-mono);
    font-size: 11px;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: var(--ink-400);
    margin: 0 0 12px;
    font-weight: 500;
  }
  .page-title {
    font-family: var(--font-serif) !important;
    font-style: italic;
    font-size: 56px;
    font-weight: 400;
    letter-spacing: -.02em;
    color: var(--ink-900) !important;
    margin: 0 0 12px;
    line-height: 1;
  }
  .page-title em {
    font-style: italic;
    color: var(--ink-900) !important;
  }
  .page-sub, .page-lede {
    color: var(--ink-500, #4a5160);
    font-size: 15px;
    font-weight: 400;
    margin: 0 0 4px;
    line-height: 1.5;
    max-width: 56ch;
    letter-spacing: -.005em;
    font-family: var(--font-sans);
  }
  .page-ts  {
    font-size: 11px;
    color: var(--ink-3);
    text-align: right;
    padding-top: 26px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 6px;
    font-weight: 500;
  }
  .page-ts::before {
    content: '';
    display: inline-block;
    width: 7px; height: 7px;
    background: var(--emerald);
    border-radius: 50%;
    box-shadow: 0 0 0 3px rgba(16,185,129,.2);
  }

  /* ── Filter Bar (removido — não usado mais; mantido vazio por segurança) ── */
  .filter-bar { display: contents !important; }

  /* ── Streamlit widget overrides ── */
  div[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border-color: var(--line) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    background: var(--surface) !important;
    box-shadow: 0 1px 4px rgba(37,99,235,.06) !important;
  }
  div[data-baseweb="select"] > div:focus-within {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,.12) !important;
  }
  .stDateInput input, .stTextInput input {
    border-radius: 10px !important;
    border-color: var(--line) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    box-shadow: 0 1px 4px rgba(37,99,235,.06) !important;
  }
  .stDateInput input:focus, .stTextInput input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,.12) !important;
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

  /* ── Logo ──
     Em Streamlit 1.35+, data-testid="stLogo" fica no proprio <img>.
     data-testid="stLogoLink" fica no <a> que envolve o <img>.
     Portanto [data-testid="stLogo"] img nao existe — precisamos
     selecionar o <img> diretamente. ── */

  /* O <a> que envolve o logo */
  [data-testid="stLogoLink"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    min-height: 72px !important;
    height: auto !important;
    max-height: none !important;
    padding: 32px 20px 10px !important;
    box-sizing: border-box !important;
    overflow: visible !important;
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
  }

  /* O <img> com data-testid="stLogo" (seletor direto) */
  img[data-testid="stLogo"],
  [data-testid="stLogoLink"] img {
    display: block !important;
    width: 145px !important;
    min-width: 100px !important;
    height: auto !important;
    max-height: none !important;
    min-height: 36px !important;
    object-fit: contain !important;
  }

  /* ── Esconder botão de colapsar sidebar ── */
  [data-testid="stSidebarCollapseButton"],
  [data-testid="collapsedControl"],
  button[data-testid="baseButton-headerNoPadding"],
  [data-testid="stSidebar"] button[kind="header"] {
    display: none !important;
    visibility: hidden !important;
  }

  /* ── EXA Sidebar — sempre visível e fixo ── */
  [data-testid="stSidebar"] {
    background: linear-gradient(160deg, #1a3ba0 0%, #0c1a60 60%, #091550 100%) !important;
    border-right: none !important;
    box-shadow: 6px 0 36px rgba(9,21,80,.30) !important;
    width: var(--sidebar-w) !important;
    min-width: var(--sidebar-w) !important;
    display: block !important;
    visibility: visible !important;
    transform: none !important;
    left: 0 !important;
    position: relative !important;
  }
  [data-testid="stSidebar"][aria-expanded="false"] {
    transform: none !important; margin-left: 0 !important; left: 0 !important; display: block !important;
  }
  [data-testid="stSidebar"] > div:first-child {
    width: var(--sidebar-w) !important;
    min-width: var(--sidebar-w) !important;
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
    border-radius: 10px !important;
    color: rgba(255,255,255,.65) !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
    padding: 10px 14px !important;
    transition: background .18s, color .18s, border-color .18s !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    border-left: 3px solid transparent !important;
    margin-bottom: 2px !important;
  }
  [data-testid="stSidebarNavLink"]:hover {
    background: rgba(255,255,255,.09) !important;
    color: rgba(255,255,255,.9) !important;
    border-left-color: rgba(255,255,255,.3) !important;
  }
  [data-testid="stSidebarNavLink"][aria-current="page"] {
    background: rgba(255,255,255,.14) !important;
    color: #fff !important;
    font-weight: 700 !important;
    border-left-color: #60A5FA !important;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.08) !important;
  }
  [data-testid="stSidebarNavLink"] span,
  [data-testid="stSidebarNavLink"] p { color: inherit !important; }
  /* Ícone do nav link (emoji/imagem) — monocromático branco */
  [data-testid="stSidebarNavLinkIcon"],
  [data-testid="stSidebarNavLinkIcon"] * {
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
    filter: grayscale(1) saturate(0) brightness(10) !important;
    -webkit-filter: grayscale(1) saturate(0) brightness(10) !important;
  }
  [data-testid="stSidebarNavLink"][aria-current="page"] [data-testid="stSidebarNavLinkIcon"],
  [data-testid="stSidebarNavLink"][aria-current="page"] [data-testid="stSidebarNavLinkIcon"] * {
    background: rgba(255,255,255,.22) !important;
    filter: grayscale(1) saturate(0) brightness(12) !important;
    -webkit-filter: grayscale(1) saturate(0) brightness(12) !important;
  }
  [data-testid="stSidebarNavLink"] img {
    width: 18px !important;
    height: 18px !important;
    object-fit: contain !important;
    filter: grayscale(1) saturate(0) brightness(10) !important;
    -webkit-filter: grayscale(1) saturate(0) brightness(10) !important;
  }
  /* Força emoji a renderizar como texto (sem cor do sistema) */
  [data-testid="stSidebarNavLinkIcon"] span,
  [data-testid="stSidebarNavLinkIcon"] p {
    font-style: normal !important;
    color: rgba(255,255,255,.75) !important;
    filter: grayscale(1) saturate(0) brightness(10) !important;
    -webkit-filter: grayscale(1) saturate(0) brightness(10) !important;
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
    border-top: 3px solid var(--blue) !important;
    border-radius: var(--radius) !important;
    padding: 14px 4px 4px !important;
    box-shadow: var(--shadow-sm) !important;
    overflow: visible !important;
    transition: box-shadow .25s !important;
  }
  [data-testid="stPlotlyChart"]:hover,
  div[class*="stPlotlyChart"]:hover {
    box-shadow: var(--shadow-md) !important;
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

  /* ── KPI Grid (template Onboarding) ──────────────────────────────────────── */
  .exa-kpi-grid {
    display: grid;
    gap: 1px;
    background: var(--hair);
    border: 1px solid var(--hair);
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 22px;
  }
  .exa-kpi-grid.cols-6 { grid-template-columns: repeat(auto-fit, minmax(155px, 1fr)); }
  .exa-kpi-grid.cols-4 { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
  .exa-kpi {
    background: var(--card);
    padding: 16px 14px 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    min-height: 132px;
    position: relative;
    min-width: 0;
  }
  .exa-kpi.churn::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--bad-600);
    opacity: .9;
  }
  .exa-kpi .label {
    font-family: var(--font-mono);
    font-size: 10px;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--ink-400);
    display: flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .exa-kpi .label > span:first-child {
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .exa-kpi .label .help {
    color: var(--ink-200);
    cursor: help;
    font-size: 10px;
  }
  .exa-kpi .value {
    font-family: var(--font-sans);
    font-feature-settings: "tnum" 1, "ss01" 1;
    font-size: clamp(22px, 1.9vw, 28px);
    font-weight: 500;
    letter-spacing: -.025em;
    color: var(--ink-900);
    line-height: 1;
    white-space: nowrap;
  }
  .exa-kpi .value .unit {
    font-size: .6em;
    color: var(--ink-400);
    font-weight: 400;
    margin-left: 2px;
  }
  .exa-kpi .foot {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: auto;
    gap: 8px;
    min-height: 22px;
  }
  .exa-kpi .delta {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 500;
    padding: 2px 6px;
    border-radius: 4px;
  }
  .exa-kpi .delta.up   { color: #146c43; background: #e6f4eb; }
  .exa-kpi .delta.down { color: #b3261e; background: #fde7e7; }
  .exa-kpi .delta.flat { color: var(--ink-400); background: var(--ink-100); }
  .exa-kpi .sub {
    font-size: 11.5px;
    color: var(--ink-400);
    letter-spacing: -.005em;
  }
  .exa-kpi .sub b { color: var(--ink-700); font-weight: 500; }
  .exa-kpi .spark { display: block; opacity: .85; }

  /* ── Section header (rule + tag) — estilo template ───────────────────────── */
  .exa-section-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 8px 0 14px;
  }
  .exa-section-head .tag {
    font-family: var(--font-mono);
    font-size: 10.5px;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: var(--ink-3);
  }
  .exa-section-head .tag.churn { color: var(--bad-600); }
  .exa-section-head .rule {
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, var(--line-2), transparent);
  }
  .exa-section-head .rule.churn {
    background: linear-gradient(to right, rgba(214,42,57,.35), transparent);
  }

  /* ── Card genérico (envolve charts/tables) — estilo template ─────────────── */
  .exa-card {
    background: var(--card);
    border: 1px solid var(--hair);
    border-radius: 14px;
    padding: 22px 24px 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    margin-bottom: 22px;
  }
  .exa-card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
  .exa-card-head h3 {
    margin: 0;
    font-family: var(--font-serif);
    font-style: italic;
    font-weight: 400;
    font-size: 22px;
    color: var(--ink-900);
    letter-spacing: -.01em;
  }
  .exa-card-head .sub {
    font-family: var(--font-mono);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: .1em;
    color: var(--ink-400);
    margin-top: 2px;
  }

  /* ── Override dos chart containers Plotly ────────────────────────────────── */
  [data-testid="stPlotlyChart"],
  div.stPlotlyChart,
  div[class*="stPlotlyChart"] {
    background: var(--card) !important;
    border: 1px solid var(--hair) !important;
    border-top: 1px solid var(--hair) !important;
    border-radius: 14px !important;
    padding: 16px 14px 6px !important;
    box-shadow: none !important;
  }

  /* ── Topbar Row (brand strip embutido no container de filtros) ───────────── */
  .exa-topbar-row {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 10px 0 6px;
    position: relative;
    z-index: 1;
  }
  .exa-topbar-pulse {
    width: 8px; height: 8px;
    background: #34d399;
    border-radius: 50%;
    box-shadow: 0 0 0 3px rgba(52,211,153,.25);
    flex-shrink: 0;
    animation: tb-pulse 2.4s ease-in-out infinite;
  }
  @keyframes tb-pulse {
    0%, 100% { box-shadow: 0 0 0 3px rgba(52,211,153,.25); opacity: 1; }
    50%       { box-shadow: 0 0 0 7px rgba(52,211,153,.08); opacity: .85; }
  }
  .exa-topbar-brand {
    color: rgba(255,255,255,.92);
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: .20em;
    text-transform: uppercase;
  }
  .exa-topbar-sep {
    width: 1px; height: 22px;
    background: rgba(255,255,255,.18);
    flex-shrink: 0;
  }
  .exa-topbar-live-badge {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 5px;
    background: rgba(52,211,153,.12);
    border: 1px solid rgba(52,211,153,.30);
    color: #6ee7b7;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .14em;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 20px;
  }
  .exa-topbar-live-badge span {
    display: inline-block;
    width: 6px; height: 6px;
    background: #34d399;
    border-radius: 50%;
  }

  /* ── Container dos filtros vira a faixa azul via :has(.exa-topbar-row) ───── */
  [data-testid="stVerticalBlock"]:has(> div > [data-testid="stMarkdownContainer"] .exa-topbar-row) {
    position: relative;
    width: calc(100% + 2.5rem) !important;
    margin-left: -1.25rem !important;
    margin-right: -1.25rem !important;
    margin-top: -0.5rem !important;
    margin-bottom: 1.5rem !important;
    padding: 0 28px 12px !important;
    background: linear-gradient(105deg, #07123d 0%, #0d1f6e 20%, #1a3ba0 45%, #2563EB 65%, #1a3ba0 82%, #0d1f6e 100%) !important;
    box-shadow: 0 6px 28px rgba(7,18,61,.40), 0 1px 0 rgba(255,255,255,.07) inset !important;
    border-radius: 0 !important;
    overflow: hidden;
    z-index: 10;
  }
  /* dot-grid overlay */
  [data-testid="stVerticalBlock"]:has(> div > [data-testid="stMarkdownContainer"] .exa-topbar-row)::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: radial-gradient(circle, rgba(255,255,255,.10) 1px, transparent 1px);
    background-size: 22px 22px;
    pointer-events: none;
    z-index: 0;
  }
  /* bottom shimmer line */
  [data-testid="stVerticalBlock"]:has(> div > [data-testid="stMarkdownContainer"] .exa-topbar-row)::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg,
      transparent 0%,
      rgba(96,165,250,.6) 20%,
      rgba(147,197,253,.9) 50%,
      rgba(96,165,250,.6) 80%,
      transparent 100%);
    z-index: 1;
  }
  /* Dropdowns no modo escuro */
  [data-testid="stVerticalBlock"]:has(> div > [data-testid="stMarkdownContainer"] .exa-topbar-row) div[data-baseweb="select"] > div {
    background: rgba(255,255,255,.10) !important;
    border-color: rgba(255,255,255,.25) !important;
    color: rgba(255,255,255,.92) !important;
    box-shadow: none !important;
  }
  [data-testid="stVerticalBlock"]:has(> div > [data-testid="stMarkdownContainer"] .exa-topbar-row) div[data-baseweb="select"] > div:focus-within {
    border-color: rgba(255,255,255,.55) !important;
    box-shadow: 0 0 0 2px rgba(255,255,255,.15) !important;
  }
  [data-testid="stVerticalBlock"]:has(> div > [data-testid="stMarkdownContainer"] .exa-topbar-row) div[data-baseweb="select"] svg {
    fill: rgba(255,255,255,.70) !important;
  }
  /* Date input no modo escuro */
  [data-testid="stVerticalBlock"]:has(> div > [data-testid="stMarkdownContainer"] .exa-topbar-row) .stDateInput input {
    background: rgba(255,255,255,.10) !important;
    border-color: rgba(255,255,255,.25) !important;
    color: rgba(255,255,255,.92) !important;
    box-shadow: none !important;
  }
  /* Labels dos widgets (usados nas outras páginas) */
  [data-testid="stVerticalBlock"]:has(> div > [data-testid="stMarkdownContainer"] .exa-topbar-row) label,
  [data-testid="stVerticalBlock"]:has(> div > [data-testid="stMarkdownContainer"] .exa-topbar-row) .stWidgetLabel p {
    color: rgba(255,255,255,.60) !important;
    font-size: 10.5px !important;
    font-weight: 700 !important;
    letter-spacing: .09em !important;
    text-transform: uppercase !important;
  }
  /* Caption / texto genérico */
  [data-testid="stVerticalBlock"]:has(> div > [data-testid="stMarkdownContainer"] .exa-topbar-row) [data-testid="stCaptionContainer"] p,
  [data-testid="stVerticalBlock"]:has(> div > [data-testid="stMarkdownContainer"] .exa-topbar-row) p {
    color: rgba(255,255,255,.80) !important;
  }
</style>
"""


def inject_theme():
    import streamlit as st
    st.markdown(KALLAS_CSS, unsafe_allow_html=True)
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


def page_header(title: str, subtitle: str, italic_word: str = "", eyebrow: str = ""):
    import streamlit as st
    from datetime import datetime
    col_t, col_ts = st.columns([5, 1])
    with col_t:
        if eyebrow:
            st.markdown(f'<div class="page-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
        display = title.replace(italic_word, f"<em>{italic_word}</em>") if italic_word else title
        st.markdown(f'<h1 class="page-title">{display}</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="page-lede">{subtitle}</p>', unsafe_allow_html=True)
    with col_ts:
        st.markdown(
            f'<div class="page-ts">Atualizado {datetime.now().strftime("%d/%m/%Y — %H:%M")}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("<br>", unsafe_allow_html=True)


def section_head(tag: str, churn: bool = False):
    """Renderiza tag + rule horizontal (estilo template)."""
    import streamlit as st
    cls = "tag churn" if churn else "tag"
    rule_cls = "rule churn" if churn else "rule"
    st.markdown(
        f'<div class="exa-section-head"><span class="{cls}">{tag}</span>'
        f'<span class="{rule_cls}"></span></div>',
        unsafe_allow_html=True,
    )


def topbar_strip():
    """Renderiza a faixa azul EXA · Analytics · Live no topo do container de filtros."""
    import streamlit as st
    st.markdown(
        '<div class="exa-topbar-row">'
        '<span class="exa-topbar-pulse"></span>'
        '<span class="exa-topbar-brand">EXA &middot; Analytics</span>'
        '<span class="exa-topbar-sep"></span>'
        '<span class="exa-topbar-live-badge"><span></span>Live</span>'
        '</div>',
        unsafe_allow_html=True,
    )
