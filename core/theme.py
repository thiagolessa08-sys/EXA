KALLAS_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
  :root {
    --bg:          #f7f6f2;
    --surface:     #ffffff;
    --surface-2:   #f0f0ec;
    --ink:         #1a2420;
    --ink-2:       #596460;
    --ink-3:       #8a9490;
    --line:        #e2e8e4;
    --line-2:      #d4ddd8;
    --green:       #3a7d52;
    --green-deep:  #1e4030;
    --green-ink:   #162b20;
    --green-soft:  #e8f5ee;
    --green-mid:   #6aad85;
    --amber:       #d4982a;
    --rose:        #d4544a;
    --radius:      22px;
    --radius-sm:   14px;
    --shadow-sm:   0 1px 3px rgba(0,0,0,.07);
    --shadow-md:   0 4px 16px rgba(0,0,0,.08);
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

  /* ── Cards ── */
  .kallas-card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 22px;
    box-shadow: var(--shadow-sm);
  }

  /* ── KPI Cards ── */
  .kpi-card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 20px 22px;
    text-align: center;
    box-shadow: var(--shadow-sm);
    transition: box-shadow .15s;
    height: 100%;
  }
  .kpi-card:hover { box-shadow: var(--shadow-md); }
  .kpi-card-feature {
    background: var(--green-deep);
    border: none;
    border-radius: var(--radius);
    padding: 20px 22px;
    text-align: center;
    box-shadow: var(--shadow-md);
    position: relative; overflow: hidden;
  }
  .kpi-card-churn {
    background: var(--surface);
    border: 1px solid #fecaca;
    border-radius: var(--radius);
    padding: 20px 22px;
    text-align: center;
    box-shadow: var(--shadow-sm);
  }

  .kpi-label {
    font-size: 11px; font-weight: 700;
    color: var(--ink-3);
    letter-spacing: .12em; text-transform: uppercase;
    margin-bottom: 10px;
  }
  .kpi-label-light {
    font-size: 11px; font-weight: 700;
    color: rgba(255,255,255,.65);
    letter-spacing: .12em; text-transform: uppercase;
    margin-bottom: 10px;
  }
  .kpi-value {
    font-family: 'Instrument Serif', serif;
    font-size: 42px; font-weight: 400;
    letter-spacing: -.02em; line-height: 1;
    color: var(--ink);
    margin: 4px 0 8px;
  }
  .kpi-value-light {
    font-family: 'Instrument Serif', serif;
    font-size: 42px; font-weight: 400;
    letter-spacing: -.02em; line-height: 1;
    color: #ffffff;
    margin: 4px 0 8px;
  }
  .kpi-up   { font-size: 12px; color: #16a34a; font-weight: 600; }
  .kpi-down { font-size: 12px; color: #ef4444; font-weight: 600; }
  .kpi-sub  { font-size: 11.5px; color: var(--ink-3); margin-top: 2px; }
  .kpi-churn { font-size: 12px; color: #ef4444; font-weight: 600; }

  /* ── Section titles ── */
  .section-title {
    font-size: 13px; font-weight: 700;
    color: var(--green-deep);
    letter-spacing: .04em;
    border-left: 3px solid var(--green);
    padding-left: 10px;
    margin-bottom: 14px;
    text-transform: uppercase;
  }
  .section-title-red {
    font-size: 13px; font-weight: 700;
    color: #b91c1c;
    letter-spacing: .04em;
    border-left: 3px solid #ef4444;
    padding-left: 10px;
    margin-bottom: 14px;
    text-transform: uppercase;
  }

  /* ── Page header ── */
  .page-title {
    font-family: 'Instrument Serif', serif;
    font-size: 42px; font-weight: 400;
    letter-spacing: -.02em;
    color: var(--ink); margin: 0 0 4px;
  }
  .page-title em { font-style: italic; color: var(--green); }
  .page-sub { color: var(--ink-2); font-size: 14px; margin: 0; }
  .page-ts  { font-size: 12px; color: var(--ink-3); text-align: right; padding-top: 22px; }

  /* ── Filter bar ── */
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
    font-size: 13.5px !important;
    border-color: var(--line-2) !important;
    color: var(--ink) !important;
    background: var(--surface) !important;
    padding: 9px 16px !important;
    transition: border-color .15s, box-shadow .15s !important;
  }
  .stButton > button:hover {
    border-color: var(--ink-3) !important;
    box-shadow: var(--shadow-sm) !important;
  }
  /* Primary button */
  .stButton > button[kind="primary"] {
    background: var(--green) !important;
    color: #fff !important;
    border-color: transparent !important;
  }

  /* Dataframe */
  .stDataFrame { border-radius: var(--radius-sm) !important; overflow: hidden; }
  .stDataFrame thead th {
    background: var(--surface-2) !important;
    color: var(--ink-3) !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: .08em !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--line) !important;
  }
  [data-testid="stSidebar"] .stMarkdown h2 {
    font-family: 'Instrument Serif', serif !important;
    color: var(--ink) !important;
  }

  /* Cohort table */
  .cohort-table { width: 100%; border-collapse: collapse; font-size: 13px; font-family: 'Plus Jakarta Sans', sans-serif; }
  .cohort-table th {
    background: var(--surface-2); color: var(--ink-3);
    font-size: 11px; font-weight: 700; letter-spacing: .08em;
    text-align: center; padding: 9px 5px;
    border-bottom: 2px solid var(--line); text-transform: uppercase;
  }
  .cohort-table th:first-child { text-align: left; padding-left: 14px; }
  .cohort-table td { padding: 6px 5px; text-align: center; border-bottom: 1px solid #f4f6f5; }
  .cohort-table td:first-child { text-align: left; padding-left: 14px; font-weight: 600; color: var(--ink); }
  .cell-100 { background: var(--green-deep); color: white;  font-weight: 700; border-radius: 8px; padding: 4px 10px; display: inline-block; width: 88%; }
  .cell-85  { background: var(--green);      color: white;  font-weight: 600; border-radius: 8px; padding: 4px 10px; display: inline-block; width: 88%; }
  .cell-45  { background: #a7d4b8; color: var(--green-ink); border-radius: 8px; padding: 4px 10px; display: inline-block; width: 88%; }
  .cell-30  { background: #c8e8d4; color: var(--green-ink); border-radius: 8px; padding: 4px 10px; display: inline-block; width: 88%; }
  .cell-15  { background: #dff0e6; color: var(--ink-2);     border-radius: 8px; padding: 4px 10px; display: inline-block; width: 88%; }
  .cell-low { background: var(--surface-2); color: var(--ink-3); border-radius: 8px; padding: 4px 10px; display: inline-block; width: 88%; }
  .cell-null { color: var(--line-2); }

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
            f'<div class="page-ts">● Atualizado {datetime.now().strftime("%d/%m/%Y — %H:%M")}</div>',
            unsafe_allow_html=True
        )
    st.markdown("<br>", unsafe_allow_html=True)
