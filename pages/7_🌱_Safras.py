import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, timedelta, date

from core.theme import inject_theme
from core.template_loader import load_template

inject_theme()

# ── Fonte de dados: Google Sheet publicado (CSV) ──────────────────────────────
SHEET_ID = "122gfwijcQ8f5iNK5aoDwGX3SQugHTiSIj9mo1AQHcOA"
SHEET_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"


# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_int(n) -> str:
    return f"{int(n or 0):,}".replace(",", ".")

def fmt_pct(n, d=1) -> str:
    return f"{float(n or 0):.{d}f}".replace(".", ",")

def fmt_brl(n) -> str:
    v = float(n or 0)
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"

def safe_div(a, b):
    return (a / b * 100) if b else 0.0

def parse_ticket(v):
    """ticket_medio_ftd vem como '27.000.000' (6 casas decimais com '.' de milhar)
    -> valor real = digitos / 1_000_000 = R$ 27,00."""
    s = str(v).strip()
    if s in ("", "nan", "None"):
        return 0.0
    if s.count(".") >= 2:
        try:
            return int(s.replace(".", "")) / 1_000_000
        except ValueError:
            return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


_EMBED_OVERRIDES = """
<style id="exa-streamlit-embed">
  html, body { min-height: 0 !important; height: auto !important; background: transparent !important; }
  .app { grid-template-columns: 1fr !important; min-height: 0 !important; height: auto !important; }
  .sidebar { display: none !important; }
  .topbar { display: none !important; }
  .page { padding-top: 12px !important; padding-bottom: 12px !important; min-height: 0 !important; }
</style>
</head>"""


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("**Filtros**")

    janela = st.selectbox(
        "Janela de cadastro",
        ["Últimos 30 dias", "Últimos 60 dias", "Últimos 90 dias", "Tudo"],
        index=1,
        key="safra_janela",
    )
    if st.button("🔄 Recarregar planilha", key="safra_reload"):
        st.cache_data.clear()


# ── Carga da planilha ─────────────────────────────────────────────────────────
NUM_COLS = ["cadastros", "ftds_total", "d0_qtd", "d0_d1_qtd", "d0_d3_qtd", "d0_d7_qtd",
            "soma_ticket_d0_d7", "cnt_ticket_d0_d7", "std_7d_qtd", "kyc_ftd_qtd"]


@st.cache_data(ttl=300, show_spinner=False)
def load_sheet() -> pd.DataFrame:
    """Le a planilha publicada e reconstroi contagens brutas a partir dos
    percentuais (necessario para reagregar por semana/mes corretamente)."""
    df = pd.read_csv(SHEET_CSV)
    df.columns = [c.strip() for c in df.columns]
    df["dia_safra"] = pd.to_datetime(df["dia_safra"], errors="coerce")
    df = df.dropna(subset=["dia_safra"])

    for c in ["cadastros", "ftds_total", "pct_ftd_d0", "pct_ftd_d0_d1",
              "pct_ftd_d0_d3", "pct_ftd_d0_d7", "pct_std_7d", "pct_kyc_completo_ftd"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["ticket_val"] = df["ticket_medio_ftd"].apply(parse_ticket)

    # Reconstroi contagens (percentual -> quantidade)
    df["d0_qtd"]    = (df["pct_ftd_d0"]    / 100 * df["cadastros"]).round()
    df["d0_d1_qtd"] = (df["pct_ftd_d0_d1"] / 100 * df["cadastros"]).round()
    df["d0_d3_qtd"] = (df["pct_ftd_d0_d3"] / 100 * df["cadastros"]).round()
    df["d0_d7_qtd"] = (df["pct_ftd_d0_d7"] / 100 * df["cadastros"]).round()
    df["std_7d_qtd"]  = (df["pct_std_7d"]           / 100 * df["ftds_total"]).round()
    df["kyc_ftd_qtd"] = (df["pct_kyc_completo_ftd"] / 100 * df["ftds_total"]).round()
    # Para media ponderada do ticket ao reagregar
    df["cnt_ticket_d0_d7"]  = df["d0_d7_qtd"]
    df["soma_ticket_d0_d7"] = df["ticket_val"] * df["d0_d7_qtd"]

    return df[["dia_safra"] + NUM_COLS]


# ── Agregação (dia / semana / mês) ───────────────────────────────────────────
def aggregate(df: pd.DataFrame, granular: str) -> pd.DataFrame:
    if df.empty:
        return df
    d = df.copy()
    if granular == "dia":
        d["periodo_ini"] = d["dia_safra"]
        d["periodo_fim"] = d["dia_safra"]
        d = d.groupby(["periodo_ini", "periodo_fim"], as_index=False)[NUM_COLS].sum()
        d["periodo_lbl"] = d["periodo_ini"].dt.strftime("%d/%m/%y")
    elif granular == "semana":
        d["periodo_ini"] = d["dia_safra"] - pd.to_timedelta(d["dia_safra"].dt.weekday, unit="D")
        g = d.groupby("periodo_ini", as_index=False)[NUM_COLS].sum()
        g["periodo_fim"] = g["periodo_ini"] + pd.Timedelta(days=6)
        g["periodo_lbl"] = g["periodo_ini"].dt.strftime("%d/%m") + "–" + g["periodo_fim"].dt.strftime("%d/%m/%y")
        d = g
    else:  # mes
        d["periodo_ini"] = d["dia_safra"].dt.to_period("M").dt.to_timestamp()
        g = d.groupby("periodo_ini", as_index=False)[NUM_COLS].sum()
        g["periodo_fim"] = g["periodo_ini"] + pd.offsets.MonthEnd(0)
        g["periodo_lbl"] = g["periodo_ini"].dt.strftime("%b/%y")
        d = g

    hoje = pd.Timestamp(date.today())
    d["dias_desde_fim"] = (hoje - d["periodo_fim"]).dt.days
    d["status_maturacao"] = d["dias_desde_fim"].apply(lambda x: "Completa" if x >= 14 else "Em maturação")

    d["pct_d0"]     = d.apply(lambda r: safe_div(r["d0_qtd"],     r["cadastros"]),  axis=1)
    d["pct_d0_d1"]  = d.apply(lambda r: safe_div(r["d0_d1_qtd"],  r["cadastros"]),  axis=1)
    d["pct_d0_d3"]  = d.apply(lambda r: safe_div(r["d0_d3_qtd"],  r["cadastros"]),  axis=1)
    d["pct_d0_d7"]  = d.apply(lambda r: safe_div(r["d0_d7_qtd"],  r["cadastros"]),  axis=1)
    d["pct_std_7d"] = d.apply(lambda r: safe_div(r["std_7d_qtd"], r["ftds_total"]), axis=1)
    d["pct_kyc"]    = d.apply(lambda r: safe_div(r["kyc_ftd_qtd"], r["ftds_total"]), axis=1)
    d["ticket_medio"] = d.apply(lambda r: (r["soma_ticket_d0_d7"] / r["cnt_ticket_d0_d7"]) if r["cnt_ticket_d0_d7"] else 0, axis=1)

    return d.sort_values("periodo_ini", ascending=False)


# ── Payload ───────────────────────────────────────────────────────────────────
def rows_to_payload(d: pd.DataFrame) -> list:
    out = []
    for _, r in d.iterrows():
        out.append({
            "periodo":      r["periodo_lbl"],
            "cadastros":    fmt_int(r["cadastros"]),
            "ftds_total":   fmt_int(r["ftds_total"]),
            "pct_d0":       fmt_pct(r["pct_d0"]),
            "pct_d0_d1":    fmt_pct(r["pct_d0_d1"]),
            "pct_d0_d3":    fmt_pct(r["pct_d0_d3"]),
            "pct_d0_d7":    fmt_pct(r["pct_d0_d7"]),
            "ticket_medio": fmt_brl(r["ticket_medio"]),
            "pct_std_7d":   fmt_pct(r["pct_std_7d"]),
            "pct_kyc":      fmt_pct(r["pct_kyc"]),
            "status":       r["status_maturacao"],
            "status_cor":   "warn" if r["status_maturacao"] == "Em maturação" else "good",
        })
    return out


def build_payload(janela: str) -> dict:
    try:
        df_raw = load_sheet()
    except Exception as e:
        st.error(f"Falha ao ler a planilha: {e}")
        df_raw = pd.DataFrame(columns=["dia_safra"] + NUM_COLS)

    # Filtro de janela
    if not df_raw.empty and janela != "Tudo":
        dias = {"Últimos 30 dias": 30, "Últimos 60 dias": 60, "Últimos 90 dias": 90}[janela]
        corte = pd.Timestamp(date.today() - timedelta(days=dias))
        df_raw = df_raw[df_raw["dia_safra"] >= corte]

    if df_raw.empty:
        dt_ini = dt_fim = date.today()
    else:
        dt_ini = df_raw["dia_safra"].min().date()
        dt_fim = df_raw["dia_safra"].max().date()

    d_dia    = aggregate(df_raw, "dia")
    d_semana = aggregate(df_raw, "semana")
    d_mes    = aggregate(df_raw, "mes")

    tot = {c: int(df_raw[c].sum()) if not df_raw.empty else 0 for c in NUM_COLS}
    pct_d0_7_tot = safe_div(tot["d0_d7_qtd"], tot["cadastros"])
    pct_std_tot  = safe_div(tot["std_7d_qtd"], tot["ftds_total"])
    pct_kyc_tot  = safe_div(tot["kyc_ftd_qtd"], tot["ftds_total"])
    ticket_tot   = (tot["soma_ticket_d0_d7"] / tot["cnt_ticket_d0_d7"]) if tot["cnt_ticket_d0_d7"] else 0

    funil = [
        {"label": "Cadastros",     "qtd": tot["cadastros"], "pct_base": 100.0},
        {"label": "FTD D0",        "qtd": tot["d0_qtd"],    "pct_base": safe_div(tot["d0_qtd"], tot["cadastros"])},
        {"label": "FTD D0–D1",     "qtd": tot["d0_d1_qtd"], "pct_base": safe_div(tot["d0_d1_qtd"], tot["cadastros"])},
        {"label": "FTD D0–D3",     "qtd": tot["d0_d3_qtd"], "pct_base": safe_div(tot["d0_d3_qtd"], tot["cadastros"])},
        {"label": "FTD D0–D7",     "qtd": tot["d0_d7_qtd"], "pct_base": safe_div(tot["d0_d7_qtd"], tot["cadastros"])},
        {"label": "STD em 7 dias", "qtd": tot["std_7d_qtd"], "pct_base": pct_std_tot, "base_alt": "sobre FTDs"},
    ]
    funil_max = max((f["qtd"] for f in funil), default=1) or 1
    for f in funil:
        f["pct_barra"] = round(f["qtd"] / funil_max * 100, 1)
        f["qtd"] = fmt_int(f["qtd"])
        f["pct_base"] = fmt_pct(f["pct_base"])

    return {
        "filters": {
            "periodo":     f"{dt_ini.strftime('%d/%m')}–{dt_fim.strftime('%d/%m/%y')}",
            "data_inicio": dt_ini.strftime("%d/%m/%Y"),
            "data_fim":    dt_fim.strftime("%d/%m/%Y"),
            "atualizado":  datetime.now().strftime("%d/%m/%Y · %H:%M"),
        },
        "header": {
            "eyebrow": "Painel · Onboarding",
            "title":   "Safras",
            "lede":    "Funil diário de conversão por safra de cadastro — FTD (D0 a D7), segundo depósito (STD) em 7 dias e KYC.",
            "base_analise": "Data de Cadastro",
            "comparativo":  "Semana anterior",
        },
        "user": {"name": "Analytics", "role": "EXA", "initials": "EX"},
        "nav": [
            {"key": "onboarding",  "label": "Onboarding",  "icon": "funnel"},
            {"key": "retencao",    "label": "Retenção",    "icon": "retention"},
            {"key": "performance", "label": "Performance", "icon": "perf"},
            {"key": "clusters",    "label": "Clusters",    "icon": "cluster"},
            {"key": "safras",      "label": "Safras",      "icon": "safra", "active": True},
            {"key": "chat",        "label": "Chat",        "icon": "chat"},
        ],
        "resumo": {
            "cadastros":    fmt_int(tot["cadastros"]),
            "pct_d0_d7":    fmt_pct(pct_d0_7_tot) + "%",
            "ticket_medio": fmt_brl(ticket_tot),
            "pct_std_7d":   fmt_pct(pct_std_tot) + "%",
            "pct_kyc":      fmt_pct(pct_kyc_tot) + "%",
        },
        "funil": funil,
        "tabelas": {
            "dia":    rows_to_payload(d_dia),
            "semana": rows_to_payload(d_semana),
            "mes":    rows_to_payload(d_mes),
        },
    }


# ── Render ────────────────────────────────────────────────────────────────────
with st.spinner("Carregando safras..."):
    payload = build_payload(janela)

template = load_template("dashboard_safras.html")
html = template.replace("__EXA_DATA_JSON__", json.dumps(payload, ensure_ascii=False))
html = html.replace("</head>", _EMBED_OVERRIDES)
components.html(html, height=1500, scrolling=False)
